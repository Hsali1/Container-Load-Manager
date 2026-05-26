import sqlite3
from data_types import Box, Container

Box_row = tuple[str, float, float, float]

def create_database_and_tables(filename: str) -> sqlite3.Connection:
    if not filename:
        filename = ":memory:"
    
    connection = sqlite3.connect(filename)

    # explicitly enforce that data follows foreign key
    connection.execute("PRAGMA foreign_keys = 1;")
    connection.commit()

    ddl = """
        DROP TABLE IF EXISTS boxes;
        CREATE TABLE boxes (
            id INTEGER NOT NULL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            x REAL NOT NULL,
            y REAL NOT NULL,
            z REAL NOT NULL,
            CONSTRAINT max_volume CHECK (x * y * z < 10)
        );
        DROP TABLE IF EXISTS freight;
        CREATE TABLE freight (
            id INTEGER PRIMARY KEY,
            container_id INTEGER NOT NULL,
            box_id INTEGER NOT NULL REFERENCES boxes(id) ON DELETE CASCADE
        );
        CREATE VIEW IF NOT EXISTS containers
        AS
        SELECT container_id, round(sum(x * y * z), 2) as occupied_volume
        FROM freight f
        LEFT JOIN boxes b on f.box_id = b.id
        GROUP BY container_id;
    """

    connection.executescript(ddl)

    return connection


# def seed_data(connection: sqlite3.Connection):
#     starter_boxes = [
#         ("a1", 1.2, 2.2, 1.2),
#         ("a2", 2.2, 2.2, 1.42),
#         ("a3", 1.2, 2.2, 1.2),
#         ("a4", 1.2, 2.2, 1.2),
#         ("a5", 1.2, 2.2, 1.2),
#         ("a6", 1.2, 2.2, 1.2),
#         ("a7", 1.2, 2.2, 1.2)
#     ]


def database_add_box(connection: sqlite3.Connection, box: Box_row) -> None:
    try:
        connection.execute(
            "INSERT INTO boxes (name, x, y, z) VALUES (?, ?, ?, ?)",
            box
        )
        connection.commit()
        print("\nBox saved successfully!\n")
    except sqlite3.IntegrityError as e:
        print("\nSorry, could not persist box to database: ", e, '\n')


def database_get_all_boxes(connection: sqlite3.Connection) -> list[Box]:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM boxes")
    result = cursor.fetchall()
    return [Box(*b) for b in result]


def get_box(connection: sqlite3.Connection, name=None, id=None) -> Box:
    fetched = None
    if name is not None:
        fetched = connection.execute(
            "SELECT * FROM boxes WHERE name = ?",
            (name,)
        ).fetchone()
    elif id is not None:
        fetched = connection.execute(
            "SELECT * FROM boxes WHERE id = ?",
            (id,)
        ).fetchone()
    if fetched:
        return Box(*fetched)
    

def get_container(connection: sqlite3.Connection, id=None) -> Container:
    fetched = None
    if id is not None:
        fetched = connection.execute(
            "SELECT * FROM containers WHERE container_id = ?",
            (id,)
        ).fetchone()
    if fetched:
        return Container(*fetched)
    

def add_box_to_container(connection: sqlite3.Connection, box_id, container_id) -> None:
    if box_id is not None and container_id is not None:
        connection.execute(
            "INSERT INTO freight (container_id, box_id) VALUES (:cid, :bid)",
            {
                "cid": container_id,
                "bid": box_id
            }
        )
        connection.commit()

