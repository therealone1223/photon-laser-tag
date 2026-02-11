import psycopg2

# Database connection settings
DB_NAME = "photon"
DB_HOST = "127.0.0.1"
DB_PORT = 5432

# Try student first
DB_USER = "student"
DB_PASSWORD = "student"


def add_player(player_id: int, codename: str):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (id, codename) VALUES (%s, %s);",
                    (player_id, codename)
                )
    finally:
        conn.close()


if __name__ == "__main__":
    add_player(101, "EvionTest1")
    add_player(102, "EvionTest2")
    print("Inserted 2 players successfully.")

