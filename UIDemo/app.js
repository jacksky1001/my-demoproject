// 视力中心蓝牙数据汇聚系统 - UI 交互逻辑

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initCheckboxes();
  initHoverEffects();
  initStatCardAnimations();
  initRippleEffects();
  initDataRefresh();
});

/* ============================================
   导航切换 - 核心功能
   ============================================ */
function initNavigation() {
  const navItems = document.querySelectorAll('.main-nav .nav-item');
  const allViews = document.querySelectorAll('.page-view');

  // 导航按钮点击
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = item.dataset.view;

      // 切换导航 active
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      // 切换视图显示
      allViews.forEach(v => v.classList.remove('active'));
      const targetView = document.getElementById('view-' + viewName);
      if (targetView) {
        targetView.classList.add('active');
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
        // 为新显示的视图中的统计卡片触发动画
        animateVisibleStats(targetView);
      }
    });
  });

  // 视图内跨页面导航按钮（如"查看全部" -> 历史）
  document.querySelectorAll('.nav-to').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = btn.dataset.view;
      const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
      if (targetNav) {
        targetNav.click();
      }
    });
  });
}

/* ============================================
   复选框交互
   ============================================ */
function initCheckboxes() {
  document.querySelectorAll('.queue-checkbox input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', (e) => {
      const item = e.target.closest('.queue-item');
      if (item) {
        item.style.background = e.target.checked ? 'var(--primary-50)' : '';
      }
      updateQueueBadge();
    });
  });

  // 表格中的全选/单选
  document.querySelectorAll('.data-table thead input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', (e) => {
      const table = e.target.closest('table');
      const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
      checkboxes.forEach(c => { c.checked = e.target.checked; });
    });
  });
}

function updateQueueBadge() {
  const checkedCount = document.querySelectorAll('#view-dashboard .queue-checkbox input:checked, #view-queue .data-table tbody input:checked').length;
  const badge = document.querySelector('.nav-item[data-view="queue"] .badge');
  if (badge) {
    badge.textContent = checkedCount > 0 ? checkedCount : '0';
  }
}

/* ============================================
   统计卡片数字动画
   ============================================ */
function initStatCardAnimations() {
  const activeView = document.querySelector('.page-view.active');
  if (activeView) {
    animateVisibleStats(activeView);
  }
}

function animateVisibleStats(view) {
  const statCards = view.querySelectorAll('.stat-card');
  statCards.forEach(card => {
    const valueEl = card.querySelector('.stat-value');
    if (!valueEl || valueEl.dataset.animated) return;
    valueEl.dataset.animated = 'true';
    animateValue(valueEl);
  });
}

function animateValue(element) {
  const text = element.textContent;
  const numMatch = text.match(/(\d+\.?\d*)/);
  if (!numMatch) return;

  const target = parseFloat(numMatch[1]);
  const prefix = text.substring(0, numMatch.index);
  const suffix = text.substring(numMatch.index + numMatch[1].length);
  const duration = 600;

  let startTime = null;
  function update(currentTime) {
    if (!startTime) startTime = currentTime;
    const progress = Math.min((currentTime - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const showValue = Number.isInteger(target)
      ? Math.round(target * eased)
      : (target * eased).toFixed(1);
    element.textContent = prefix + showValue + suffix;
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  requestAnimationFrame(update);
}

/* ============================================
   悬停效果
   ============================================ */
function initHoverEffects() {
  document.querySelectorAll('.data-table tbody tr').forEach(row => {
    row.addEventListener('click', () => {
      const tbody = row.closest('tbody');
      tbody.querySelectorAll('tr').forEach(r => r.style.background = '');
      row.style.background = 'var(--primary-50)';
    });
  });
}

/* ============================================
   按钮涟漪效果
   ============================================ */
function initRippleEffects() {
  document.querySelectorAll('.btn, .btn-icon, .btn-icon-sm').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.cssText = `
        position:absolute;width:${size}px;height:${size}px;border-radius:50%;
        background:rgba(255,255,255,0.4);left:${e.clientX - rect.left - size/2}px;
        top:${e.clientY - rect.top - size/2}px;transform:scale(0);
        animation:ripple 0.5s ease-out;pointer-events:none;`;
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 500);
    });
  });
}

/* ============================================
   数据刷新
   ============================================ */
function initDataRefresh() {
  const refreshBtn = document.querySelector('.btn-refresh');
  if (!refreshBtn) return;

  refreshBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const originalHTML = refreshBtn.innerHTML;
    refreshBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-icon"><path d="M21 12a9 9 0 1 1-6.2-8.6"/></svg> 刷新中...`;
    refreshBtn.disabled = true;

    setTimeout(() => {
      refreshBtn.innerHTML = originalHTML;
      refreshBtn.disabled = false;
      showToast('数据已刷新', 'success');
    }, 1500);
  });
}

/* ============================================
   Toast 提示
   ============================================ */
function showToast(message, type) {
  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.textContent = message;
  document.body.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('show'));

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// 添加必要的动态样式
const dynStyle = document.createElement('style');
dynStyle.textContent = `
  @keyframes ripple { to { transform: scale(4); opacity: 0; } }
  @keyframes spin { to { transform: rotate(360deg); } }
  .spin-icon { animation: spin 0.8s linear infinite; }
  .toast {
    position: fixed; top: 72px; right: 24px; padding: 12px 20px;
    border-radius: 8px; font-size: 0.9rem; font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000;
    opacity: 0; transform: translateX(50px);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }
  .toast.show { opacity: 1; transform: translateX(0); }
  .toast-success { background: var(--success); color: white; }
  .toast-info { background: var(--primary); color: white; }
  .toast-error { background: var(--danger); color: white; }
  .filter-select {
    padding: 6px 12px; border: 1px solid var(--gray-300);
    border-radius: var(--radius-md); font-family: var(--font-sans);
    font-size: 0.85rem; color: var(--gray-700); background: var(--surface);
    cursor: pointer; outline: none;
  }
  .filter-select:focus { border-color: var(--primary); }
  .pagination {
    display: flex; align-items: center; justify-content: space-between;
    padding-top: var(--space-4); margin-top: var(--space-4);
    border-top: 1px solid var(--gray-100); flex-wrap: wrap; gap: var(--space-3);
  }
  .pagination-info { font-size: 0.85rem; color: var(--gray-600); }
  .pagination-btns { display: flex; align-items: center; gap: var(--space-1); }
`;
document.head.appendChild(dynStyle);

console.log('%c👁️ VisionHub 视力中心蓝牙数据汇聚系统', 'font-size:14px;font-weight:bold;color:#1a73e8;');
console.log('%cUI 原型已加载 - 点击导航栏切换视图', 'font-size:12px;color:#5f6368;');
