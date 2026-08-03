/* Floor Plan JS — renders house grid with sensor dots and elderly profile */

const FloorPlan = {
  emojiMap: {
    'Quarto': '🛏️',
    'Banheiro': '🚿',
    'Cozinha': '🍳',
    'Sala': '📺',
    'Corredor': '🚶',
    'Entrada': '🚪'
  },

  sensorPositions: {
    'sensor-quarto-01': 'quarto-corredor',
    'sensor-banheiro-01': 'banheiro-corredor',
    'sensor-cozinha-01': 'cozinha-corredor',
    'sensor-sala-01': 'sala-corredor',
    'sensor-entrada-01': 'entrada'
  },

  async render(containerId, homeId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = this._template(homeId);
    await this._loadData(homeId);
  },

  async refresh(homeId) {
    await this._loadData(homeId);
  },

  _template(homeId) {
    return `
      <div class="floor-plan">
        <div class="floor-plan__header">
          <h2 class="floor-plan__title">🏠 Casa Biônica</h2>
          <span class="floor-plan__home-selector" id="fp-home-id">${homeId}</span>
        </div>

        <div class="house-grid">
          <div class="room room--quarto" id="room-quarto">
            <span class="sensor-dot sensor-dot--quarto-corredor" id="dot-sensor-quarto-01" title="Sensor Quarto"></span>
            <div class="elderly-profile" id="elderly-profile">
              <div class="elderly-profile__photo" id="elderly-photo">?</div>
              <span class="elderly-profile__name" id="elderly-name">---</span>
              <span class="elderly-profile__age" id="elderly-age"></span>
              <span class="presence-badge presence-badge--unknown" id="presence-badge">⏳</span>
            </div>
            <span class="room__emoji">🛏️</span>
            <span class="room__label">Quarto</span>
            <span class="room__duration" id="dur-quarto"></span>
          </div>

          <div class="room room--banheiro" id="room-banheiro">
            <span class="sensor-dot sensor-dot--banheiro-corredor" id="dot-sensor-banheiro-01" title="Sensor Banheiro"></span>
            <span class="room__emoji">🚿</span>
            <span class="room__label">Banheiro</span>
            <span class="room__duration" id="dur-banheiro"></span>
          </div>

          <div class="room room--cozinha" id="room-cozinha">
            <span class="sensor-dot sensor-dot--cozinha-corredor" id="dot-sensor-cozinha-01" title="Sensor Cozinha"></span>
            <span class="room__emoji">🍳</span>
            <span class="room__label">Cozinha</span>
            <span class="room__duration" id="dur-cozinha"></span>
          </div>

          <div class="room room--sala" id="room-sala">
            <span class="sensor-dot sensor-dot--sala-corredor" id="dot-sensor-sala-01" title="Sensor Sala"></span>
            <span class="room__emoji">📺</span>
            <span class="room__label">Sala</span>
            <span class="room__duration" id="dur-sala"></span>
          </div>

          <div class="room room--corredor">
            <span class="room__label">Corredor</span>
          </div>

          <div class="room room--entrada" id="room-entrada">
            <span class="sensor-dot sensor-dot--entrada" id="dot-sensor-entrada-01" title="Sensor Entrada"></span>
            <span class="room__emoji">🚪</span>
            <span class="room__label">Entrada</span>
            <span class="room__duration" id="dur-entrada"></span>
          </div>
        </div>

        <div class="floor-plan__legend">
          <div class="legend-item"><span class="legend-dot legend-dot--sensor"></span> Sensor ativo</div>
          <div class="legend-item"><span class="legend-dot legend-dot--last"></span> Último movimento</div>
          <div class="legend-item"><span class="legend-dot legend-dot--alert"></span> Alerta</div>
        </div>

        <div class="floor-plan__error" id="fp-error" style="display:none;color:var(--color-danger);margin-top:var(--space-sm);font-size:0.8rem"></div>
      </div>
    `;
  },

  async _loadData(homeId) {
    try {
      const data = await API.get(`/status/${homeId}`);
      this._updateUI(data);
    } catch (e) {
      const errEl = document.getElementById('fp-error');
      if (errEl) {
        errEl.style.display = 'block';
        errEl.textContent = '⚠️ Não foi possível carregar os dados. Verifique a conexão.';
      }
    }
  },

  _updateUI(data) {
    // Elderly profile
    const name = data.elderly_name || '---';
    document.getElementById('elderly-name').textContent = name;
    document.getElementById('elderly-photo').textContent = name.charAt(0).toUpperCase();

    // Presence badge
    const badge = document.getElementById('presence-badge');
    badge.className = 'presence-badge';
    if (data.presence === 'home') {
      badge.classList.add('presence-badge--home');
      badge.textContent = '🟢 Em casa';
    } else if (data.presence === 'away') {
      badge.classList.add('presence-badge--away');
      badge.textContent = '🟡 Fora de casa';
    } else {
      badge.classList.add('presence-badge--unknown');
      badge.textContent = '⏳ Desconhecido';
    }

    // Reset all rooms
    document.querySelectorAll('.room').forEach(r => {
      r.classList.remove('room--active', 'room--alert');
    });
    document.querySelectorAll('.sensor-dot').forEach(d => {
      d.classList.remove('sensor-dot--active', 'sensor-dot--last', 'sensor-dot--alert');
    });

    // Mark active sensors
    (data.devices || []).forEach(dev => {
      if (dev.status === 'active') {
        const dotId = `dot-${dev.sensor_id}`;
        const dot = document.getElementById(dotId);
        if (dot) dot.classList.add('sensor-dot--active');

        // Map sensor to room and mark room active
        const roomName = dev.passage_name;
        const roomId = `room-${this._slugify(roomName)}`;
        const room = document.getElementById(roomId);
        if (room && dev.status === 'active') {
          // Don't mark all rooms active — only the one with last event
        }
      }
    });

    // Last event — highlight sensor + room
    if (data.last_event) {
      const lastSensor = data.last_event.sensor_id;
      const dot = document.getElementById(`dot-${lastSensor}`);
      if (dot) {
        dot.classList.add('sensor-dot--last');

        // Highlight current room
        const passageName = data.last_event.passage_name || this._inferRoom(lastSensor);
        const roomId = `room-${this._slugify(passageName)}`;
        const room = document.getElementById(roomId);
        if (room) room.classList.add('room--active');

        // Update duration display
        RoomTracker.updateDurations(data);
      }
    }

    // Active alerts
    if (data.active_alerts > 0) {
      document.querySelectorAll('.sensor-dot--active').forEach(d => {
        d.classList.add('sensor-dot--alert');
      });
    }

    document.getElementById('fp-home-id').textContent = data.home_id;
  },

  _inferRoom(sensorId) {
    const map = {
      'sensor-quarto-01': 'Quarto',
      'sensor-banheiro-01': 'Banheiro',
      'sensor-cozinha-01': 'Cozinha',
      'sensor-sala-01': 'Sala',
      'sensor-entrada-01': 'Entrada'
    };
    return map[sensorId] || '?';
  },

  _slugify(text) {
    return text.toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }
};

/* Room duration tracker — runs on the same polling interval */
const RoomTracker = {
  updateDurations(statusData) {
    const durations = {};
    // Clear all first
    document.querySelectorAll('.room__duration').forEach(el => {
      el.textContent = '';
      el.className = 'room__duration';
    });

    if (statusData.last_event && statusData.last_event.direction === 'entry') {
      const room = FloorPlan._inferRoom(statusData.last_event.sensor_id);
      const slug = FloorPlan._slugify(room);
      const durEl = document.getElementById(`dur-${slug}`);
      if (durEl) {
        const eventTime = new Date(statusData.last_event.event_timestamp);
        const now = new Date();
        const minutes = Math.floor((now - eventTime) / 60000);
        durEl.textContent = `${minutes} min`;
        durEl.classList.add('room__duration--warning');
      }
    }
  }
};
