import os

class Config:
    # Flask 应用密钥，用于会话安全
    # 在生产环境中，应该设置为一个复杂的随机值
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    # MySQL 数据库配置
    # 在生产环境中，这些值应该通过环境变量设置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'your-mysql-username'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'your-mysql-password'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'book_review'

    # 可选：其他配置选项
    # SESSION_COOKIE_SECURE = True  # 仅通过HTTPS发送cookie
    # PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 会话持续时间
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传文件大小（16MB） 