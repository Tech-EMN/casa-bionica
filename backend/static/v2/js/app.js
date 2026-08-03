/* App Shell — router, state, init */

const App = {
  state: {
    homeId: 'home-001',
    elderlyName: ''
  },

  async init() {
    this.state.homeId = Utils.getHomeId();

    // Render shell
    this._renderShell();

    // Health check
    const healthy = await API.healthCheck();
    if (!healthy) {
      document.getElementById('app-error').classList.add('app-error-banner--visible');
      document.getElementById('app-error').textContent =
        '⚠️ Não foi possível conectar ao servidor. Verifique sua conexão.';
      return;
    }

    // Load all components
    await Promise.all([
      FloorPlan.render('floor-plan-container', this.state.homeId),
      Timeline.render('timeline-container', this.state.homeId),
      CareNetwork.render('care-network-container', this.state.homeId),
      this._loadBaseline()
    ]);

    // Set elderly name in timeline
    try {
      const data = await API.get(`/status/${this.state.homeId}`);
      this.state.elderlyName = data.elderly_name || '';
      Timeline.setElderlyName(this.state.elderlyName);
      document.getElementById('app-elderly-name').textContent =
        this.state.elderlyName || 'Casa Biônica';
    } catch (e) { /* silent */ }

    // Start polling
    this._startPolling();

    // Hide loading
    document.getElementById('app-loading').style.display = 'none';
    document.getElementById('app-content').style.display = 'block';
  },

  async _loadBaseline() {
    try {
      await Baseline.render('baseline-container', this.state.homeId);
    } catch (e) {
      // Baseline might not exist yet — graceful degradation
      document.getElementById('baseline-container').innerHTML = `
        <div class="baseline-weekly">
          <h2 class="baseline-weekly__title">📊 Rotina Semanal</h2>
          <p class="baseline-weekly__subtitle" style="color:var(--color-muted);padding:var(--space-lg)">
            📡 Baseline em calibração — disponível após 7 dias de uso.
          </p>
        </div>`;
    }
  },

  _renderShell() {
    const root = document.getElementById('app-root');
    root.innerHTML = `
      <div class="app-container">
        <header class="app-header">
          <h1 class="app-header__logo" id="app-elderly-name">🌿 Casa Biônica</h1>
          <div class="app-header__actions">
            <button class="app-header__btn" id="btn-config" title="Configurar">⚙️</button>
          </div>
        </header>

        <div class="app-error-banner" id="app-error"></div>

        <div id="app-loading" style="text-align:center;padding:var(--space-2xl);color:var(--color-muted);font-size:1rem;">
          🌿 Carregando...
        </div>

        <div id="app-content" style="display:none">
          <!-- Floor Plan (full width) -->
          <div class="app-grid__full" id="floor-plan-container"></div>

          <!-- Grid: Timeline | Baseline + Contacts -->
          <div class="app-grid">
            <div id="timeline-container"></div>
            <div>
              <div id="baseline-container"></div>
              <div id="care-network-container"></div>
            </div>
          </div>
        </div>

        <footer class="app-footer">
          Casa Biônica v2 · <a href="#" onclick="Wizard.open();return false">Configurar</a>
        </footer>
      </div>`;

    // Bind config button
    document.getElementById('btn-config').addEventListener('click', () => Wizard.open());

    // Handle ?home= param changes
    window.addEventListener('popstate', () => {
      this.state.homeId = Utils.getHomeId();
      this.refresh();
    });
  },

  _startPolling() {
    // Floor plan: 30s
    setInterval(() => {
      FloorPlan.refresh(this.state.homeId);
    }, 30000);

    // Timeline: 60s
    setInterval(() => {
      Timeline.refresh(this.state.homeId);
    }, 60000);
  },

  async refresh() {
    document.getElementById('app-loading').style.display = 'block';
    document.getElementById('app-content').style.display = 'none';
    await this.init();
  }
};

// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
