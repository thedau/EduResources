/**
 * ================================================================
 * EduResource - Real-time Features (AJAX Polling)
 * 1. Thông báo real-time
 * 4. Live Search
 * 5. Online Users
 * 6. Live Dashboard Stats
 * ================================================================
 */

document.addEventListener("DOMContentLoaded", function () {
  const CONFIG = window.EDURESOURCE_CONFIG || {};

  // ============================================================
  // 1. REAL-TIME NOTIFICATIONS (polling mỗi 15 giây)
  // ============================================================
  if (CONFIG.isAuthenticated) {
    const notifBadge = document.getElementById("notifBadge");
    const notifList = document.getElementById("notificationList");
    const markAllBtn = document.getElementById("markAllReadBtn");

    function fetchNotifications() {
      fetch(CONFIG.urls.notifications)
        .then(function (res) { return res.json(); })
        .then(function (data) {
          // Cập nhật badge số thông báo chưa đọc
          if (data.unread_count > 0) {
            notifBadge.textContent = data.unread_count > 99 ? "99+" : data.unread_count;
            notifBadge.style.display = "inline-block";
          } else {
            notifBadge.style.display = "none";
          }

          // Cập nhật pending badge trên navbar (cho admin)
          if (CONFIG.isAdmin) {
            var pendingBadge = document.getElementById("navPendingBadge");
            if (pendingBadge && data.notifications) {
              var pendingNotifs = data.notifications.filter(function(n) {
                return n.type === "new_pending" && !n.is_read;
              });
              // Đếm pending từ dashboard stats thay vì notifications
            }
          }

          // Render danh sách thông báo
          renderNotifications(data.notifications);
        })
        .catch(function (err) {
          console.warn("Notification fetch error:", err);
        });
    }

    function renderNotifications(notifications) {
      if (!notifications || notifications.length === 0) {
        notifList.innerHTML =
          '<div class="text-center py-4 text-muted">' +
          '<i class="fas fa-bell-slash me-1"></i>Không có thông báo</div>';
        return;
      }

      var html = "";
      notifications.forEach(function (n) {
        var readClass = n.is_read ? "notification-read" : "notification-unread";
        html +=
          '<a href="' + (n.link || "#") + '" ' +
          'class="dropdown-item notification-item ' + readClass + '" ' +
          'data-notif-id="' + n.id + '">' +
          '<div class="d-flex align-items-start py-1">' +
          '<div class="me-2 mt-1"><i class="' + n.icon_class + '"></i></div>' +
          '<div class="flex-grow-1">' +
          '<div class="fw-semibold small">' + n.title + "</div>" +
          '<div class="text-muted small text-truncate" style="max-width: 260px;">' +
          n.message + "</div>" +
          '<div class="text-muted" style="font-size: 0.7rem;">' +
          '<i class="fas fa-clock me-1"></i>' + n.time_ago + "</div>" +
          "</div>" +
          (!n.is_read ? '<div class="ms-1 mt-1"><span class="badge bg-primary rounded-circle p-1" style="width:8px;height:8px;"></span></div>' : "") +
          "</div></a>";
      });
      notifList.innerHTML = html;

      // Click để đánh dấu đã đọc
      notifList.querySelectorAll(".notification-item").forEach(function (item) {
        item.addEventListener("click", function () {
          var id = item.getAttribute("data-notif-id");
          markAsRead(id);
        });
      });
    }

    function markAsRead(id) {
      fetch(CONFIG.urls.notifications.replace("notifications/", "notifications/" + id + "/read/"), {
        method: "POST",
        headers: {
          "X-CSRFToken": CONFIG.csrfToken,
          "Content-Type": "application/json",
        },
      }).catch(function () {});
    }

    // Đánh dấu tất cả đã đọc
    if (markAllBtn) {
      markAllBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        fetch(CONFIG.urls.markAllRead, {
          method: "POST",
          headers: {
            "X-CSRFToken": CONFIG.csrfToken,
            "Content-Type": "application/json",
          },
        })
          .then(function () {
            fetchNotifications();
          })
          .catch(function () {});
      });
    }

    // Fetch lần đầu + polling mỗi 15 giây
    fetchNotifications();
    setInterval(fetchNotifications, 15000);
  }

  // ============================================================
  // 4. LIVE SEARCH (debounced 300ms)
  // ============================================================
  function initLiveSearch(inputId, resultsId) {
    var input = document.getElementById(inputId);
    var results = document.getElementById(resultsId);
    var timer = null;

    if (!input || !results) return;

    input.addEventListener("input", function () {
      clearTimeout(timer);
      var query = input.value.trim();

      if (query.length < 2) {
        results.style.display = "none";
        results.innerHTML = "";
        return;
      }

      timer = setTimeout(function () {
        fetch(CONFIG.urls.liveSearch + "?q=" + encodeURIComponent(query))
          .then(function (res) { return res.json(); })
          .then(function (data) {
            renderSearchResults(data, results);
          })
          .catch(function () {
            results.style.display = "none";
          });
      }, 300);
    });

    // Ẩn dropdown khi click bên ngoài
    document.addEventListener("click", function (e) {
      if (!input.contains(e.target) && !results.contains(e.target)) {
        results.style.display = "none";
      }
    });

    // Enter để tìm kiếm trang đầy đủ
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && inputId === "liveSearchInput") {
        e.preventDefault();
        var query = input.value.trim();
        if (query.length >= 2) {
          window.location.href = CONFIG.urls.resourceDetail + "?q=" + encodeURIComponent(query);
        }
      }
    });
  }

  function renderSearchResults(data, container) {
    if (!data.results || data.results.length === 0) {
      container.innerHTML =
        '<div class="p-3 text-center text-muted small">' +
        '<i class="fas fa-search me-1"></i>Không tìm thấy kết quả cho "' +
        data.query + '"</div>';
      container.style.display = "block";
      return;
    }

    var html = "";
    data.results.forEach(function (r) {
      var typeIcon = {
        document: "fas fa-file-alt",
        video: "fas fa-video",
        presentation: "fas fa-file-powerpoint",
        exercise: "fas fa-pen",
        other: "fas fa-file",
      };
      var icon = typeIcon[r.type_raw] || "fas fa-file";

      html +=
        '<a href="/resources/' + r.slug + '/" class="search-result-item">' +
        '<div class="d-flex align-items-center">' +
        '<div class="search-result-icon me-2"><i class="' + icon + '"></i></div>' +
        '<div class="flex-grow-1">' +
        '<div class="fw-semibold small">' + r.title + "</div>" +
        '<div class="text-muted" style="font-size: 0.75rem;">' +
        '<span class="me-2"><i class="fas fa-folder me-1"></i>' + r.category + "</span>" +
        '<span class="me-2"><i class="fas fa-eye me-1"></i>' + r.view_count + "</span>" +
        (r.rating > 0 ? '<span class="text-warning"><i class="fas fa-star me-1"></i>' + r.rating + "</span>" : "") +
        "</div></div></div></a>";
    });

    // Link xem tất cả
    if (data.total > data.results.length) {
      html +=
        '<a href="' + CONFIG.urls.resourceDetail + "?q=" + encodeURIComponent(data.query) +
        '" class="search-result-item text-center d-block text-primary small fw-bold">' +
        "Xem tất cả " + data.total + " kết quả →</a>";
    }

    container.innerHTML = html;
    container.style.display = "block";
  }

  // Khởi tạo live search cho cả navbar và hero section
  initLiveSearch("liveSearchInput", "liveSearchResults");
  initLiveSearch("heroSearchInput", "heroSearchResults");

  // ============================================================
  // 5. ONLINE USERS (polling mỗi 30 giây)
  // ============================================================
  var onlineCountEl = document.getElementById("onlineCount");

  function fetchOnlineUsers() {
    fetch(CONFIG.urls.onlineUsers)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (onlineCountEl) {
          onlineCountEl.textContent = data.online_count;
        }
        // Cập nhật cả phần ở trang chủ / footer nếu có
        var homeOnline = document.getElementById("homeOnlineCount");
        if (homeOnline) {
          homeOnline.textContent = data.online_count;
        }
      })
      .catch(function () {});
  }

  if (onlineCountEl) {
    fetchOnlineUsers();
    setInterval(fetchOnlineUsers, 30000);
  }

  // ============================================================
  // 6. LIVE DASHBOARD STATS (polling mỗi 30 giây)
  // ============================================================
  var isDashboard = document.getElementById("dashboardStats");

  if (isDashboard && CONFIG.isAdmin) {
    function fetchDashboardStats() {
      fetch(CONFIG.urls.dashboardStats)
        .then(function (res) { return res.json(); })
        .then(function (data) {
          // Cập nhật các thẻ thống kê
          updateStatEl("statTotalResources", data.total_resources);
          updateStatEl("statTotalUsers", data.total_users);
          updateStatEl("statPending", data.pending_resources);
          updateStatEl("statDownloads", data.total_downloads);
          updateStatEl("statApproved", data.approved_resources);
          updateStatEl("statRejected", data.rejected_resources);
          updateStatEl("statViews", data.total_views);
          updateStatEl("statComments", data.total_comments);

          // Cập nhật pending badge trên navbar
          var pendingBadge = document.getElementById("navPendingBadge");
          if (pendingBadge) {
            if (data.pending_resources > 0) {
              pendingBadge.textContent = data.pending_resources;
              pendingBadge.style.display = "inline-block";
            } else {
              pendingBadge.style.display = "none";
            }
          }

          // Cập nhật online users trên dashboard
          updateStatEl("dashOnlineCount", data.online_count);
        })
        .catch(function () {});
    }

    function updateStatEl(id, value) {
      var el = document.getElementById(id);
      if (el) {
        var formatted = (typeof value === "number")
          ? value.toLocaleString("vi-VN")
          : value;
        // Animation nhấp nháy nhẹ khi giá trị thay đổi
        if (el.textContent !== String(formatted)) {
          el.textContent = formatted;
          el.style.transition = "color 0.3s ease";
          el.style.color = "#ffd166";
          setTimeout(function () {
            el.style.color = "";
          }, 600);
        }
      }
    }

    fetchDashboardStats();
    setInterval(fetchDashboardStats, 30000);
  }

  console.log("EduResource Real-time - Loaded ✓");
});
