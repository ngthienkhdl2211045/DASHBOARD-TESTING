from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app import db
from app.models import Message, User, Notification

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat')
@chat_bp.route('/chat/<int:user_id>')
@login_required
def chat_view(user_id=None):
    users = User.query.filter(User.id != current_user.id).all()
    messages = []
    active_user = None

    if user_id:
        active_user = User.query.get_or_404(user_id)
        messages = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id),
            )
        ).order_by(Message.timestamp).all()

    return render_template('chat.html', users=users, messages=messages, active_user=active_user)


@chat_bp.route('/chat/<int:user_id>/send', methods=['POST'])
@login_required
def send_message(user_id):
    content = request.form.get('content', '').strip()
    if content:
        msg = Message(sender_id=current_user.id, receiver_id=user_id, content=content)
        db.session.add(msg)
        db.session.add(Notification(
            user_id=user_id,
            content=f'Tin nhắn mới từ {current_user.full_name or current_user.username}',
            type='message',
        ))
        db.session.commit()
    return redirect(url_for('chat.chat_view', user_id=user_id))


@chat_bp.route('/api/chat/<int:user_id>/poll')
@login_required
def poll_messages(user_id):
    """Dùng để tự động refresh tin nhắn mới (polling đơn giản, không cần websocket)"""
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id),
        )
    ).order_by(Message.timestamp).all()
    return jsonify([
        {
            'sender_id': m.sender_id,
            'content': m.content,
            'time': m.timestamp.strftime('%H:%M %d/%m'),
        }
        for m in messages
    ])
