/* Timeline JS — Professional activity feed */

const Timeline = {
  roomIcons: {
    'Quarto':   '<svg viewBox="0 0 16 16"><rect x="2" y="3" width="12" height="10" rx="1.5"/><line x1="2" y1="9.5" x2="14" y2="9.5"/></svg>',
    'Banheiro': '<svg viewBox="0 0 16 16"><path d="M2 8h12M2 8a3 3 0 013-3h1a3 3 0 013 3M2 8v3a1.5 1.5 0 001.5 1.5h1.5M14 8v3a1.5 1.5 0 01-1.5 1.5h-1.5"/></svg>',
    'Cozinha':  '<svg viewBox="0 0 16 16"><rect x="1" y="3" width="14" height="2" rx="1"/><rect x="3" y="7" width="4" height="5" rx="1"/><circle cx="5" cy="9.5" r="1"/></svg>',
    'Sala':     '<svg viewBox="0 0 16 16"><rect x="1" y="4" width="6" height="4" rx="1"/><rect x="9" y="4" width="6" height="8" rx="1"/></svg>',
    'Entrada':  '<svg viewBox="0 0 16 16"><path d="M1 14V7l7-5 7 5v7"/><circle cx="9" cy="10.5" r="1"/></svg>'
  },

  periods: [
    { key: 'madrugada', label: 'Madrugada', start: 0, end: 6 },
    { key: 'manha',     label: 'Manhã',     start: 6, end: 12 },
    { key: 'tarde',     label: 'Tarde',     start: 12, end: 18 },
    { key: 'noite',     label: 'Noite',     start: 18, end: 24 }
  ],

  async render(containerId, homeId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const from = new Date(); from.setHours(0,0,0,0);
    container.innerHTML = `<div class="glass-card timeline-panel" id="timeline-inner"></div>`;
    try {
      const events = await API.get(`/events?home_id=${homeId}&from=${from.toISOString()}&limit=60`);
      this._render(events);
    } catch (e) { this._renderEmpty(); }
  },

  async refresh(homeId) {
    const from = new Date(); from.setHours(0,0,0,0);
    try {
      const events = await API.get(`/events?home_id=${homeId}&from=${from.toISOString()}&limit=60`);
      this._render(events);
    } catch (e) { /* silent */ }
  },

  _render(events) {
    const el = document.getElementById('timeline-inner');
    if (!events || !events.length) {
      el.innerHTML = this._emptyTemplate();
      return;
    }

    const grouped = {}; this.periods.forEach(p => { grouped[p.key] = []; });
    events.forEach(e => {
      const h = new Date(e.event_timestamp).getHours();
      const period = this.periods.find(p => h >= p.start && h < p.end);
      if (period) grouped[period.key].push(e);
    });

    let html = `<div class="timeline-panel__header"><span class="timeline-panel__title">Atividade Hoje</span><span class="timeline-panel__badge">${events.length} eventos</span></div>`;

    this.periods.forEach(period => {
      if (!grouped[period.key].length) return;
      html += `<div class="timeline-period"><div class="timeline-period__label">${period.label}</div>`;
      grouped[period.key].forEach((event, i) => {
        const time = new Date(event.event_timestamp).toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
        const room = event.passage_name || '?';
        const icon = this.roomIcons[room] || '';
        const isEntry = event.direction === 'entry';
        const dirClass = isEntry ? 'timeline-event--entry' : 'timeline-event--exit';
        const dirLabel = isEntry ? 'ENTRADA' : 'SAÍDA';
        const dirBadgeClass = isEntry ? 'timeline-event__direction--entry' : 'timeline-event__direction--exit';
        const isLast = (i === grouped[period.key].length - 1);
        const rowClass = `timeline-event ${dirClass} ${isLast ? 'timeline-event--current' : ''}`;
        const barWidth = Math.min((event.distance_mm / 2000) * 100, 100);

        html += `
          <div class="${rowClass}">
            <span class="timeline-event__time">${time}</span>
            <div class="timeline-event__content">
              <span class="timeline-event__icon">${icon}</span>
              <div>
                <span class="timeline-event__desc">${room}</span>
              </div>
            </div>
            <div class="timeline-event__side">
              <span class="timeline-event__direction ${dirBadgeClass}">${dirLabel}</span>
              <div class="timeline-event__bar"><div class="timeline-event__bar-fill" style="width:${barWidth}%"></div></div>
            </div>
          </div>`;
      });
      html += `</div>`;
    });

    el.innerHTML = html;
  },

  _renderEmpty() {
    document.getElementById('timeline-inner').innerHTML = this._emptyTemplate();
  },

  _emptyTemplate() {
    return `
      <div class="timeline-panel__header"><span class="timeline-panel__title">Atividade Hoje</span></div>
      <div class="timeline-empty">
        <div class="timeline-empty__icon"><svg viewBox="0 0 40 40" stroke="currentColor" fill="none" stroke-width="1.5"><circle cx="20" cy="20" r="15"/><line x1="20" y1="8" x2="20" y2="20"/><line x1="20" y1="20" x2="28" y2="28"/></svg></div>
        <div class="timeline-empty__text">Nenhum evento registrado hoje</div>
      </div>`;
  }
};
