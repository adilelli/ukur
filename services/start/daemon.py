import subprocess
import sys
import platform
import os

def start_docker_daemon():
    """
    Detect the operating system and start the Docker daemon if it is not already running.
    
    Returns:
        bool: True if Docker daemon is running after this function, False otherwise.
    """
    # Helper to run shell commands
    def run_cmd(cmd, capture_output=True, check=False):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=check)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return -1, "", str(e)

    # Check if Docker command exists
    docker_exists_code, _, _ = run_cmd("docker --version")
    if docker_exists_code != 0:
        print("Docker is not installed or not in PATH.")
        return False

    # Check if Docker daemon is running (using 'docker info')
    info_code, _, _ = run_cmd("docker info")
    if info_code == 0:
        print("Docker daemon is already running.")
        return True

    # Determine OS and attempt to start the daemon
    os_type = platform.system().lower()
    print(f"Detected OS: {os_type}. Attempting to start Docker daemon...")

    if os_type == "linux":
        # Try systemd, then service command, and finally using sudo if needed.
        start_cmds = [
            "systemctl start docker",
            "service docker start",
            "sudo systemctl start docker",
            "sudo service docker start"
        ]
        for cmd in start_cmds:
            code, _, err = run_cmd(cmd)
            if code == 0:
                print(f"Started Docker using: {cmd}")
                # Give it a moment to come up
                import time
                time.sleep(2)
                # Verify again
                info_code, _, _ = run_cmd("docker info")
                return info_code == 0
            else:
                print(f"Command '{cmd}' failed: {err}")
        print("Unable to start Docker daemon on Linux. Please start it manually.")
        return False

    elif os_type == "darwin":
        # macOS: Docker Desktop is usually an application.
        # Try to open Docker.app
        docker_app_path = "/Applications/Docker.app"
        if os.path.exists(docker_app_path):
            code, _, err = run_cmd(f"open -a {docker_app_path}")
            if code == 0:
                print("Launched Docker Desktop. Waiting for daemon to start...")
                # Wait up to 30 seconds for Docker to be ready
                for _ in range(30):
                    import time
                    time.sleep(1)
                    info_code, _, _ = run_cmd("docker info")
                    if info_code == 0:
                        print("Docker daemon is now running.")
                        return True
                print("Timeout waiting for Docker daemon.")
            else:
                print(f"Failed to launch Docker Desktop: {err}")
        else:
            print("Docker Desktop not found in /Applications. Please install Docker Desktop.")
        return False

    elif os_type == "windows":
        # On Windows, try to start Docker Desktop using PowerShell commands.
        # First attempt: start the service "Docker Desktop Service"
        start_cmds = [
            'powershell -Command "Start-Service -Name \"Docker Desktop Service\""',
            'powershell -Command "Start-Process \'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\'"'
        ]
        for cmd in start_cmds:
            code, _, err = run_cmd(cmd)
            if code == 0:
                print("Attempted to start Docker Desktop. Waiting...")
                # Wait for daemon to become responsive
                for _ in range(30):
                    import time
                    time.sleep(1)
                    info_code, _, _ = run_cmd("docker info")
                    if info_code == 0:
                        print("Docker daemon is now running.")
                        return True
                print("Timeout waiting for Docker daemon.")
            else:
                print(f"Command '{cmd}' failed: {err}")
        print("Unable to start Docker daemon on Windows. Please start Docker Desktop manually.")
        return False

    else:
        print(f"Unsupported OS: {os_type}")
        return False

# Example usage
if __name__ == "__main__":
    if start_docker_daemon():
        print("Docker is ready.")
    else:
        print("Failed to start Docker daemon.")
        sys.exit(1)