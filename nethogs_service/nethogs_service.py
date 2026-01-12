import asyncio
import json
from collections import defaultdict
from db_helper import add_process_data, get_today_data, get_process_history, get_total_usage
import os

SOCKET_PATH = "/tmp/nethogs_service.sock"

def normalize_name(proc_str: str):
    normalized_name = proc_str
    if "/proc/self" in proc_str:
        normalized_name = "Nethog"
    elif "/opt/" in proc_str:
        parts = proc_str.split("/")
        name = parts[3].split(" ")[0]
        normalized_name = name.capitalize()
    elif " " in proc_str:
        first_part = proc_str.split(" ")[0]
        name = first_part.split("/")[-1]
        normalized_name = name.capitalize()
    else:
        name = proc_str.split("/")[-1]
        if name.isdigit():
            for part in reversed(proc_str.split("/")):
                if part.isalpha():
                    normalized_name = part.capitalize()
                    break
        else:
            normalized_name = name.capitalize()
    uuid_code = hash(proc_str)
    return normalized_name, uuid_code


async def nethogs_tracker(update_interval=1):
    proc = await asyncio.create_subprocess_exec(
        "sudo", "nethogs", "-t",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    program_totals = defaultdict(lambda: {"sent_kbps": 0.0, "recv_kbps": 0.0, "total_bytes": 0.0})

    try:
        while True:
            try:
                while True:
                    line_bytes = await asyncio.wait_for(proc.stdout.readline(), timeout=0.1)
                    if not line_bytes:
                        break
                    line = line_bytes.decode().strip()
                    if not line or line.startswith(("Adding", "Ethernet", "Refreshing")):
                        continue
                    try:
                        cmd, sent, recv = line.rsplit("\t", 2)
                        sent = float(sent)
                        recv = float(recv)
                        name, _ = normalize_name(cmd)
                        program_totals[name]["sent_kbps"] += sent
                        program_totals[name]["recv_kbps"] += recv
                        program_totals[name]["total_bytes"] += (sent + recv) * 1024 / 8
                        add_process_data(name, recv, sent)
                    except ValueError:
                        continue
            except asyncio.TimeoutError:
                pass

            yield program_totals
            await asyncio.sleep(update_interval)

    except asyncio.CancelledError:
        proc.terminate()
        raise



async def handle_client(reader, writer):
    try:
        _ = await reader.read(100)  # you could also ignore input entirely

        # Pull today's stats directly from the database
        today_stats = get_today_data()  # returns list of tuples

        # Convert to a dict for JSON
        data_dict = {
            name: {"kbps_down": down, "kbps_up": up, "kbps_total": total, "last_update": last_update}
            for name, down, up, total, last_update in today_stats
        }

        data_bytes = json.dumps(data_dict).encode()
        writer.write(data_bytes)
        await writer.drain()
    except Exception as e:
        print("Error handling client:", e)
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    # Initialize tracker_state to empty dict
    tracker_state = {}

    server = await asyncio.start_unix_server(
        lambda r, w: handle_client(r, w),
        path=SOCKET_PATH
    )

    # Make socket world-readable/writable
    os.chmod(SOCKET_PATH, 0o666)

    print(f"Nethogs service running. Socket: {SOCKET_PATH}")

    async for tracker_state in nethogs_tracker():
        # just updating tracker_state, server handler reads latest
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
