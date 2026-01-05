import subprocess
import json
# RX = Download
#TX = Upload
def bytes_to_mb(bytes_value: int) -> float:
    """
    Convert bytes to megabytes (MB), rounded to 2 decimal places.
    """
    mb = bytes_value / (1024 ** 2)
    return round(mb, 2)

def bytes_to_gb(bytes_value: int) -> float:
    """
    Convert bytes to gigabytes (GB), rounded to 2 decimal places.
    """
    gb = bytes_value / (1024 ** 3)
    return round(gb, 2)




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
            return timestamp,bytes_to_mb(tx),bytes_to_mb(rx)
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
            return timestamp,bytes_to_mb(tx),bytes_to_mb(rx)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")

def get_year_output():
    cmd = ["vnstat", "--json", "y"]  # monthly JSON output

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
            month_data = traffic['year'][len(traffic['year'])-1]
            timestamp = month_data["timestamp"]
            rx = month_data["rx"]
            tx = month_data['tx']
            return timestamp,bytes_to_gb(tx),bytes_to_gb(rx)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")