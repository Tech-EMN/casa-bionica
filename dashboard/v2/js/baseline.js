/* Baseline JS — Activity rings per room (health-tech standard) */

const Baseline = {
  days: ['dom','seg','ter','qua','qui','sex','sab'],
  dayLabels: ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'],
  todayIndex: new Date().getDay(),

  async render(containerId, homeId) {
    const c = document.getElementById(containerId);
    if (!c) return;
    c.innerHTML = `<div class="glass-card baseline-panel" id="baseline-inner"></div>`;
    try {
      const data = await API.get(`/baseline/${homeId}`);
      this._render(data);
    } catch (e) { this._renderCalibrating(); }
  },

  _render(data) {
    const rooms = Object.keys(data.rooms || {});
    if (!rooms.length) { this._renderCalibrating(); return; }

    const el = document.getElementById('baseline-inner');
    let html = `
      <div class="baseline-panel__header"><span class="baseline-panel__title">Rotina Semanal</span><span class="baseline-panel__period">${data.window_days || 7} dias</span></div>
      <div class="baseline-rooms" id="baseline-rooms">${rooms.map((r,i) => `<button class="baseline-room-pill ${i===0?'baseline-room-pill--active':''}" data-room="${r}">${r}</button>`).join('')}</div>
      <div id="baseline-chart"></div>
      <div class="baseline-summary baseline-summary--ok" id="baseline-summary">✅ Sem desvios significativos</div>
    `;
    el.innerHTML = html;

    // Bind room selector
    el.querySelectorAll('.baseline-room-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        el.querySelectorAll('.baseline-room-pill').forEach(b => b.classList.remove('baseline-room-pill--active'));
        btn.classList.add('baseline-room-pill--active');
        this._renderRoom(btn.dataset.room, data);
      });
    });

    this._renderRoom(rooms[0], data);
  },

  _renderRoom(room, data) {
    const roomData = data.rooms[room];
    if (!roomData) return;

    const maxMin = Math.max(...this.days.map(d => roomData[d]?.real_min || roomData[d]?.baseline_min || 0), 1);
    const R = 18, C = 2*Math.PI*R, strokeW = 4;

    document.getElementById('baseline-chart').innerHTML = `
      <div class="baseline-grid">
        ${this.days.map((d, i) => {
          const day = roomData[d] || {};
          const real = day.real_min || 0;
          const base = day.baseline_min || 0;
          const pct = Math.min(real / Math.max(maxMin, 1), 1);
          const offset = C * (1 - pct);
          const dev = day.deviation || 0;
          const ringClass = dev > 1 ? (dev > 2 ? 'baseline-ring--danger' : 'baseline-ring--warning') : '';
          const isToday = i === this.todayIndex;

          return `
            <div class="baseline-day">
              <div class="baseline-day__label ${isToday ? 'baseline-day__label--today' : ''}">${this.dayLabels[i]}</div>
              <div class="baseline-ring ${ringClass}">
                <svg width="44" height="44" viewBox="0 0 44 44">
                  <circle class="baseline-ring__bg" cx="22" cy="22" r="${R}"/>
                  <circle class="baseline-ring__fill" cx="22" cy="22" r="${R}" stroke-dasharray="${C}" stroke-dashoffset="${offset}"/>
                </svg>
                <div class="baseline-ring__center">
                  <span class="baseline-ring__value">${real}</span>
                  <span class="baseline-ring__unit">min</span>
                </div>
              </div>
            </div>`;
        }).join('')}
      </div>`;

    // Check anomalies
    const anomalies = (data.anomalies_today || []).filter(a => a.passage_name === room);
    const summary = document.getElementById('baseline-summary');
    if (anomalies.length) {
      summary.className = 'baseline-summary baseline-summary--warn';
      summary.textContent = `⚠️ ${anomalies.length} desvio${anomalies.length>1?'s':''} detectado${anomalies.length>1?'s':''} hoje`;
    } else {
      summary.className = 'baseline-summary baseline-summary--ok';
      summary.textContent = '✅ Sem desvios significativos';
    }
  },

  _renderCalibrating() {
    document.getElementById('baseline-inner').innerHTML = `
      <div class="baseline-panel__header"><span class="baseline-panel__title">Rotina Semanal</span></div>
      <div class="timeline-empty">
        <div class="timeline-empty__icon"><svg viewBox="0 0 40 40" stroke="currentColor" fill="none" stroke-width="1.5"><circle cx="20" cy="20" r="15"/><polyline points="12,20 18,14 20,20 28,20"/></svg></div>
        <div class="timeline-empty__text">Período de calibração — 7 dias</div>
      </div>`;
  }
};
