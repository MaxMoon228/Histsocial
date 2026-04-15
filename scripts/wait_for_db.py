import os
import time

import psycopg2


def wait():
    db_name = os.getenv("DB_NAME", "chronograph")
    db_user = os.getenv("DB_USER", "chronograph")
    db_password = os.getenv("DB_PASSWORD", "chronograph")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    for _ in range(40):
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            conn.close()
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("Database is not ready")


if __name__ == "__main__":
    wait()
