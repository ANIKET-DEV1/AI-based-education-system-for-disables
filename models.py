import pymysql as sql
from werkzeug.security import check_password_hash, generate_password_hash


class Helper:
    def __init__(self):
        print("Connecting to database...")
        self.db = sql.connect(
            host="localhost",
            user="root",
            passwd="Awesome123.",
            database="builditon"
        )

        print("Connected!")
        queries = [
        """CREATE TABLE IF NOT EXISTS users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",

        """CREATE TABLE IF NOT EXISTS lessons(
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            original_text TEXT,
            simplified_text TEXT,
            audio_path VARCHAR(255),
            video_path VARCHAR(255),
            image_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

    
        """CREATE TABLE IF NOT EXISTS progress(
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            lesson_id INT NOT NULL,

            status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
            score INT DEFAULT 0,
            level ENUM('easy','medium','hard') DEFAULT 'easy',

            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
        );"""
        ]

        cur = self.db.cursor()

        for q in queries:
            cur.execute(q)

        cur.close()
   

    def insert_user(self, username, email, password):
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
            if cur.fetchone():
                return 2
            hashed = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users(username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed)
            )
            self.db.commit()
            return True

        except Exception as e:
            print("Error:", e)
            return False
        finally:
            cur.close()

    def auth_user(self, username, password):
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))
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
            cur.close()

    def save_lesson(self, title, original, simplified, audio, video):
        try:
            cur = self.db.cursor()
            query = """
            INSERT INTO lessons (title, original_text, simplified_text, audio_path, video_path)
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (title, original, simplified, audio, video))
            self.db.commit()

            return cur.lastrowid  # return lesson ID

        except Exception as e:
            print("Error:", e)
            return 0
        finally:
            cur.close()

    def get_lessons(self):
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM lessons ORDER BY created_at DESC")
            return cur.fetchall()

        except Exception as e:
            print("Error:", e)
            return []
        finally:
            cur.close()


    def save_progress(self, user_id, lesson_id, score, level):
        try:
            cur = self.db.cursor()

            query = """
            INSERT INTO progress (user_id, lesson_id, score, level, status)
            VALUES (%s, %s, %s, %s, 'completed')
            """

            cur.execute(query, (user_id, lesson_id, score, level))
            self.db.commit()

            return True

        except Exception as e:
            print("Error:", e)
            return False
        finally:
            cur.close()

    def get_user_progress(self, user_id):
        try:
            cur = self.db.cursor()

            query = """
            SELECT p.score, p.level, l.title
            FROM progress p
            JOIN lessons l ON p.lesson_id = l.id
            WHERE p.user_id = %s
            """

            cur.execute(query, (user_id,))
            return cur.fetchall()

        except Exception as e:
            print("Error:", e)
            return []
        finally:
            cur.close()