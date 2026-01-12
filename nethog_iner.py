import subprocess
from collections import defaultdict
import asyncio

async def nethogs_tracker(update_interval=1):
    """
    Async nethogs tracker generator.
    Yields per-program totals every `update_interval` seconds.
    """
    # Start nethogs in text mode
    proc = subprocess.Popen(
        ["sudo", "nethogs", "-t"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

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

    # Dictionaries for tracking
    programs = defaultdict(lambda: {"name": "", "sent_kbps": 0.0, "recv_kbps": 0.0, "total_bytes": 0.0})
    program_totals = defaultdict(lambda: {"sent_kbps": 0.0, "recv_kbps": 0.0, "total_bytes": 0.0})

    try:
        while True:
            # Non-blocking read
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line or line.startswith(("Adding", "Ethernet", "Refreshing")):
                    continue

                try:
                    cmd, sent, recv = line.rsplit("\t", 2)
                    sent = float(sent)
                    recv = float(recv)

                    name, uuid = normalize_name(cmd)

                    # Track individual process instance
                    if uuid not in programs:
                        programs[uuid]["name"] = name
                    programs[uuid]["sent_kbps"] += sent
                    programs[uuid]["recv_kbps"] += recv
                    programs[uuid]["total_bytes"] += (sent + recv) * 1024 / 8  # kbps -> bytes/sec

                    # Aggregate totals by program name
                    program_totals[name]["sent_kbps"] += sent
                    program_totals[name]["recv_kbps"] += recv
                    program_totals[name]["total_bytes"] += (sent + recv) * 1024 / 8

                except ValueError:
                    continue

            # Yield totals for the UI
            yield program_totals

            await asyncio.sleep(update_interval)

    except asyncio.CancelledError:
        # Cleanly terminate nethogs if cancelled
        proc.terminate()
        raise
