from flask import Blueprint, request, jsonify, session
from app.models.interaction import ReviewReply, ReviewLike
from app.auth import login_required
from app import mysql
import MySQLdb.cursors

bp = Blueprint('interactions', __name__, url_prefix='/interactions')

@bp.route('/review/<int:review_id>/like', methods=['POST'])
@login_required
def like_review(review_id):
    try:
        action = request.form.get('action')
        if action not in ['like', 'unlike']:
            return jsonify({'error': 'Invalid action'}), 400
        
        if action == 'like':
            success = ReviewLike.like(review_id, session['user_id'])
        else:
            success = ReviewLike.unlike(review_id, session['user_id'])
            
        if success:
            return jsonify({'message': f'Review {action}d successfully'})
        return jsonify({'error': f'Failed to {action} review'}), 500
    except Exception as e:
        print(f"Error in like route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/review/<int:review_id>/likes')
def get_likes(review_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT likes_count FROM reviews WHERE review_id = %s', (review_id,))
    likes = cur.fetchone() or {'likes_count': 0}
    
    # Get user's current like status if logged in
    if 'user_id' in session:
        likes['user_liked'] = ReviewLike.get_user_like(review_id, session['user_id'])
    
    cur.close()
    return jsonify(likes)

@bp.route('/check_table')
def check_table():
    ReviewLike.check_table()
    return jsonify({'message': 'Check terminal for table structure'})

@bp.route('/review/<int:review_id>/reply', methods=['POST'])
@login_required
def add_reply(review_id):
    content = request.form.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    reply = ReviewReply(
        review_id=review_id,
        user_id=session['user_id'],
        content=content
    )
    reply.save()
    
    return jsonify({'message': 'Reply added successfully'})

@bp.route('/review/<int:review_id>/replies')
def get_replies(review_id):
    replies = ReviewReply.get_by_review(review_id)
    return jsonify(replies)

@bp.route('/review/<int:review_id>/report', methods=['POST'])
@login_required
def report_review(review_id):
    # 检查是否已经举报过
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT 1 FROM review_reports 
        WHERE review_id = %s AND reporter_id = %s
    ''', (review_id, session['user_id']))
    if cur.fetchone():
        cur.close()
        return jsonify({'error': 'You have already reported this review'}), 400
    
    # 添加举报
    cur.execute('''
        INSERT INTO review_reports (review_id, reporter_id, reason)
        VALUES (%s, %s, %s)
    ''', (review_id, session['user_id'], 'Reported by user'))
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Review reported successfully'})
  