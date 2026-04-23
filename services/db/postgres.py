#!/usr/bin/env python3
"""
Script to run a PostgreSQL container using Docker.
The container is named 'test_db' and can be customized via environment variables.
"""

import subprocess
import sys
import os

from ..start.daemon import start_docker_daemon
from dotenv import load_dotenv

load_dotenv()

CONTAINER_NAME = os.getenv("CONTAINER_NAME")
IMAGE = os.getenv("IMAGE")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
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
        # sys.exit(1)
        return False
    # Optional: check if Docker daemon is running by calling 'docker info'
    returncode, _, stderr = run_command(["docker", "info"])
    if returncode != 0:
        print("Docker daemon is not running. Please start Docker and try again.")
        # sys.exit(1)
        return False
    return True

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

def run_postgres(database_name) -> str:
    """Run the PostgreSQL container."""
    print(f"Starting PostgreSQL container '{CONTAINER_NAME}'...")
    cmd = [
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "-e", f"POSTGRES_USER={POSTGRES_USER}",
        "-e", f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
        "-e", f"POSTGRES_DB={database_name}",
        "-p", f"{HOST_PORT}:{CONTAINER_PORT}",
        IMAGE
    ]
    returncode, stdout, stderr = run_command(cmd)
    if returncode != 0:
        print(f"Failed to start container: {stderr}")
        sys.exit(1)
    container_id = stdout.strip()
    connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{HOST_PORT}/{database_name}"
    print(f"Container started successfully (ID: {container_id})")
    print(f"Connection string: postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{HOST_PORT}/{database_name}")
    return connection_string

def process_postgres(postgres_db: str = None) -> str:
    """
    Script to run a PostgreSQL container using Docker.
    The container is named 'test_db' and can be customized via environment variables.
    """
    if not postgres_db:
        postgres_db = POSTGRES_DB

    status = check_docker()
    if not status:
        start_docker_daemon()
    if container_exists(CONTAINER_NAME):
        print(f"Container '{CONTAINER_NAME}' already exists. Removing it...")
        remove_container(CONTAINER_NAME)
    print(f"Starting PostgreSQL container with database: {postgres_db}...")
    connection_string = run_postgres(postgres_db)
    return connection_string


if __name__ == "__main__":
    process_postgres(None)