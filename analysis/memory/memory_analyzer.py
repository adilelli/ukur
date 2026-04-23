from concurrent.futures import process
import os

import psutil

def get_postgres_memory() -> (float | None):
    try:
        process = psutil.Process(os.getpid())
        print(f"Process RSS: {process.memory_info().rss / (1024**2):.2f} MB")
        rss = process.memory_info().rss / (1024**2)  # MB
        return rss
    except:
        print("PostgreSQL process not found.")
        return None  


if __name__ == "__main__":
    memory_usage = get_postgres_memory()