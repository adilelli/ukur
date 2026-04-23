#!/usr/bin/env python3
"""
Script to run a MySQL container using Docker.
The container is named 'test_db' and can be customized via environment variables.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

CONTAINER_NAME = os.getenv("CONTAINER_NAME")
IMAGE = os.getenv("IMAGE")

MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")      # optional
MYSQL_USER = os.getenv("MYSQL_USER")                 # optional
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") # optional
HOST_PORT = os.getenv("HOST_PORT")
CONTAINER_PORT = os.getenv("CONTAINER_PORT")

def run_command(cmd):
    """Execute a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def check_docker():
    """Check if Docker is installed and running."""
    returncode, _, stderr = run_command(["docker", "--version"])
    if returncode != 0:
        print("Docker is not installed or not in PATH. Please install Docker and try again.")
        sys.exit(1)
    returncode, _, stderr = run_command(["docker", "info"])
    if returncode != 0:
        print("Docker daemon is not running. Please start Docker and try again.")
        sys.exit(1)

def container_exists(name):
    """Check if a container with the given name exists (running or stopped)."""
    returncode, stdout, _ = run_command(["docker", "ps", "-a", "--format", "{{.Names}}", "--filter", f"name={name}"])
    return name in stdout.split()

def remove_container(name):
    """Stop and remove the container if it exists."""
    run_command(["docker", "stop", name])
    run_command(["docker", "rm", name])

def run_mysql():
    """Run the MySQL container."""
    print(f"Starting MySQL container '{CONTAINER_NAME}'...")
    cmd = [
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "-e", f"MYSQL_ROOT_PASSWORD={MYSQL_ROOT_PASSWORD}",
        "-p", f"{HOST_PORT}:{CONTAINER_PORT}",
        IMAGE
    ]
    # Optional: add database, user, and user password if provided
    if MYSQL_DATABASE:
        cmd.extend(["-e", f"MYSQL_DATABASE={MYSQL_DATABASE}"])
    if MYSQL_USER and MYSQL_PASSWORD:
        cmd.extend(["-e", f"MYSQL_USER={MYSQL_USER}", "-e", f"MYSQL_PASSWORD={MYSQL_PASSWORD}"])
    
    returncode, stdout, stderr = run_command(cmd)
    if returncode != 0:
        print(f"Failed to start container: {stderr}")
        sys.exit(1)
    container_id = stdout.strip()
    print(f"Container started successfully (ID: {container_id})")
    print(f"Connection info: mysql -h localhost -P {HOST_PORT} -u root -p")
    if MYSQL_USER and MYSQL_PASSWORD:
        print(f"Alternatively, user '{MYSQL_USER}' with password '{MYSQL_PASSWORD}' can connect.")

def main():
    check_docker()
    if container_exists(CONTAINER_NAME):
        print(f"Container '{CONTAINER_NAME}' already exists. Removing it...")
        remove_container(CONTAINER_NAME)
    run_mysql()

if __name__ == "__main__":
    main()