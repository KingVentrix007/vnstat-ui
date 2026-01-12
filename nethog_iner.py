import asyncio
from collections import defaultdict

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
    print("I made it yall")
    proc = await asyncio.create_subprocess_exec(
        "sudo", "nethogs", "-t",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    program_totals = defaultdict(lambda: {"sent_kbps": 0.0, "recv_kbps": 0.0, "total_bytes": 0.0})

    try:
        while True:
            # Read lines for a short burst of time
            try:
                while True:
                    # timeout = 0.1 so we don't block forever
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
                    except ValueError:
                        continue
            except asyncio.TimeoutError:
                # no more lines available right now
                pass

            # Yield whatever we have, then sleep
            yield program_totals
            await asyncio.sleep(update_interval)

    except asyncio.CancelledError:
        proc.terminate()
        raise
