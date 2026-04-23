#!/usr/bin/env python3
"""
Script to run a Redis cache container using Docker.
The container is named 'cache' and can be customized via environment variables.
"""

import subprocess
import sys
import os

CONTAINER_NAME = "cache"
IMAGE = "redis:latest"               # Use a specific version if needed, e.g., "redis:7"

# Optional Redis configuration
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")   # if set, Redis will require authentication
HOST_PORT = os.getenv("HOST_PORT", "6379")
CONTAINER_PORT = "6379"

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
    # Stop if running
    run_command(["docker", "stop", name])
    # Remove
    run_command(["docker", "rm", name])

def run_redis():
    """Run the Redis container."""
    print(f"Starting Redis container '{CONTAINER_NAME}'...")
    cmd = [
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "-p", f"{HOST_PORT}:{CONTAINER_PORT}",
        IMAGE
    ]
    # Add password if provided
    if REDIS_PASSWORD:
        # Redis requires --requirepass argument to set password
        cmd.extend(["redis-server", "--requirepass", REDIS_PASSWORD])

    returncode, stdout, stderr = run_command(cmd)
    if returncode != 0:
        print(f"Failed to start container: {stderr}")
        sys.exit(1)
    container_id = stdout.strip()
    print(f"Container started successfully (ID: {container_id})")
    # Connection info
    if REDIS_PASSWORD:
        print(f"Connection: redis-cli -h localhost -p {HOST_PORT} -a {REDIS_PASSWORD}")
    else:
        print(f"Connection: redis-cli -h localhost -p {HOST_PORT}")

def main():
    check_docker()
    if container_exists(CONTAINER_NAME):
        print(f"Container '{CONTAINER_NAME}' already exists. Removing it...")
        remove_container(CONTAINER_NAME)
    run_redis()

if __name__ == "__main__":
    main()