from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Event, Notification, User

calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.route('/calendar')
@login_required
def calendar_view():
    return render_template('calendar.html')


@calendar_bp.route('/api/events')
@login_required
def get_events():
    events = Event.query.all()
    return jsonify([
        {
            'id': e.id,
            'title': e.title,
            'start': e.date.isoformat(),
            'description': e.description or '',
        }
        for e in events
    ])


@calendar_bp.route('/calendar/add', methods=['POST'])
@login_required
def add_event():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    date_str = request.form.get('date', '')

    if not title or not date_str:
        flash('Vui lòng nhập tên sự kiện và ngày.', 'danger')
        return redirect(url_for('calendar.calendar_view'))

    event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    event = Event(title=title, description=description, date=event_date, created_by=current_user.id)
    db.session.add(event)

    # Tạo thông báo cho tất cả người dùng khác
    for user in User.query.filter(User.id != current_user.id).all():
        db.session.add(Notification(
            user_id=user.id,
            content=f'Sự kiện mới: {title} ({event_date.strftime("%d/%m/%Y")})',
            type='event',
        ))

    db.session.commit()
    flash('Đã thêm sự kiện.', 'success')
    return redirect(url_for('calendar.calendar_view'))
