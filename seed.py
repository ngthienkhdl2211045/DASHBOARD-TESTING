"""
Script tạo dữ liệu mẫu để demo dashboard ngay lập tức.
Chạy: python seed.py
"""
import random
from datetime import date, timedelta
from app import create_app, db
from app.models import User, Resident, SocioEconomicData, Event

app = create_app()

FIRST_NAMES = ['Nguyễn Văn', 'Trần Thị', 'Lê Văn', 'Phạm Thị', 'Hoàng Văn', 'Vũ Thị', 'Đặng Văn', 'Bùi Thị']
LAST_NAMES = ['An', 'Bình', 'Cường', 'Dung', 'Em', 'Phong', 'Giang', 'Hà', 'Khang', 'Linh', 'Minh', 'Nam']
OCCUPATIONS = ['Nông dân', 'Công nhân', 'Buôn bán', 'Giáo viên', 'Cán bộ xã', 'Học sinh/Sinh viên', 'Nghỉ hưu', 'Khác']
ADDRESSES = ['Ấp 1', 'Ấp 2', 'Ấp 3', 'Ấp 4', 'Ấp 5']
HOUSEHOLD_STATUS = ['Thường trú', 'Tạm trú']

with app.app_context():
    db.drop_all()
    db.create_all()

    # Tạo tài khoản admin mẫu
    admin = User(username='admin', full_name='Quản trị viên', email='admin@xa.gov.vn', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # Tạo thêm 1 tài khoản cán bộ thường
    staff = User(username='canbo', full_name='Nguyễn Văn Cán Bộ', email='canbo@xa.gov.vn', role='user')
    staff.set_password('canbo123')
    db.session.add(staff)

    db.session.commit()

    # Sinh 300 bản ghi dân cư mẫu
    for _ in range(300):
        gender = random.choice(['Nam', 'Nữ'])
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        age = random.randint(1, 85)
        dob = date.today() - timedelta(days=age * 365 + random.randint(0, 364))
        resident = Resident(
            full_name=f'{first} {last}',
            dob=dob,
            gender=gender,
            address=random.choice(ADDRESSES),
            occupation=random.choice(OCCUPATIONS) if age >= 15 else 'Học sinh/Sinh viên',
            household_status=random.choices(HOUSEHOLD_STATUS, weights=[85, 15])[0],
        )
        db.session.add(resident)

    # Dữ liệu KT-XH mẫu qua các năm
    years = [2020, 2021, 2022, 2023, 2024, 2025]
    incomes = [28, 31, 34, 38, 42, 46]
    poverty_rates = [8.5, 7.2, 6.5, 5.1, 4.0, 3.2]

    for y, inc, pov in zip(years, incomes, poverty_rates):
        db.session.add(SocioEconomicData(year=y, indicator='Thu nhập bình quân', value=inc, unit='triệu đồng/người/năm'))
        db.session.add(SocioEconomicData(year=y, indicator='Tỷ lệ hộ nghèo', value=pov, unit='%'))

    # Vài sự kiện mẫu
    db.session.add(Event(title='Họp giao ban xã', description='Họp định kỳ hàng tháng', date=date.today() + timedelta(days=3), created_by=admin.id))
    db.session.add(Event(title='Ngày hội đại đoàn kết toàn dân', description='Tổ chức tại nhà văn hóa xã', date=date.today() + timedelta(days=10), created_by=admin.id))

    db.session.commit()
    print('✅ Đã tạo dữ liệu mẫu thành công!')
    print('   Đăng nhập admin: username=admin, password=admin123')
    print('   Đăng nhập cán bộ: username=canbo, password=canbo123')
