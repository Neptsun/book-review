from flask import Blueprint, render_template
from app.models.book import Book

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # 获取最新添加的书籍
    latest_books = Book.get_latest(limit=6)
    # 获取评分最高的书籍
    top_rated_books = Book.get_top_rated(limit=6)
    return render_template('index.html', latest_books=latest_books, top_rated_books=top_rated_books) 