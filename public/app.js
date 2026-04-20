const API = '';

function fmt(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

async function checkHealth() {
  const dot  = document.querySelector('.status-dot');
  const text = document.getElementById('status-text');
  try {
    const res = await fetch(`${API}/api/health`);
    if (res.ok) {
      dot.classList.add('online');
      text.textContent = 'Server is online';
    } else {
      throw new Error('non-ok');
    }
  } catch {
    dot.classList.add('offline');
    text.textContent = 'Server offline';
  }
}

async function loadStats() {
  try {
    const res  = await fetch(`${API}/api/stats`);
    const data = await res.json();
    document.querySelectorAll('[data-key]').forEach(el => {
      const val = data[el.dataset.key];
      el.textContent = val !== undefined ? fmt(val) : '—';
    });
  } catch {
    document.querySelectorAll('[data-key]').forEach(el => { el.textContent = '—'; });
  }
}

async function loadFeatures() {
  const grid = document.getElementById('features-grid');
  try {
    const res      = await fetch(`${API}/api/features`);
    const features = await res.json();
    grid.innerHTML = features.map(f => `
      <div class="feature-card">
        <div class="feature-icon">${f.icon}</div>
        <div class="feature-title">${f.title}</div>
        <div class="feature-desc">${f.description}</div>
      </div>
    `).join('');
  } catch {
    grid.innerHTML = '<p style="color:var(--text-muted)">Could not load features.</p>';
  }
}

async function loadTrending() {
  const list = document.getElementById('trending-list');
  try {
    const res   = await fetch(`${API}/api/trending`);
    const items = await res.json();
    list.innerHTML = items.map((item, i) => `
      <div class="trending-item">
        <div class="trending-rank">${String(i + 1).padStart(2, '0')}</div>
        <div class="trending-info">
          <div class="trending-title">${item.title}</div>
          <div class="trending-meta">
            <span>${item.channel}</span>
            <span>${item.views} views</span>
          </div>
        </div>
        <div class="trending-badge">${item.category}</div>
      </div>
    `).join('');
  } catch {
    list.innerHTML = '<p style="color:var(--text-muted)">Could not load trending.</p>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  loadStats();
  loadFeatures();
  loadTrending();
});
