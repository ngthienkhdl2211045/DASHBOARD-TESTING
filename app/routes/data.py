import os
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Resident, SocioEconomicData

data_bp = Blueprint('data', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@data_bp.route('/data')
@login_required
def data_view():
    residents = Resident.query.order_by(Resident.id.desc()).limit(50).all()
    econ_data = SocioEconomicData.query.order_by(SocioEconomicData.year.desc()).limit(50).all()
    return render_template('data.html', residents=residents, econ_data=econ_data)


@data_bp.route('/data/upload-residents', methods=['POST'])
@login_required
def upload_residents():
    """
    Import file dân cư. File cần có các cột:
    full_name, dob (YYYY-MM-DD), gender (Nam/Nữ), address, occupation, household_status
    """
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('Vui lòng chọn file.', 'danger')
        return redirect(url_for('data.data_view'))

    if not allowed_file(file.filename):
        flash('Chỉ chấp nhận file .csv, .xlsx, .xls', 'danger')
        return redirect(url_for('data.data_view'))

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        required_cols = {'full_name'}
        if not required_cols.issubset(set(df.columns)):
            flash(f'File thiếu cột bắt buộc: {required_cols}', 'danger')
            return redirect(url_for('data.data_view'))

        count = 0
        for _, row in df.iterrows():
            dob = None
            if 'dob' in df.columns and pd.notna(row.get('dob')):
                try:
                    dob = pd.to_datetime(row['dob']).date()
                except Exception:
                    dob = None

            resident = Resident(
                full_name=str(row.get('full_name', '')).strip(),
                dob=dob,
                gender=str(row.get('gender', '')).strip() if pd.notna(row.get('gender')) else None,
                address=str(row.get('address', '')).strip() if pd.notna(row.get('address')) else None,
                occupation=str(row.get('occupation', '')).strip() if pd.notna(row.get('occupation')) else None,
                household_status=str(row.get('household_status', '')).strip() if pd.notna(row.get('household_status')) else None,
            )
            db.session.add(resident)
            count += 1

        db.session.commit()
        flash(f'Đã import thành công {count} bản ghi dân cư.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi đọc file: {str(e)}', 'danger')

    return redirect(url_for('data.data_view'))


@data_bp.route('/data/upload-economic', methods=['POST'])
@login_required
def upload_economic():
    """
    Import file KT-XH. File cần có các cột: year, indicator, value, unit (tùy chọn)
    """
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('Vui lòng chọn file.', 'danger')
        return redirect(url_for('data.data_view'))

    if not allowed_file(file.filename):
        flash('Chỉ chấp nhận file .csv, .xlsx, .xls', 'danger')
        return redirect(url_for('data.data_view'))

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        required_cols = {'year', 'indicator', 'value'}
        if not required_cols.issubset(set(df.columns)):
            flash(f'File thiếu cột bắt buộc: {required_cols}', 'danger')
            return redirect(url_for('data.data_view'))

        count = 0
        for _, row in df.iterrows():
            entry = SocioEconomicData(
                year=int(row['year']),
                indicator=str(row['indicator']).strip(),
                value=float(row['value']),
                unit=str(row.get('unit', '')).strip() if pd.notna(row.get('unit')) else None,
            )
            db.session.add(entry)
            count += 1

        db.session.commit()
        flash(f'Đã import thành công {count} bản ghi KT-XH.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi đọc file: {str(e)}', 'danger')

    return redirect(url_for('data.data_view'))


@data_bp.route('/data/resident/<int:resident_id>/delete', methods=['POST'])
@login_required
def delete_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    db.session.delete(resident)
    db.session.commit()
    flash('Đã xóa bản ghi.', 'success')
    return redirect(url_for('data.data_view'))
