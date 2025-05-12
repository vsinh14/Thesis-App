import sqlite3
import os
import time

class database:
    @staticmethod
    def path():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.db")

    @staticmethod
    def db_create():
        """Creates the database table if it does not exist."""
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT,
                caption TEXT,
                tag TEXT,
                description TEXT,
                timestamp INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def db_insert(image, caption, tags, description, timestamp):
        """Inserts image metadata into the database."""
        database.db_create()  # Ensure table exists
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        timestamp = int(time.time())
        sql = 'INSERT INTO image_table (image_name, caption, tag, description, timestamp) VALUES (?, ?, ?, ?, ?)'
        cursor.execute(sql, (image, caption, tags, description, timestamp))
        conn.commit()
        conn.close()

    @staticmethod
    def db_select_recent(days=3):
        """Fetches tags from images uploaded in the last X days."""
        database.db_create()  # Ensure table exists
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        time_threshold = int(time.time()) - (57 + days)
        #time_threshold = int(time.time()) - (days * 86400)
        cursor.execute("SELECT tag FROM image_table WHERE timestamp > ?", (time_threshold,))
        records = cursor.fetchall()
        conn.close()
        return records  # Returns a list of tag strings

