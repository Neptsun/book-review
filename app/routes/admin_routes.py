from flask import Blueprint, render_template, request, jsonify, session
from app.auth import admin_required
from app import mysql
import MySQLdb.cursors
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/reports')
@admin_required
def reports():
    status = request.args.get('status', 'pending')
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if status == 'pending':
        # 对于待处理的举报，只显示未删除的评论
        cur.execute('''
            SELECT rr.*, 
                   r.comment as review_comment,
                   r.book_id,
                   b.title as book_title,
                   u1.username as reporter_username,
                   u2.username as review_username
            FROM review_reports rr
            JOIN reviews r ON rr.review_id = r.review_id
            JOIN books b ON r.book_id = b.book_id
            JOIN users u1 ON rr.reporter_id = u1.user_id
            JOIN users u2 ON r.user_id = u2.user_id
            WHERE rr.status = 'pending'
            AND r.is_deleted = FALSE
            ORDER BY rr.created_at DESC
        ''')
    else:
        # 对于已处理的举报，显示所有记录
        cur.execute('''
            SELECT rr.*, 
                   r.comment as review_comment,
                   r.book_id,
                   r.is_deleted,
                   r.deleted_at,
                   b.title as book_title,
                   u1.username as reporter_username,
                   u2.username as review_username
            FROM review_reports rr
            JOIN reviews r ON rr.review_id = r.review_id
            JOIN books b ON r.book_id = b.book_id
            JOIN users u1 ON rr.reporter_id = u1.user_id
            JOIN users u2 ON r.user_id = u2.user_id
            WHERE rr.status = %s
            ORDER BY rr.resolved_at DESC
        ''', (status,))
    reports = cur.fetchall()
    cur.close()
    
    return render_template('admin/reports.html', reports=reports)

@bp.route('/reports/<int:report_id>/<action>', methods=['POST'])
@admin_required
def handle_report(report_id, action):
    if action not in ['resolve', 'reject']:
        return jsonify({'error': 'Invalid action'}), 400
    
    status = 'resolved' if action == 'resolve' else 'rejected'
    
    cur = mysql.connection.cursor()
    try:
        # 获取评论ID
        cur.execute('''
            SELECT review_id FROM review_reports WHERE report_id = %s
        ''', (report_id,))
        review_id = cur.fetchone()[0]

        # 如果接受举报，软删除评论及其关联数据
        if action == 'resolve':
            # 1. 删除相关的点赞记录
            cur.execute('DELETE FROM review_likes WHERE review_id = %s', (review_id,))
            
            # 2. 删除相关的回复记录
            cur.execute('DELETE FROM review_replies WHERE review_id = %s', (review_id,))
            
            # 3. 更新所有相关举报的状态为已处理
            cur.execute('''
                UPDATE review_reports
                SET status = %s, resolved_at = %s
                WHERE review_id = %s AND status = 'pending'
            ''', (status, datetime.now(), review_id))
            
            # 4. 软删除评论（标记为已删除）
            cur.execute('''
                UPDATE reviews 
                SET is_deleted = TRUE, deleted_at = %s
                WHERE review_id = %s
            ''', (datetime.now(), review_id))
        else:
            # 如果拒绝举报，只更新当前举报的状态
            cur.execute('''
                UPDATE review_reports
                SET status = %s, resolved_at = %s
                WHERE report_id = %s
            ''', (status, datetime.now(), report_id))
        
        mysql.connection.commit()
        return jsonify({'message': f'Report {action}d successfully'})
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error handling report: {str(e)}")
        return jsonify({'error': 'Failed to process report'}), 500
    finally:
        cur.close() 