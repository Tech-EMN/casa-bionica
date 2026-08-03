/* Baseline Weekly JS — real vs expected room occupancy */

const Baseline = {
  days: ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sab'],
  dayLabels: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
  todayIndex: new Date().getDay(),

  async render(containerId, homeId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="baseline-weekly">
        <h2 class="baseline-weekly__title">📊 Rotina Semanal</h2>
        <p class="baseline-weekly__subtitle">Tempo de permanência: real vs esperado</p>
        <div class="baseline-room-selector" id="baseline-room-selector"></div>
        <div id="baseline-chart"><div class="baseline-loading">Carregando...</div></div>
        <div class="baseline-summary" id="baseline-summary"></div>
      </div>`;

    try {
      const data = await API.get(`/baseline/${homeId}`);
      this._renderChart(data);
    } catch (e) {
      document.getElementById('baseline-chart').innerHTML = `
        <div class="baseline-loading">
          📡 Baseline ainda não disponível.<br>
          <small style="color:var(--color-muted)">Período de calibração: 7 dias</small>
        </div>`;
    }
  },

  _renderChart(data) {
    const rooms = Object.keys(data.rooms || {});
    if (rooms.length === 0) {
      document.getElementById('baseline-chart').innerHTML =
        '<div class="baseline-loading">Nenhum dado de baseline disponível.</div>';
      return;
    }

    // Room selector
    const selector = document.getElementById('baseline-room-selector');
    selector.innerHTML = rooms.map((r, i) =>
      `<button class="baseline-room-btn ${i === 0 ? 'baseline-room-btn--active' : ''}" data-room="${r}">${r}</button>`
    ).join('');

    selector.querySelectorAll('.baseline-room-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        selector.querySelectorAll('.baseline-room-btn').forEach(b => b.classList.remove('baseline-room-btn--active'));
        btn.classList.add('baseline-room-btn--active');
        this._renderRoom(btn.dataset.room, data);
      });
    });

    this._renderRoom(rooms[0], data);
  },

  _renderRoom(room, data) {
    const roomData = data.rooms[room];
    if (!roomData) return;

    const maxMin = Math.max(...this.days.map(d => {
      const day = roomData[d];
      return Math.max(day?.real_min || 0, day?.baseline_min || 0);
    }), 1);

    const chart = document.getElementById('baseline-chart');
    chart.innerHTML = `
      <div class="baseline-grid">
        ${this.days.map((d, i) => {
          const day = roomData[d] || {};
          const realPct = Math.min(((day.real_min || 0) / maxMin) * 100, 100);
          const basePct = Math.min(((day.baseline_min || 0) / maxMin) * 100, 100);
          const dev = day.deviation || 0;
          const isToday = i === this.todayIndex;

          let devClass = 'normal';
          let devLabel = 'Normal';
          if (dev > 2) { devClass = 'critical'; devLabel = '⚠ Crítico'; }
          else if (dev > 1) { devClass = 'warning'; devLabel = '⚠ Acima'; }

          return `
            <div class="baseline-day">
              <div class="baseline-day__label ${isToday ? 'baseline-day__label--today' : ''}">
                ${this.dayLabels[i]}${isToday ? ' •' : ''}
              </div>
              <div class="baseline-bars">
                <div class="baseline-bar baseline-bar--real" style="height:${realPct}px" title="Real: ${day.real_min || 0} min"></div>
                <div class="baseline-bar baseline-bar--baseline" style="height:${basePct}px" title="Baseline: ${day.baseline_min || 0} min"></div>
                <span class="baseline-bar__value">${day.real_min || 0}m</span>
              </div>
              ${dev > 0.5 ? `<span class="baseline-deviation baseline-deviation--${devClass}">${devLabel}</span>` : ''}
            </div>`;
        }).join('')}
      </div>`;

    // Summary
    const summary = document.getElementById('baseline-summary');
    const hasAnomalies = data.anomalies_today?.some(a => a.room === room);
    if (hasAnomalies) {
      summary.className = 'baseline-summary baseline-summary--warn';
      summary.textContent = '⚠️ Desvios detectados hoje — verifique a timeline.';
    } else {
      summary.className = 'baseline-summary baseline-summary--ok';
      summary.textContent = '✅ Sem desvios significativos nesta semana.';
    }
  }
};
