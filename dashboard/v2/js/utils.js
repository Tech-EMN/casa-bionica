/* Utils — shared helpers */

const Utils = {
  timeAgo(dateStr) {
    const now = new Date();
    const then = new Date(dateStr);
    const diffMs = now - then;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMs / 3600000);

    if (diffMin < 1) return 'agora';
    if (diffMin < 60) return `${diffMin} min atrás`;
    if (diffHr < 24) return `${diffHr}h atrás`;
    return then.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' });
  },

  formatMinutes(totalMin) {
    if (totalMin < 60) return `${totalMin} min`;
    const hr = Math.floor(totalMin / 60);
    const min = totalMin % 60;
    return min > 0 ? `${hr}h ${min}min` : `${hr}h`;
  },

  slugify(text) {
    return (text || '')
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  },

  getHomeId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('home') || 'home-001';
  },

  getParam(name, fallback) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name) || fallback;
  },

  debounce(fn, ms = 300) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), ms);
    };
  }
};
