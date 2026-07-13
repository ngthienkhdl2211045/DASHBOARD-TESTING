from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models import Resident, SocioEconomicData

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def dashboard():
    total_residents = Resident.query.count()
    male_count = Resident.query.filter_by(gender='Nam').count()
    female_count = Resident.query.filter_by(gender='Nữ').count()
    return render_template(
        'dashboard.html',
        total_residents=total_residents,
        male_count=male_count,
        female_count=female_count,
    )


@main_bp.route('/api/dashboard-data')
@login_required
def dashboard_data():
    # Biểu đồ giới tính
    gender_rows = db.session.query(Resident.gender, func.count(Resident.id)).group_by(Resident.gender).all()
    gender_data = {g or 'Không rõ': c for g, c in gender_rows}

    # Biểu đồ độ tuổi (nhóm tuổi)
    residents = Resident.query.all()
    age_groups = {'0-17': 0, '18-35': 0, '36-60': 0, '60+': 0}
    from datetime import date
    today = date.today()
    for r in residents:
        if not r.dob:
            continue
        age = today.year - r.dob.year - ((today.month, today.day) < (r.dob.month, r.dob.day))
        if age <= 17:
            age_groups['0-17'] += 1
        elif age <= 35:
            age_groups['18-35'] += 1
        elif age <= 60:
            age_groups['36-60'] += 1
        else:
            age_groups['60+'] += 1

    # Biểu đồ nghề nghiệp (top 6)
    occ_rows = (
        db.session.query(Resident.occupation, func.count(Resident.id))
        .filter(Resident.occupation.isnot(None))
        .group_by(Resident.occupation)
        .order_by(func.count(Resident.id).desc())
        .limit(6)
        .all()
    )
    occupation_data = {o: c for o, c in occ_rows}

    # Biểu đồ KT-XH theo năm (ví dụ: thu nhập bình quân)
    econ_rows = (
        SocioEconomicData.query.filter_by(indicator='Thu nhập bình quân')
        .order_by(SocioEconomicData.year)
        .all()
    )
    econ_labels = [str(r.year) for r in econ_rows]
    econ_values = [r.value for r in econ_rows]

    # Tỷ lệ hộ nghèo theo năm
    poverty_rows = (
        SocioEconomicData.query.filter_by(indicator='Tỷ lệ hộ nghèo')
        .order_by(SocioEconomicData.year)
        .all()
    )
    poverty_labels = [str(r.year) for r in poverty_rows]
    poverty_values = [r.value for r in poverty_rows]

    return jsonify({
        'gender': gender_data,
        'age_groups': age_groups,
        'occupation': occupation_data,
        'income': {'labels': econ_labels, 'values': econ_values},
        'poverty': {'labels': poverty_labels, 'values': poverty_values},
    })
