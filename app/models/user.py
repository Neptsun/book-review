from app import mysql
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id=None, username=None, email=None, password=None, role='user'):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def save(self):
        cur = mysql.connection.cursor()
        if self.password:
            password_hash = generate_password_hash(self.password)
        
        if self.id:
            # Update existing user
            if self.password:
                cur.execute('''
                    UPDATE users 
                    SET username=%s, email=%s, password_hash=%s, role=%s
                    WHERE user_id=%s
                ''', (self.username, self.email, password_hash, self.role, self.id))
            else:
                cur.execute('''
                    UPDATE users 
                    SET username=%s, email=%s, role=%s
                    WHERE user_id=%s
                ''', (self.username, self.email, self.role, self.id))
        else:
            # Insert new user
            cur.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
            ''', (self.username, self.email, password_hash, self.role))
        
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def get_by_email(email):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def verify_password(stored_password_hash, password):
        return check_password_hash(stored_password_hash, password)

    @staticmethod
    def get_user_stats(user_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT 
                COUNT(*) as total_reviews,
                COUNT(DISTINCT book_id) as reviewed_books,
                AVG(rating) as avg_rating
            FROM reviews
            WHERE user_id = %s
        ''', (user_id,))
        stats = cur.fetchone()
        cur.close()
        return stats

    @staticmethod
    def get_user_reviews(user_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT r.*, b.title as book_title, b.author as book_author
            FROM reviews r
            JOIN books b ON r.book_id = b.book_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        ''', (user_id,))
        reviews = cur.fetchall()
        cur.close()
        return reviews