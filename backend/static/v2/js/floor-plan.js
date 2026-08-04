/* Floor Plan JS — Professional health-tech monitoring */

const FloorPlan = {
  roomIcons: {
    'Quarto':   '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="14" rx="2"/><line x1="3" y1="14" x2="21" y2="14"/><rect x="7" y="6" width="10" height="4" rx="0.5"/></svg>',
    'Banheiro': '<svg viewBox="0 0 24 24"><path d="M4 12h16M4 12a4 4 0 014-4h2a4 4 0 014 4M4 12v4a2 2 0 002 2h2M20 12v4a2 2 0 01-2 2h-2"/></svg>',
    'Cozinha':  '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="2" rx="1"/><rect x="5" y="9" width="5" height="6" rx="1"/><circle cx="7.5" cy="12" r="1.5"/></svg>',
    'Sala':     '<svg viewBox="0 0 24 24"><rect x="2" y="7" width="7" height="5" rx="1"/><rect x="12" y="7" width="10" height="9" rx="1"/><path d="M20 8v7"/></svg>',
    'Entrada':  '<svg viewBox="0 0 24 24"><path d="M3 21V10l9-7 9 7v11"/><circle cx="14" cy="15" r="1.5"/></svg>'
  },

  async render(containerId, homeId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = this._template(homeId);
    await this._loadData(homeId);
  },

  async refresh(homeId) { await this._loadData(homeId); },

  _template(homeId) {
    return `
      <div class="glass-card floor-plan">
        <div class="floor-plan__header">
          <div class="floor-plan__title-group">
            <h2>Planta da Residência</h2>
            <p>Monitoramento em tempo real</p>
          </div>
          <span class="floor-plan__home-selector" id="fp-home-id">${homeId}</span>
        </div>

        <!-- Elderly Card -->
        <div class="elderly-card" id="elderly-card">
          <div class="elderly-card__avatar" id="elderly-avatar">?</div>
          <div class="elderly-card__info">
            <div class="elderly-card__name" id="elderly-name">---</div>
            <div class="elderly-card__meta" id="elderly-meta"></div>
          </div>
          <div class="elderly-card__metrics">
            <div class="elderly-metric">
              <div class="elderly-metric__value" id="metric-events">0</div>
              <div class="elderly-metric__label">Eventos hoje</div>
            </div>
            <div class="elderly-metric">
              <div class="elderly-metric__value" id="metric-alerts">0</div>
              <div class="elderly-metric__label">Alertas</div>
            </div>
            <div class="elderly-metric">
              <span class="status-badge status-badge--ok" id="presence-badge">Em casa</span>
            </div>
          </div>
        </div>

        <!-- House Grid -->
        <div class="house-grid">
          <div class="room room--quarto" id="room-quarto">
            <span class="sensor-dot sensor-dot--quarto-hall" id="dot-sensor-quarto-01"></span>
            <div class="room__header"><span class="room__icon">${this.roomIcons['Quarto']}</span><span class="room__label">Quarto</span></div>
            <div class="room__body"><span class="room__status" id="status-quarto">--</span><span class="room__duration" id="dur-quarto"></span></div>
          </div>
          <div class="room room--bathroom" id="room-bathroom">
            <span class="sensor-dot sensor-dot--bath-hall" id="dot-sensor-banheiro-01"></span>
            <div class="room__header"><span class="room__icon">${this.roomIcons['Banheiro']}</span><span class="room__label">Banheiro</span></div>
            <div class="room__body"><span class="room__status" id="status-bathroom">--</span><span class="room__duration" id="dur-bathroom"></span></div>
          </div>
          <div class="room room--kitchen" id="room-kitchen">
            <span class="sensor-dot sensor-dot--kitchen-hall" id="dot-sensor-cozinha-01"></span>
            <div class="room__header"><span class="room__icon">${this.roomIcons['Cozinha']}</span><span class="room__label">Cozinha</span></div>
            <div class="room__body"><span class="room__status" id="status-kitchen">--</span><span class="room__duration" id="dur-kitchen"></span></div>
          </div>
          <div class="room room--living" id="room-living">
            <span class="sensor-dot sensor-dot--living-hall" id="dot-sensor-sala-01"></span>
            <div class="room__header"><span class="room__icon">${this.roomIcons['Sala']}</span><span class="room__label">Sala</span></div>
            <div class="room__body"><span class="room__status" id="status-living">--</span><span class="room__duration" id="dur-living"></span></div>
          </div>
          <div class="room room--hallway"></div>
          <div class="room room--entrance" id="room-entrance">
            <span class="sensor-dot sensor-dot--entrance" id="dot-sensor-entrada-01"></span>
            <div class="room__header"><span class="room__icon">${this.roomIcons['Entrada']}</span><span class="room__label">Entrada</span></div>
            <div class="room__body"><span class="room__status" id="status-entrance">--</span><span class="room__duration" id="dur-entrance"></span></div>
          </div>
        </div>

        <div class="floor-plan__error" id="fp-error">Não foi possível carregar os dados.</div>
      </div>`;
  },

  async _loadData(homeId) {
    try {
      const data = await API.get(`/status/${homeId}`);
      this._updateUI(data);
    } catch (e) {
      const el = document.getElementById('fp-error');
      if (el) { el.style.display = 'block'; }
    }
  },

  _updateUI(data) {
    const name = data.elderly_name || '---';
    document.getElementById('elderly-name').textContent = name;
    document.getElementById('elderly-avatar').textContent = name.charAt(0).toUpperCase();
    document.getElementById('elderly-meta').textContent = 'Monitoramento ativo';
    document.getElementById('metric-alerts').textContent = data.active_alerts || 0;

    // Presence badge
    const badge = document.getElementById('presence-badge');
    badge.className = 'status-badge';
    if (data.presence === 'home') { badge.classList.add('status-badge--ok'); badge.textContent = 'Em casa'; }
    else if (data.presence === 'away') { badge.classList.add('status-badge--warning'); badge.textContent = 'Fora'; }
    else { badge.classList.add('status-badge--info'); badge.textContent = '--'; }

    // Reset rooms
    document.querySelectorAll('.room').forEach(r => r.classList.remove('room--active', 'room--alert'));
    document.querySelectorAll('.sensor-dot').forEach(d => d.classList.remove('sensor-dot--active', 'sensor-dot--last', 'sensor-dot--alert'));

    // Mark active devices
    (data.devices || []).forEach(dev => {
      if (dev.status === 'active') {
        const slug = dev.passage_name?.toLowerCase().normalize('NFD').replace(/[^a-z]/g,'') || '';
        document.getElementById(`dot-${dev.sensor_id}`)?.classList.add('sensor-dot--active');
        document.getElementById(`status-${slug}`)?.textContent = 'Ativo';
      }
    });

    // Last event highlight
    if (data.last_event) {
      const dot = document.getElementById(`dot-${data.last_event.sensor_id}`);
      if (dot) {
        dot.classList.add('sensor-dot--last');
        const roomSlug = (data.last_event.passage_name || '').toLowerCase().normalize('NFD').replace(/[^a-z]/g,'');
        document.getElementById(`room-${roomSlug}`)?.classList.add('room--active');
      }
    }

    // Alerts
    if (data.active_alerts > 0) {
      document.querySelectorAll('.sensor-dot--active').forEach(d => d.classList.add('sensor-dot--alert'));
    }

    document.getElementById('fp-home-id').textContent = data.home_id;
    document.getElementById('fp-error').style.display = 'none';
  }
};
