# Dashboard Dân cư - Kinh tế Xã hội (UBND Xã)

Web dashboard quản lý dữ liệu dân cư và kinh tế - xã hội, xây dựng bằng Flask.

## 1. Chạy thử trên máy (local)

### Bước 1: Cài Python
Cần Python 3.10+ (kiểm tra bằng `python --version` hoặc `python3 --version`).
Tải tại: https://www.python.org/downloads/ (nhớ tick "Add Python to PATH" khi cài trên Windows)

### Bước 2: Cài thư viện
Mở terminal/cmd tại thư mục dự án, chạy:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Bước 3: Tạo dữ liệu mẫu để demo
```bash
python seed.py
```
Lệnh này tạo sẵn 300 người dân giả, dữ liệu KT-XH 6 năm, 2 sự kiện, và 2 tài khoản:
- **admin / admin123** (quyền quản trị)
- **canbo / canbo123** (quyền người dùng thường)

### Bước 4: Chạy server
```bash
python run.py
```
Mở trình duyệt vào: **http://localhost:5000**

Đăng nhập bằng tài khoản `admin / admin123` để xem đầy đủ tính năng (kể cả trang Quản trị).

---

## 2. Cấu trúc dự án

```
ubnd_dashboard/
├── app/
│   ├── __init__.py        # Khởi tạo Flask app, đăng ký blueprint
│   ├── models.py           # Định nghĩa bảng database (User, Resident, ...)
│   ├── routes/              # Các route xử lý từng trang
│   │   ├── auth.py          # Đăng nhập / đăng ký
│   │   ├── main.py          # Trang chủ + API dữ liệu biểu đồ
│   │   ├── calendar.py       # Lịch sự kiện
│   │   ├── chat.py           # Chat
│   │   ├── data.py           # Quản lý & import dữ liệu
│   │   ├── account.py        # Tài khoản
│   │   ├── admin.py          # Trang quản trị
│   │   └── notifications.py  # Thông báo
│   ├── templates/            # Giao diện HTML (Jinja2)
│   └── static/                # CSS, JS
├── seed.py                    # Script tạo dữ liệu mẫu
├── run.py                     # File chạy app
└── requirements.txt
```

## 3. Cách import dữ liệu thật của xã

Vào trang **Quản lý dữ liệu**, upload file Excel/CSV theo đúng định dạng cột:

**File dân cư** cần các cột: `full_name, dob, gender, address, occupation, household_status`
- `dob` định dạng `YYYY-MM-DD` (VD: 1990-05-20)
- `gender`: `Nam` hoặc `Nữ`

**File KT-XH** cần các cột: `year, indicator, value, unit`
- VD: `2025, Thu nhập bình quân, 45, triệu đồng/người/năm`

Có thể tạo file mẫu bằng Excel rồi lưu thành `.xlsx` hoặc `.csv` để test.

---

## 4. Deploy lên Internet (miễn phí) bằng Render.com

### Bước 1: Đưa code lên GitHub
1. Tạo tài khoản GitHub (nếu chưa có): https://github.com
2. Tạo repository mới, ví dụ tên `ubnd-dashboard`
3. Upload toàn bộ thư mục dự án lên (kéo thả trên web GitHub, hoặc dùng git):
```bash
git init
git add .
git commit -m "Init dashboard project"
git branch -M main
git remote add origin https://github.com/<username>/ubnd-dashboard.git
git push -u origin main
```

### Bước 2: Tạo tài khoản Render
Vào https://render.com, đăng ký bằng GitHub (miễn phí, không cần thẻ tín dụng cho gói free).

### Bước 3: Tạo Database PostgreSQL miễn phí
1. Trên Render Dashboard → **New** → **PostgreSQL**
2. Đặt tên (VD: `ubnd-db`) → chọn **Free** plan → **Create Database**
3. Sau khi tạo xong, copy giá trị **Internal Database URL** (sẽ dùng ở bước sau)

### Bước 4: Deploy Web Service
1. Trên Render Dashboard → **New** → **Web Service**
2. Chọn **Build and deploy from a Git repository** → kết nối repo `ubnd-dashboard` vừa tạo
3. Điền cấu hình:
   - **Name**: `ubnd-dashboard`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Instance Type**: Free
4. Vào tab **Environment**, thêm biến môi trường:
   - `DATABASE_URL` = (dán giá trị Internal Database URL từ Bước 3)
   - `SECRET_KEY` = (một chuỗi bất kỳ, VD: `xa-dashboard-2026-secret-key`)
5. Bấm **Create Web Service** → đợi vài phút để Render build và deploy

### Bước 5: Tạo dữ liệu mẫu trên server (tùy chọn)
Sau khi deploy xong, vào tab **Shell** của Web Service trên Render, chạy:
```bash
python seed.py
```
(hoặc bạn tự đăng ký tài khoản qua trang `/register` — tài khoản đầu tiên đăng ký sẽ tự động là admin)

### Bước 6: Truy cập
Render sẽ cấp cho bạn 1 URL dạng: `https://ubnd-dashboard.onrender.com`
Đây là link bạn dùng để demo và nộp báo cáo.

⚠️ **Lưu ý về gói Free của Render**: server sẽ "ngủ" sau 15 phút không có ai truy cập, và mất khoảng 30-50 giây để "thức dậy" ở lượt truy cập tiếp theo. Điều này bình thường với gói free — khi demo trực tiếp, bạn nên mở link trước vài phút để server sẵn sàng.

---

## 5. Việc cần làm trong 1 tuần tới (ưu tiên cho demo giữa kỳ)

1. Chạy thử local, hiểu luồng code (`app/__init__.py` → `routes/` → `templates/`)
2. Chạy `python seed.py` để có dữ liệu đẹp cho demo
3. Test đăng nhập, thử từng trang (dashboard, lịch, chat, quản lý dữ liệu, tài khoản, admin)
4. Chuẩn bị 1 file Excel dữ liệu dân cư thật (hoặc gần thật) của xã để import demo trực tiếp
5. Deploy lên Render theo hướng dẫn trên
6. Chuẩn bị vài câu giải thích ngắn gọn về kiến trúc (Flask, SQLAlchemy, Chart.js) để trả lời câu hỏi khi báo cáo

## 6. Việc làm thêm cho đến cuối tháng (deadline cuối)

- Cải thiện giao diện, thêm bộ lọc dữ liệu theo Ấp/Thôn, theo năm
- Thêm chức năng xuất báo cáo (PDF/Excel) từ dashboard
- Viết tài liệu/báo cáo mô tả hệ thống, sơ đồ ERD, sơ đồ luồng dữ liệu
- Test kỹ với dữ liệu thật của xã, sửa lỗi phát sinh
- Có thể nâng cấp chat thành realtime bằng Flask-SocketIO nếu còn thời gian
