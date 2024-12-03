from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 确保设置了 SECRET_KEY
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'dev'
    
    mysql.init_app(app)
    
    from app.routes import main_routes, book_routes, auth_routes, review_routes, user_routes, interaction_routes, admin_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(review_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(interaction_routes.bp)
    app.register_blueprint(admin_routes.bp)
    
    # 设置首页路由
    app.add_url_rule('/', endpoint='index', view_func=main_routes.index)
    
    return app 