from app import mysql
import MySQLdb.cursors

class ReviewReply:
    def __init__(self, id=None, review_id=None, user_id=None, content=None):
        self.id = id
        self.review_id = review_id
        self.user_id = user_id
        self.content = content

    def save(self):
        cur = mysql.connection.cursor()
        if self.id:
            cur.execute('''
                UPDATE review_replies 
                SET content=%s, updated_at=CURRENT_TIMESTAMP
                WHERE reply_id=%s
            ''', (self.content, self.id))
        else:
            cur.execute('''
                INSERT INTO review_replies (review_id, user_id, content)
                VALUES (%s, %s, %s)
            ''', (self.review_id, self.user_id, self.content))
        
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_by_review(review_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT r.*, u.username
            FROM review_replies r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.review_id = %s
            ORDER BY r.created_at ASC
        ''', (review_id,))
        replies = cur.fetchall()
        cur.close()
        return replies

class ReviewLike:
    @staticmethod
    def like(review_id, user_id):
        cur = mysql.connection.cursor()
        try:
            # 尝试插入点赞
            cur.execute('''
                INSERT INTO review_likes (review_id, user_id)
                VALUES (%s, %s)
            ''', (review_id, user_id))
            
            # 更新评论的点赞数
            cur.execute('''
                UPDATE reviews r
                SET likes_count = (
                    SELECT COUNT(*) FROM review_likes 
                    WHERE review_id = r.review_id
                )
                WHERE review_id = %s
            ''', (review_id,))
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error in ReviewLike.like: {str(e)}")
            return False
        finally:
            cur.close()

    @staticmethod
    def unlike(review_id, user_id):
        cur = mysql.connection.cursor()
        try:
            # 删除点赞
            cur.execute('''
                DELETE FROM review_likes 
                WHERE review_id = %s AND user_id = %s
            ''', (review_id, user_id))
            
            # 更新评论的点赞数
            cur.execute('''
                UPDATE reviews r
                SET likes_count = (
                    SELECT COUNT(*) FROM review_likes 
                    WHERE review_id = r.review_id
                )
                WHERE review_id = %s
            ''', (review_id,))
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error in ReviewLike.unlike: {str(e)}")
            return False
        finally:
            cur.close()

    @staticmethod
    def get_user_like(review_id, user_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            SELECT 1 as liked 
            FROM review_likes 
            WHERE review_id = %s AND user_id = %s
        ''', (review_id, user_id))
        result = cur.fetchone()
        cur.close()
        return bool(result)

    @staticmethod
    def check_table():
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name = 'review_likes'
            ''')
            exists = cur.fetchone()[0]
            if not exists:
                print("review_likes table does not exist!")
                return
            
            cur.execute('SHOW CREATE TABLE review_likes')
            table_def = cur.fetchone()[1]
            print("Table structure:")
            print(table_def)
        except Exception as e:
            print(f"Error checking table: {str(e)}")
        finally:
            cur.close()