from app import mysql
from flask import current_app
import MySQLdb.cursors

class Book:
    def __init__(self, id=None, title=None, author=None, isbn=None, 
                 publisher=None, publication_year=None, category=None, 
                 description=None):
        self.id = id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.publication_year = publication_year
        self.category = category
        self.description = description

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM books')
        books = cur.fetchall()
        cur.close()
        return books

    @staticmethod
    def get_by_id(book_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM books WHERE book_id = %s', (book_id,))
        book = cur.fetchone()
        cur.close()
        return book

    def save(self):
        cur = mysql.connection.cursor()
        if self.id:
            # Update existing book
            cur.execute('''
                UPDATE books 
                SET title=%s, author=%s, isbn=%s, publisher=%s, 
                    publication_year=%s, category=%s, description=%s
                WHERE book_id=%s
            ''', (self.title, self.author, self.isbn, self.publisher,
                 self.publication_year, self.category, self.description, self.id))
        else:
            # Insert new book
            cur.execute('''
                INSERT INTO books (title, author, isbn, publisher, 
                                 publication_year, category, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (self.title, self.author, self.isbn, self.publisher,
                 self.publication_year, self.category, self.description))
        
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete(book_id):
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM books WHERE book_id = %s', (book_id,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_latest(limit=6):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM books ORDER BY created_at DESC LIMIT %s', (limit,))
        books = cur.fetchall()
        cur.close()
        return books

    @staticmethod
    def get_top_rated(limit=6):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT * FROM books 
            WHERE total_reviews > 0 
            ORDER BY average_rating DESC, total_reviews DESC 
            LIMIT %s
        ''', (limit,))
        books = cur.fetchall()
        cur.close()
        return books

    @staticmethod
    def search(query):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # 安全地构建搜索参数
        search_pattern = '%' + query + '%'
        params = tuple([search_pattern] * 7)  # 需要7个参数用于LIKE和CASE语句
        
        cur.execute('''
            SELECT * FROM books 
            WHERE title LIKE %s 
            OR author LIKE %s 
            OR category LIKE %s 
            OR description LIKE %s
            ORDER BY 
                CASE 
                    WHEN title LIKE %s THEN 1
                    WHEN author LIKE %s THEN 2
                    WHEN category LIKE %s THEN 3
                    ELSE 4
                END,
                average_rating DESC,
                total_reviews DESC
        ''', params)
        
        books = cur.fetchall()
        cur.close()
        return books
  