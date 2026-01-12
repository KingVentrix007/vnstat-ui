import subprocess
from collections import defaultdict
import time

# Start nethogs in text mode
proc = subprocess.Popen(
    ["sudo", "nethogs", "-t"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1
)

def normalize_name(proc: str):
    normalized_name = proc
    if "/proc/self" in proc:
        normalized_name = "Nethog"
    elif "/opt/" in proc:
        parts = proc.split("/")
        name = parts[3].split(" ")[0]
        normalized_name = name.capitalize()
    elif " " in proc:
        first_part = proc.split(" ")[0]
        name = first_part.split("/")[-1]
        normalized_name = name.capitalize()
    else:
        name = proc.split("/")[-1]
        if name.isdigit():
            for part in reversed(proc.split("/")):
                if part.isalpha():
                    normalized_name = part.capitalize()
                    break
        else:
            normalized_name = name.capitalize()

    uuid_code = hash(proc)
    return normalized_name, uuid_code

# Dictionary for per-instance tracking
programs = defaultdict(lambda: {"name": "", "sent_kbps": 0.0, "recv_kbps": 0.0, "total_bytes": 0.0})

# Dictionary for per-program totals (human-readable)
program_totals = defaultdict(lambda: {"sent_kbps": 0.0, "recv_kbps": 0.0, "total_bytes": 0.0})

print("Starting live nethogs tracker... Ctrl+C to stop.")

try:
    for raw in proc.stdout:
        line = raw.strip()
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
            programs[uuid]["total_bytes"] += (sent + recv) * 1024 / 8  # Convert kbps -> Bytes/sec

            # Aggregate totals by program name
            program_totals[name]["sent_kbps"] += sent
            program_totals[name]["recv_kbps"] += recv
            program_totals[name]["total_bytes"] += (sent + recv) * 1024 / 8

        except ValueError:
            continue

        # Example: print live totals every few seconds
        if int(time.time()) % 5 == 0:  # every ~5 seconds
            print("\n=== Program Bandwidth Totals (KBps) ===")
            for prog, data in program_totals.items():
                print(f"{prog}: Sent {data['sent_kbps']:.2f} KBps | Recv {data['recv_kbps']:.2f} KBps | Total {data['total_bytes'] / 1024:.2f} KB")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping tracker...")
    proc.terminate()
