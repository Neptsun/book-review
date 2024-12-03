from app import mysql
import MySQLdb.cursors
from datetime import datetime

class Review:
    def __init__(self, id=None, book_id=None, user_id=None, rating=None, comment=None):
        self.id = id
        self.book_id = book_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment

    def save(self):
        cur = mysql.connection.cursor()
        if self.id:
            # Update existing review
            cur.execute('''
                UPDATE reviews 
                SET rating=%s, comment=%s, updated_at=CURRENT_TIMESTAMP
                WHERE review_id=%s
            ''', (self.rating, self.comment, self.id))
        else:
            # Insert new review
            cur.execute('''
                INSERT INTO reviews (book_id, user_id, rating, comment)
                VALUES (%s, %s, %s, %s)
            ''', (self.book_id, self.user_id, self.rating, self.comment))
            
            # Update book's average rating
            self.update_book_rating()
        
        mysql.connection.commit()
        cur.close()

    def update_book_rating(self):
        cur = mysql.connection.cursor()
        cur.execute('''
            UPDATE books b
            SET average_rating = (
                SELECT AVG(rating)
                FROM reviews r
                WHERE r.book_id = b.book_id
            ),
            total_reviews = (
                SELECT COUNT(*)
                FROM reviews r
                WHERE r.book_id = b.book_id
            )
            WHERE b.book_id = %s
        ''', (self.book_id,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_by_id(review_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT r.*, u.username 
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.review_id = %s
            AND r.is_deleted = FALSE
        ''', (review_id,))
        review = cur.fetchone()
        cur.close()
        return review

    @staticmethod
    def get_by_book_id(book_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT r.*, u.username 
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.book_id = %s
            AND r.is_deleted = FALSE
            ORDER BY r.created_at DESC
        ''', (book_id,))
        reviews = cur.fetchall()
        cur.close()
        return reviews

    @staticmethod
    def get_user_review(book_id, user_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT * FROM reviews 
            WHERE book_id = %s AND user_id = %s
            AND is_deleted = FALSE
        ''', (book_id, user_id))
        review = cur.fetchone()
        cur.close()
        return review

    @staticmethod
    def delete(review_id):
        cur = mysql.connection.cursor()
        try:
            # 检查评论是否已被删除
            cur.execute('''
                SELECT book_id, is_deleted 
                FROM reviews 
                WHERE review_id = %s
            ''', (review_id,))
            result = cur.fetchone()
            if not result:
                return False
            
            book_id, is_deleted = result
            if is_deleted:
                return False  # 评论已经被删除
            
            # 软删除评论
            cur.execute('''
                UPDATE reviews 
                SET is_deleted = TRUE, deleted_at = CURRENT_TIMESTAMP
                WHERE review_id = %s
            ''', (review_id,))
            print(f"Review deleted: {review_id}")
            
            # 删除相关的点赞记录
            cur.execute('DELETE FROM review_likes WHERE review_id = %s', (review_id,))
            
            # 删除相关的回复记录
            cur.execute('DELETE FROM review_replies WHERE review_id = %s', (review_id,))
            
            # Update book's average rating (只计算未删除的评论)
            cur.execute('''
                UPDATE books b
                SET average_rating = COALESCE((
                    SELECT AVG(rating)
                    FROM reviews r
                    WHERE r.book_id = b.book_id
                    AND r.is_deleted = FALSE
                ), 0),
                total_reviews = (
                    SELECT COUNT(*)
                    FROM reviews r
                    WHERE r.book_id = b.book_id
                    AND r.is_deleted = FALSE
                )
                WHERE b.book_id = %s
            ''', (book_id,))
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error deleting review: {str(e)}")
            return False
        finally:
            cur.close() 