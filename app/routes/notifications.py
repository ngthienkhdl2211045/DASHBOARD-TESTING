from flask import Blueprint, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notif_bp = Blueprint('notif', __name__)


@notif_bp.route('/api/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).limit(20).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({
        'unread_count': unread_count,
        'items': [
            {
                'id': n.id,
                'content': n.content,
                'type': n.type,
                'is_read': n.is_read,
                'time': n.created_at.strftime('%H:%M %d/%m'),
            }
            for n in notifications
        ]
    })


@notif_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})
