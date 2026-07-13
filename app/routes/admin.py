from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
@login_required
@admin_required
def admin_view():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin.html', users=users)


@admin_bp.route('/admin/user/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Không thể tự thay đổi quyền của chính mình.', 'danger')
        return redirect(url_for('admin.admin_view'))
    user.role = 'user' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f'Đã cập nhật quyền cho {user.username}.', 'success')
    return redirect(url_for('admin.admin_view'))


@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Không thể tự xóa chính mình.', 'danger')
        return redirect(url_for('admin.admin_view'))
    db.session.delete(user)
    db.session.commit()
    flash('Đã xóa tài khoản.', 'success')
    return redirect(url_for('admin.admin_view'))
