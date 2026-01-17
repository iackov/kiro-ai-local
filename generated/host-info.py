import platform
import subprocess
import os

def get_basic_system_info():
    info = {}

    # Get operating system details
    info['system'] = platform.system()
    info['node'] = platform.node()
    info['release'] = platform.release()
    info['version'] = platform.version()

    # Get processor information
    try:
        info['processor'] = platform.processor()
    except NotImplementedError:
        info['processor'] = 'Processor info not available'

    # Get total memory
    try:
        result = subprocess.run(['free', '-m'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        lines = output.split('\n')
        for line in lines:
            if 'Mem:' in line:
                parts = line.split()
                info['total_memory'] = int(parts[1])
                break
    except FileNotFoundError:
        info['total_memory'] = 'Memory info not available'

    # Get disk usage
    try:
        result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        lines = output.split('\n')
        for line in lines[1:]:
            parts = line.split()
            if len(parts) > 1:
                info['disk_usage'] = parts[4]
                break
    except FileNotFoundError:
        info['disk_usage'] = 'Disk usage info not available'

    # Get current working directory
    info['current_working_dir'] = os.getcwd()

    return info

if __name__ == "__main__":
    system_info = get_basic_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")