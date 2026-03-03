/**
 * ================================================================
 * EduResource - JavaScript
 * Thư viện tài liệu học tập trực tuyến
 * ================================================================
 */

document.addEventListener("DOMContentLoaded", function () {
  // === Tự động ẩn thông báo sau 5 giây ===
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // === Xác nhận trước khi xóa ===
  const deleteForms = document.querySelectorAll("form[data-confirm]");
  deleteForms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const message =
        form.getAttribute("data-confirm") ||
        "Bạn có chắc chắn muốn thực hiện hành động này?";
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // === Hiệu ứng đếm số cho thống kê ===
  const counters = document.querySelectorAll(".counter");
  if (counters.length > 0) {
    const observerOptions = {
      root: null,
      rootMargin: "0px",
      threshold: 0.5,
    };

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const counter = entry.target;
          const target =
            parseInt(counter.getAttribute("data-target")) ||
            parseInt(counter.textContent) ||
            0;
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
      element.textContent = Math.floor(current).toLocaleString("vi-VN");
    }, stepTime);
  }

  // === Preview ảnh trước khi upload ===
  const imageInputs = document.querySelectorAll(
    'input[type="file"][accept*="image"]',
  );
  imageInputs.forEach(function (input) {
    input.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        // Kiểm tra kích thước (10MB)
        if (file.size > 10 * 1024 * 1024) {
          alert("Kích thước tệp vượt quá 10MB.");
          input.value = "";
          return;
        }

        // Kiểm tra định dạng
        const allowedTypes = [
          "image/jpeg",
          "image/png",
          "image/gif",
          "image/webp",
        ];
        if (!allowedTypes.includes(file.type)) {
          alert(
            "Định dạng ảnh không được hỗ trợ. Cho phép: JPG, PNG, GIF, WEBP",
          );
          input.value = "";
          return;
        }
      }
    });
  });

  // === Kiểm tra tệp upload ===
  const fileInputs = document.querySelectorAll(
    'input[type="file"][accept*=".pdf"]',
  );
  fileInputs.forEach(function (input) {
    input.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        if (file.size > 10 * 1024 * 1024) {
          alert("Kích thước tệp vượt quá 10MB.");
          input.value = "";
          return;
        }
      }
    });
  });

  // === Active nav link dựa trên URL hiện tại ===
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll("#mainNav .nav-link");
  navLinks.forEach(function (link) {
    const href = link.getAttribute("href");
    if (href && href !== "/" && currentPath.startsWith(href)) {
      link.classList.add("active");
    } else if (href === "/" && currentPath === "/") {
      link.classList.add("active");
    }
  });

  // === Smooth scroll cho anchor links ===
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (targetId && targetId !== "#") {
        e.preventDefault();
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  });

  // === Loading States cho Forms (chống double-submit) ===
  const submitButtons = document.querySelectorAll(".btn-submit, form button[type='submit']");
  submitButtons.forEach(function (btn) {
    const form = btn.closest("form");
    if (!form || form.hasAttribute("data-no-loading")) return;

    form.addEventListener("submit", function (e) {
      // Không áp dụng cho forms có data-confirm (đã có confirm dialog)
      if (form.hasAttribute("data-confirm")) return;

      // Tránh double submit
      if (form.dataset.submitting === "true") {
        e.preventDefault();
        return;
      }
      form.dataset.submitting = "true";

      // Lưu nội dung gốc và hiển thị loading
      const originalHTML = btn.innerHTML;
      const originalWidth = btn.offsetWidth;
      btn.style.minWidth = originalWidth + "px";
      btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang xử lý...';
      btn.disabled = true;
      btn.classList.add("btn-loading");

      // Timeout an toàn: khôi phục sau 15 giây nếu form bị kẹt
      setTimeout(function () {
        if (form.dataset.submitting === "true") {
          btn.innerHTML = originalHTML;
          btn.disabled = false;
          btn.classList.remove("btn-loading");
          btn.style.minWidth = "";
          form.dataset.submitting = "false";
        }
      }, 15000);
    });
  });

  // === Tooltip Bootstrap ===
  const tooltipTriggerList = document.querySelectorAll("[title]");
  tooltipTriggerList.forEach(function (el) {
    if (el.closest(".modal") === null) {
      // Không áp dụng tooltip trong modal
      new bootstrap.Tooltip(el, { trigger: "hover" });
    }
  });

  // === Scroll Reveal Animation ===
  const revealElements = document.querySelectorAll(
    ".reveal, .reveal-left, .reveal-right, .reveal-scale",
  );

  if (revealElements.length > 0) {
    // Kiểm tra prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    if (prefersReducedMotion) {
      // Bỏ qua animation nếu người dùng tắt hiệu ứng
      revealElements.forEach(function (el) {
        el.classList.add("revealed");
      });
    } else {
      const revealObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("revealed");

              // Nếu có stagger children, reveal chúng
              if (entry.target.classList.contains("reveal-stagger")) {
                const children = entry.target.children;
                for (let i = 0; i < children.length; i++) {
                  children[i].classList.add("revealed");
                }
              }

              revealObserver.unobserve(entry.target);
            }
          });
        },
        { root: null, rootMargin: "0px 0px -60px 0px", threshold: 0.1 },
      );

      revealElements.forEach(function (el) {
        revealObserver.observe(el);
      });
    }
  }

  // === Tilt effect nhẹ cho resource-card (chỉ desktop) ===
  if (window.innerWidth > 768) {
    const tiltCards = document.querySelectorAll(".resource-card");
    tiltCards.forEach(function (card) {
      card.addEventListener("mousemove", function (e) {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -3;
        const rotateY = ((x - centerX) / centerX) * 3;

        card.style.transform =
          "translateY(-8px) perspective(800px) rotateX(" +
          rotateX +
          "deg) rotateY(" +
          rotateY +
          "deg)";
      });

      card.addEventListener("mouseleave", function () {
        card.style.transform = "";
      });
    });
  }

  // === Theme Toggle (Sáng / Tối) ===
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    // Áp dụng theme đã lưu (chạy sớm trong <html> để tránh flash)
    const savedTheme = localStorage.getItem('eduresource-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('eduresource-theme', next);
    });
  }

  console.log("EduResource - Tải hoàn tất ✓");

  // ================================================================
  //  FLOATING CHATBOT WIDGET
  // ================================================================
  const chatbotWidget = document.getElementById('chatbotWidget');
  if (chatbotWidget) {
    const toggle = document.getElementById('chatbotToggle');
    const window_ = document.getElementById('chatbotWindow');
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSend');
    const messagesEl = document.getElementById('chatbotMessages');
    const suggestionsEl = document.getElementById('chatbotSuggestions');
    const clearBtn = document.getElementById('chatbotClear');
    const minimizeBtn = document.getElementById('chatbotMinimize');
    const iconOpen = toggle.querySelector('.chatbot-icon-open');
    const iconClose = toggle.querySelector('.chatbot-icon-close');

    let chatHistory = [];
    let isSending = false;

    // --- Toggle open / close ---
    function openChat() {
      chatbotWidget.classList.add('open');
      window_.style.display = 'flex';
      iconOpen.style.display = 'none';
      iconClose.style.display = 'inline';
      setTimeout(function () { input.focus(); }, 100);
    }

    function closeChat() {
      chatbotWidget.classList.remove('open');
      window_.style.display = 'none';
      iconOpen.style.display = 'inline';
      iconClose.style.display = 'none';
    }

    toggle.addEventListener('click', function () {
      if (chatbotWidget.classList.contains('open')) {
        closeChat();
      } else {
        openChat();
      }
    });

    minimizeBtn.addEventListener('click', closeChat);

    // --- Send message ---
    function appendMessage(role, html) {
      var div = document.createElement('div');
      div.className = 'chatbot-msg chatbot-msg-' + role;
      var icon = role === 'bot' ? 'fa-robot' : 'fa-user';
      div.innerHTML =
        '<div class="chatbot-msg-avatar"><i class="fas ' + icon + '"></i></div>' +
        '<div class="chatbot-msg-content">' + html + '</div>';
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping() {
      var div = document.createElement('div');
      div.className = 'chatbot-msg chatbot-msg-bot';
      div.id = 'chatbotTyping';
      div.innerHTML =
        '<div class="chatbot-msg-avatar"><i class="fas fa-robot"></i></div>' +
        '<div class="chatbot-msg-content"><div class="chatbot-typing"><span></span><span></span><span></span></div></div>';
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function removeTyping() {
      var el = document.getElementById('chatbotTyping');
      if (el) el.remove();
    }

    function escapeHtml(text) {
      var d = document.createElement('div');
      d.textContent = text;
      return d.innerHTML;
    }

    function formatBotResponse(text) {
      // Simple markdown-like formatting
      var html = escapeHtml(text);
      // Bold **text**
      html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      // Bullet lists
      html = html.replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>');
      if (html.includes('<li>')) {
        html = html.replace(/(<li>.*?<\/li>(\s*)?)+/gs, function (match) {
          return '<ul class="mb-1 mt-1 ps-3">' + match + '</ul>';
        });
      }
      // Line breaks
      html = html.replace(/\n/g, '<br>');
      return html;
    }

    async function sendMessage(text) {
      if (isSending || !text.trim()) return;

      var userText = text.trim();
      isSending = true;
      sendBtn.disabled = true;
      input.value = '';

      // Hide suggestions after first user message
      suggestionsEl.style.display = 'none';

      // Show user message
      appendMessage('user', escapeHtml(userText));

      // Add to history
      chatHistory.push({ role: 'user', content: userText });

      // Show typing
      showTyping();

      try {
        var config = window.EDURESOURCE_CONFIG || {};
        var url = (config.urls && config.urls.aiGeneralChat) || '/api/ai/general-chat/';
        var csrf = config.csrfToken || '';

        var response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({
            message: userText,
            history: chatHistory.slice(-10) // Send last 10 messages for context
          })
        });

        removeTyping();

        if (response.ok) {
          var data = await response.json();
          var botReply = data.reply || data.response || 'Xin lỗi, tôi không thể trả lời lúc này.';
          chatHistory.push({ role: 'assistant', content: botReply });
          appendMessage('bot', formatBotResponse(botReply));
        } else if (response.status === 429) {
          appendMessage('bot', '⚠️ Bạn đã gửi quá nhiều tin nhắn. Vui lòng chờ một chút rồi thử lại.');
        } else {
          appendMessage('bot', '❌ Đã xảy ra lỗi. Vui lòng thử lại sau.');
        }
      } catch (err) {
        removeTyping();
        appendMessage('bot', '❌ Không thể kết nối đến server. Vui lòng thử lại.');
        console.error('Chatbot error:', err);
      }

      isSending = false;
      sendBtn.disabled = false;
      input.focus();
    }

    sendBtn.addEventListener('click', function () {
      sendMessage(input.value);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input.value);
      }
    });

    // --- Suggestion buttons ---
    suggestionsEl.addEventListener('click', function (e) {
      var btn = e.target.closest('.chatbot-suggestion-btn');
      if (btn) {
        var msg = btn.getAttribute('data-msg');
        if (msg) sendMessage(msg);
      }
    });

    // --- Clear history ---
    clearBtn.addEventListener('click', function () {
      chatHistory = [];
      // Keep only the welcome message (first child)
      while (messagesEl.children.length > 1) {
        messagesEl.removeChild(messagesEl.lastChild);
      }
      suggestionsEl.style.display = 'flex';
    });
  }
});
