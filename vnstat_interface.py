import subprocess
import json
import inspect
import os
import sys
# RX = Download
#TX = Upload

chosen_interface = "wlan0"
def debug_print(message,er=None):
    """Prints a message along with the file name and line number of the caller."""
    # Get frame info of the caller's stack
    frame_info = inspect.getframeinfo(inspect.currentframe().f_back)
    filename = os.path.basename(frame_info.filename)
    line_number = frame_info.lineno
    print(f"DEBUG {filename} line {line_number}: {message}",file=sys.stderr)
    if(er != None):
        print(f"\tError: {er}")

def set_interface(interface_name:str):
    global chosen_interface
    valid_options = get_vnstat_interfaces()
    if(interface_name not in valid_options):
        return -1
    else:
        chosen_interface = interface_name
        return 0
def get_interface():
    global chosen_interface
    return chosen_interface
def get_vnstat_interfaces():
    cmd = ["vnstat", "--json", "m"]  # monthly JSON output
    interfaces = []
    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for inter in data['interfaces']:
            interfaces.append(inter.get("name",None))
        for name in interfaces:
            if(name == None):
                interfaces.remove(None)
        return interfaces
    except subprocess.CalledProcessError as e:
        debug_print("Error running command")
        return None
    except json.JSONDecodeError as je:
        debug_print("Error decoding json")

        return None

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
    global chosen_interface
    cmd = ["vnstat", "--json", "m"]  # monthly JSON output

    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse JSON
        data = json.loads(result.stdout)
        section_to_use = None
        for inter in data['interfaces']:
            if(inter["name"] == chosen_interface):
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
    global chosen_interface

    cmd = ["vnstat", "--json", "d"]  # monthly JSON output

    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse JSON
        data = json.loads(result.stdout)
        section_to_use = None
        for inter in data['interfaces']:
            if(inter["name"] == chosen_interface):
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
    global chosen_interface

    cmd = ["vnstat", "--json", "y"]  # monthly JSON output

    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse JSON
        data = json.loads(result.stdout)
        section_to_use = None
        for inter in data['interfaces']:
            if(inter["name"] == chosen_interface):
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