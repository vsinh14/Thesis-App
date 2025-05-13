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
                tag TEXT,
                timestamp INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def db_insert(image, tags, timestamp):
        """Inserts image metadata into the database."""
        database.db_create()  # Ensure table exists
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        timestamp = int(time.time())
        sql = 'INSERT INTO image_table (image_name,  tag,  timestamp) VALUES (?, ?, ?)'
        cursor.execute(sql, (image, tags, timestamp))
        conn.commit()
        conn.close()

    @staticmethod
    def db_select_recent(delay):
        """Fetches tags from images uploaded in the last X days."""
        database.db_create()  # Ensure table exists
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        time_threshold = int(time.time()) - delay 
        #time_threshold = int(time.time()) - (days * 86400)
        cursor.execute("SELECT tag FROM image_table WHERE timestamp > ?", (time_threshold,))
        records = cursor.fetchall()
        conn.close()
        return records  # Returns a list of tag strings

    @staticmethod
    def db_select_all():
        """Fetches all image metadata from the database."""
        database.db_create()  # Ensure table exists
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        cursor.execute("SELECT image_name,  tag FROM image_table")
        records = cursor.fetchall()
        conn.close()
        return records  # Returns a list of tuples containing image data

    @staticmethod
    def db_select_tags(image_name):
        """Fetches the tags for a specific image by its filename."""
        database.db_create()  # Ensure table exists
        conn = sqlite3.connect(database.path())
        cursor = conn.cursor()
        cursor.execute("SELECT tag FROM image_table WHERE image_name = ?", (image_name,))
        tags = cursor.fetchall()
        conn.close()
        # Return a list of tags
        print(tags)
        return [tag[0] for tag in tags]  # Fetches tags as a list of strings

