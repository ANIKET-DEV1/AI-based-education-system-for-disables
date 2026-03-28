import os
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "builditon.db")


class Helper:
    def __init__(self):
        print("Connecting to database...")
        self.db_path = DB_PATH
        db = self._get_connection()
        cur = db.cursor()

        queries = [
        """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",

        """CREATE TABLE IF NOT EXISTS lessons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            original_text TEXT,
            simplified_text TEXT,
            audio_path TEXT,
            video_path TEXT,
            image_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );""",

        """CREATE TABLE IF NOT EXISTS progress(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            status TEXT DEFAULT 'not_started',
            score INTEGER DEFAULT 0,
            level TEXT DEFAULT 'easy',
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
        );"""
        ]

        for q in queries:
            cur.execute(q)

        db.commit()
        cur.close()
        db.close()
        print("Connected!")

    def _get_connection(self):
        """Get a new SQLite connection."""
        return sqlite3.connect(self.db_path)

    def insert_user(self, username, email, password):
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
            if cur.fetchone():
                return 2
            hashed = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed)
            )
            db.commit()
            return True

        except Exception as e:
            print("Error:", e)
            return False
        finally:
            if db:
                db.close()

    def auth_user(self, username, password):
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()
            cur.execute("SELECT id, password FROM users WHERE username=?", (username,))
            result = cur.fetchone()

            if result:
                user_id, stored_password = result
                if check_password_hash(stored_password, password):
                    return user_id

            return 0

        except Exception as e:
            print("Error:", e)
            return 0
        finally:
            if db:
                db.close()

    def save_lesson(self, user_id, title, original, simplified, audio, video):
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()
            query = """
            INSERT INTO lessons (user_id, title, original_text, simplified_text, audio_path, video_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cur.execute(query, (user_id, title, original, simplified, audio, video))
            db.commit()

            return cur.lastrowid

        except Exception as e:
            print("Error:", e)
            return 0
        finally:
            if db:
                db.close()

    def get_lessons(self, user_id=None):
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()
            if user_id:
                cur.execute("SELECT * FROM lessons WHERE user_id=? ORDER BY created_at DESC", (user_id,))
            else:
                cur.execute("SELECT * FROM lessons ORDER BY created_at DESC")
            return cur.fetchall()

        except Exception as e:
            print("Error:", e)
            return []
        finally:
            if db:
                db.close()


    def save_progress(self, user_id, lesson_id, score, level):
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()

            query = """
            INSERT INTO progress (user_id, lesson_id, score, level, status)
            VALUES (?, ?, ?, ?, 'completed')
            """

            cur.execute(query, (user_id, lesson_id, score, level))
            db.commit()

            return True

        except Exception as e:
            print("Error:", e)
            return False
        finally:
            if db:
                db.close()

    def get_user_progress(self, user_id):
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()

            query = """
            SELECT p.score, p.level, l.title
            FROM progress p
            JOIN lessons l ON p.lesson_id = l.id
            WHERE p.user_id = ?
            """

            cur.execute(query, (user_id,))
            return cur.fetchall()

        except Exception as e:
            print("Error:", e)
            return []
        finally:
            if db:
                db.close()

    def get_user_stats(self, user_id):
        """Get user statistics for dashboard."""
        db = None
        try:
            db = self._get_connection()
            cur = db.cursor()
            
            cur.execute("SELECT COUNT(*) FROM lessons WHERE user_id=?", (user_id,))
            lesson_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM progress WHERE user_id=? AND status='completed'", (user_id,))
            completed = cur.fetchone()[0]
            
            cur.execute("SELECT AVG(score) FROM progress WHERE user_id=?", (user_id,))
            avg_score = cur.fetchone()[0] or 0
            
            return {
                "lessons": lesson_count,
                "completed": completed,
                "avg_score": round(avg_score, 1)
            }
        except Exception as e:
            print("Error:", e)
            return {"lessons": 0, "completed": 0, "avg_score": 0}
        finally:
            if db:
                db.close()