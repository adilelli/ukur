from concurrent.futures import process
import os

import psutil

def get_postgres_percent_memory() -> (tuple[float, float] | tuple[None, None]):
    try:
        process = psutil.Process(os.getpid())
        rss_percent = process.memory_percent(memtype='rss')
        print(f"Memory Usage (RSS): {rss_percent:.2f}%")
        return rss_percent
    except:
        print("PostgreSQL process not found.")
        return None   


if __name__ == "__main__":
    memory_usage = get_postgres_percent_memory()