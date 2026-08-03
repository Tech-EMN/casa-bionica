/* Narrative Timeline — "O dia da Dona Cida" as a visual story */

const Timeline = {
  emojiMap: {
    'Quarto': '🛏️',
    'Banheiro': '🚿',
    'Cozinha': '🍳',
    'Sala': '📺',
    'Corredor': '🚶',
    'Entrada': '🚪'
  },

  sections: [
    { key: 'madrugada', label: 'Madrugada', hourStart: 0, hourEnd: 6 },
    { key: 'manha',     label: 'Manhã',     hourStart: 6, hourEnd: 12 },
    { key: 'tarde',     label: 'Tarde',     hourStart: 12, hourEnd: 18 },
    { key: 'noite',     label: 'Noite',     hourStart: 18, hourEnd: 24 }
  ],

  async render(containerId, homeId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const from = new Date();
    from.setHours(0, 0, 0, 0);

    container.innerHTML = this._template();

    try {
      const events = await API.get(`/events?home_id=${homeId}&from=${from.toISOString()}&limit=100`);
      this._populate(events);
    } catch (e) {
      document.getElementById('timeline-content').innerHTML = `
        <div class="timeline-empty">
          <span class="timeline-empty__emoji">📡</span>
          Não foi possível carregar os eventos.
        </div>`;
    }
  },

  async refresh(homeId) {
    const from = new Date();
    from.setHours(0, 0, 0, 0);
    try {
      const events = await API.get(`/events?home_id=${homeId}&from=${from.toISOString()}&limit=100`);
      this._populate(events);
    } catch (e) { /* silently fail on refresh */ }
  },

  _template() {
    let html = `
      <div class="narrative-timeline">
        <h2 class="narrative-timeline__title">📖 O dia <em id="timeline-elderly">de hoje</em></h2>
        <div id="timeline-content">`;

    this.sections.forEach(sec => {
      html += `
        <div class="timeline-section" id="timeline-${sec.key}">
          <div class="timeline-section__header">${sec.label}</div>
          <div id="timeline-${sec.key}-events"></div>
        </div>`;
    });

    html += `</div></div>`;
    return html;
  },

  _populate(events) {
    if (!events || events.length === 0) {
      document.getElementById('timeline-content').innerHTML = `
        <div class="timeline-empty">
          <span class="timeline-empty__emoji">🌙</span>
          Nenhum evento registrado hoje ainda.
        </div>`;
      return;
    }

    // Group by section
    const grouped = {};
    this.sections.forEach(s => { grouped[s.key] = []; });

    events.forEach(e => {
      const hour = new Date(e.event_timestamp).getHours();
      const section = this.sections.find(s => hour >= s.hourStart && hour < s.hourEnd);
      if (section) grouped[section.key].push(e);
    });

    // Render each section
    this.sections.forEach(sec => {
      const el = document.getElementById(`timeline-${sec.key}-events`);
      if (!el) return;

      if (grouped[sec.key].length === 0) {
        el.innerHTML = '<div style="color:var(--color-muted);font-size:0.8rem;padding:var(--space-xs) 0">—</div>';
        return;
      }

      el.innerHTML = grouped[sec.key].map((event, i) => {
        const time = new Date(event.event_timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        const room = event.passage_name || '?';
        const emoji = this.emojiMap[room] || '📍';
        const dir = event.direction === 'entry' ? 'Entrou' : 'Saiu';
        const desc = `${dir}: ${room}`;
        const isLast = (i === grouped[sec.key].length - 1 && sec.key === this._lastNonEmptySection(grouped));
        const cssClass = isLast ? 'timeline-event timeline-event--current' : 'timeline-event';

        return `
          <div class="${cssClass}">
            <span class="timeline-event__time">${time}</span>
            <span class="timeline-event__emoji">${emoji}</span>
            <span class="timeline-event__desc">${desc}</span>
            <span class="timeline-event__duration">${event.direction === 'entry' ? '▶ Entrada' : '◀ Saída'}</span>
            <span class="timeline-event__indicator indicator--normal">✅</span>
          </div>`;
      }).join('');
    });

    // Hide empty sections
    this.sections.forEach(sec => {
      const sectionEl = document.getElementById(`timeline-${sec.key}`);
      if (sectionEl && grouped[sec.key].length === 0) {
        sectionEl.style.display = 'none';
      } else if (sectionEl) {
        sectionEl.style.display = 'block';
      }
    });
  },

  setElderlyName(name) {
    const el = document.getElementById('timeline-elderly');
    if (el) el.textContent = name ? `da ${name}` : 'de hoje';
  },

  _lastNonEmptySection(grouped) {
    for (let i = this.sections.length - 1; i >= 0; i--) {
      if (grouped[this.sections[i].key].length > 0) return this.sections[i].key;
    }
    return null;
  }
};
