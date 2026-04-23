import asyncio

import streamlit as st
import psycopg2
import asyncpg
import sqlite3
import time
import pandas as pd

from services.db.postgres import process_postgres
from analysis.memory.memory_analyzer import get_postgres_memory

# --- SQLite initialization (logs) ---
def init_sqlite():
    conn = sqlite3.connect("query_logs.db")
    c = conn.cursor()
    # c.execute('''
    #     DROP TABLE IF EXISTS query_performance
    # ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS query_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            connection_string TEXT,
            query_text TEXT,
            execution_time_ms REAL,
            rows_returned INTEGER,
            error TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_sqlite()

def log_query(connection_string, query, elapsed_ms, rows_returned, error):
    conn = sqlite3.connect("query_logs.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO query_performance (connection_string, query_text, execution_time_ms, rows_returned, error)
        VALUES (?, ?, ?, ?, ?)
    ''', (connection_string, query, elapsed_ms, rows_returned, error))
    conn.commit()
    conn.close()

# --- UI ---
st.title("PostgreSQL Query Performance Tester")

st.subheader("Connect automatically")
db_name = st.text_input("Database Name", value="testdb", key="db_name")

if "connection_string" not in st.session_state:
    st.session_state.connection_string = ""

if st.button("Start PostgreSQL Container"):
    st.session_state.connection_string = process_postgres(db_name)
    if st.session_state.connection_string:
        st.success("PostgreSQL container started successfully with database: " + db_name)
        st.info(f"Connection string: {st.session_state.connection_string}")
    else:
        st.error("Failed to start PostgreSQL container.")
# Connection string input
st.subheader("Or connect via connection string")
conn_str = st.text_area(
    "PostgreSQL Connection String",
    height=100,
    placeholder="Example: postgresql://user:password@localhost:5432/testdb"
)

# SQL query input
sql_query = st.text_area("SQL Query", height=150)

col1, col2, col3 = st.columns(3)
with col1:
    run_sync_btn = st.button("Run Synchronous Query")
with col2:
    run_async_btn = st.button("Run Asynchronous Query")
with col3:
    show_logs_btn = st.button("Show History")



def run_sync_query(connection_db, sql_query):
    st.info("Executing: " + st.session_state.connection_string)
    if not st.session_state.connection_string.strip() and not conn_str.strip():
        st.error("Please provide a PostgreSQL connection string.")
    else:
        connection_db = st.session_state.connection_string.strip() if st.session_state.connection_string.strip() else conn_str.strip()
        with st.spinner("Executing..."):
            pg_conn = None
            try:
                # Connect using the user-provided connection string
                pg_conn = psycopg2.connect(connection_db)
                pg_conn.autocommit = True
                cursor = pg_conn.cursor()

                memory_before = get_postgres_memory()
                start = time.perf_counter()
                cursor.execute(sql_query)
                elapsed_ms = (time.perf_counter() - start) * 1000
                memory_after = get_postgres_memory()

                rows_returned = 0
                try:
                    rows = cursor.fetchall()
                    rows_returned = len(rows)
                    if rows:
                        st.subheader("Results (first 10 rows)")
                        # Display as DataFrame for better readability
                        st.dataframe(pd.DataFrame(rows))
                except psycopg2.ProgrammingError:
                    # No result set (e.g., INSERT/UPDATE)
                    st.info("Query executed successfully (no result set).")

                log_query(connection_db, sql_query, elapsed_ms, rows_returned, None)
                st.success(f"Execution time: {elapsed_ms:.2f} ms | Rows: {rows_returned} | Memory Before: {memory_before:.2f} MB | Memory After: {memory_after:.2f} MB")

            except Exception as e:
                log_query(connection_db, sql_query, None, None, str(e))
                st.error(f"Error: {e}")
            finally:
                if pg_conn:
                    pg_conn.close()


async def run_async_query(connection_db, sql_query):
    st.info("Executing: " + st.session_state.connection_string)
    if not st.session_state.connection_string.strip() and not conn_str.strip():
        st.error("Please provide a PostgreSQL connection string.")
    else:
        connection_db = st.session_state.connection_string.strip() if st.session_state.connection_string.strip() else conn_str.strip()
        with st.spinner("Executing..."):
            pg_conn_async = None
            try:
                # Connect using the user-provided connection string
                pg_conn_async = await asyncpg.connect(connection_db)
                # pg_conn.autocommit = True
                
                memory_before = get_postgres_memory()
                start = time.perf_counter()
                cursor = await pg_conn_async.fetch(sql_query)
                elapsed_ms = (time.perf_counter() - start) * 1000
                memory_after = get_postgres_memory()

                rows_returned = 0
                try:
                    # rows = await cursor.fetch()
                    rows_returned = len(cursor)
                    if rows_returned:
                        st.subheader("Results (first 10 rows)")
                        # Display as DataFrame for better readability
                        st.dataframe(pd.DataFrame(cursor))
                except psycopg2.ProgrammingError:
                    # No result set (e.g., INSERT/UPDATE)
                    st.info("Query executed successfully (no result set).")

                log_query(connection_db, sql_query, elapsed_ms, rows_returned, None)
                st.success(f"Execution time: {elapsed_ms:.2f} ms | Rows: {rows_returned} | Memory Before: {memory_before:.2f} MB | Memory After: {memory_after:.2f} MB")

            except Exception as e:
                log_query(connection_db, sql_query, None, None, str(e))
                st.error(f"Error: {e}")
            finally:
                if pg_conn_async:
                    await pg_conn_async.close()

if run_sync_btn and sql_query.strip():
    run_sync_query(st.session_state.connection_string, sql_query)

if run_async_btn and sql_query.strip():
    asyncio.run(run_async_query(st.session_state.connection_string, sql_query))

if show_logs_btn:
    conn = sqlite3.connect("query_logs.db")
    df = pd.read_sql_query("SELECT * FROM query_performance ORDER BY timestamp DESC", conn)
    conn.close()
    st.dataframe(df)