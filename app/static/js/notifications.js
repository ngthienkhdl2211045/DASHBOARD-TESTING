document.addEventListener('DOMContentLoaded', function () {
    const bell = document.getElementById('notifBell');
    const dropdown = document.getElementById('notifDropdown');
    const badge = document.getElementById('notifBadge');
    const list = document.getElementById('notifList');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (!bell) return; // chưa đăng nhập thì không có topbar

    async function loadNotifications() {
        try {
            const res = await fetch('/api/notifications');
            const data = await res.json();

            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }

            if (data.items.length === 0) {
                list.innerHTML = '<div class="text-muted text-center p-3">Không có thông báo</div>';
                return;
            }

            list.innerHTML = data.items.map(n => `
                <div class="notif-item ${n.is_read ? '' : 'fw-semibold'}">
                    <div>${n.content}</div>
                    <small class="text-muted">${n.time}</small>
                </div>
            `).join('');
        } catch (e) {
            console.error('Lỗi tải thông báo', e);
        }
    }

    bell.addEventListener('click', async function (e) {
        e.stopPropagation();
        dropdown.classList.toggle('d-none');
        if (!dropdown.classList.contains('d-none')) {
            await fetch('/notifications/mark-read', { method: 'POST' });
            loadNotifications();
        }
    });

    document.addEventListener('click', function (e) {
        if (!dropdown.contains(e.target) && e.target !== bell) {
            dropdown.classList.add('d-none');
        }
    });

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }

    loadNotifications();
    setInterval(loadNotifications, 15000); // tự cập nhật mỗi 15 giây
});
