from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db

account_bp = Blueprint('account', __name__)


@account_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account_view():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', '').strip()
        current_user.email = request.form.get('email', '').strip()

        new_password = request.form.get('new_password', '')
        if new_password:
            confirm = request.form.get('confirm_password', '')
            if new_password != confirm:
                flash('Mật khẩu xác nhận không khớp.', 'danger')
                return redirect(url_for('account.account_view'))
            current_user.set_password(new_password)

        db.session.commit()
        flash('Đã cập nhật thông tin tài khoản.', 'success')
        return redirect(url_for('account.account_view'))

    return render_template('account.html')
