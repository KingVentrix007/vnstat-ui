import subprocess
import json

# The Linux command you want to run (as a list of arguments)


def get_month_output():
    cmd = ["vnstat", "--json", "m"]  # monthly JSON output

    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse JSON
        data = json.loads(result.stdout)
        section_to_use = None
        for inter in data['interfaces']:
            if(inter["name"] == "wlan0"):
                section_to_use = inter
                break
        # Pretty-print JSON
        # print(json.dumps(section_to_use, indent=4))
        if(section_to_use != None):
            traffic = section_to_use['traffic']
            month_data = traffic['month'][len(traffic['month'])-1]
            timestamp = month_data["timestamp"]
            rx = month_data["rx"]
            tx = month_data['tx']
            return timestamp,rx,tx
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")

def get_day_output():
    cmd = ["vnstat", "--json", "d"]  # monthly JSON output

    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse JSON
        data = json.loads(result.stdout)
        section_to_use = None
        for inter in data['interfaces']:
            if(inter["name"] == "wlan0"):
                section_to_use = inter
                break
        # Pretty-print JSON
        # print(json.dumps(section_to_use, indent=4))
        if(section_to_use != None):
            traffic = section_to_use['traffic']
            month_data = traffic['day'][len(traffic['day'])-1]
            timestamp = month_data["timestamp"]
            rx = month_data["rx"]
            tx = month_data['tx']
            return timestamp,rx,tx
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")

# print(get_day_output())