/**
 * ================================================================
 * EduResource - JavaScript
 * Thư viện tài liệu học tập trực tuyến
 * ================================================================
 */

document.addEventListener('DOMContentLoaded', function () {

    // === Tự động ẩn thông báo sau 5 giây ===
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // === Xác nhận trước khi xóa ===
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.getAttribute('data-confirm') || 'Bạn có chắc chắn muốn thực hiện hành động này?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // === Hiệu ứng đếm số cho thống kê ===
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.5,
        };

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-target')) || parseInt(counter.textContent) || 0;
                    animateCounter(counter, target);
                    observer.unobserve(counter);
                }
            });
        }, observerOptions);

        counters.forEach(function (counter) {
            observer.observe(counter);
        });
    }

    function animateCounter(element, target) {
        let current = 0;
        const increment = target / 50;
        const duration = 1500;
        const stepTime = duration / 50;

        const timer = setInterval(function () {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString('vi-VN');
        }, stepTime);
    }

    // === Preview ảnh trước khi upload ===
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function (input) {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                // Kiểm tra kích thước (10MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('Kích thước tệp vượt quá 10MB.');
                    input.value = '';
                    return;
                }

                // Kiểm tra định dạng
                const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Định dạng ảnh không được hỗ trợ. Cho phép: JPG, PNG, GIF, WEBP');
                    input.value = '';
                    return;
                }
            }
        });
    });

    // === Kiểm tra tệp upload ===
    const fileInputs = document.querySelectorAll('input[type="file"][accept*=".pdf"]');
    fileInputs.forEach(function (input) {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 10 * 1024 * 1024) {
                    alert('Kích thước tệp vượt quá 10MB.');
                    input.value = '';
                    return;
                }
            }
        });
    });

    // === Active nav link dựa trên URL hiện tại ===
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('#mainNav .nav-link');
    navLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });

    // === Smooth scroll cho anchor links ===
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // === Tooltip Bootstrap ===
    const tooltipTriggerList = document.querySelectorAll('[title]');
    tooltipTriggerList.forEach(function (el) {
        if (el.closest('.modal') === null) {
            // Không áp dụng tooltip trong modal
            new bootstrap.Tooltip(el, { trigger: 'hover' });
        }
    });

    console.log('EduResource - Tải hoàn tất ✓');
});
