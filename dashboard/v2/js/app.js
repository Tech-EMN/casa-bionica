/* App Shell — Professional health-tech monitoring */

const App = {
  state: { homeId: 'home-001', elderlyName: '' },

  async init() {
    this.state.homeId = Utils.getHomeId();
    this._renderShell();
    const ok = await API.healthCheck();
    if (!ok) { this._showError('Servidor indisponível. Verifique sua conexão.'); return; }

    await Promise.all([
      FloorPlan.render('floor-plan-container', this.state.homeId),
      Timeline.render('timeline-container', this.state.homeId),
      CareNetwork.render('care-network-container', this.state.homeId),
      this._loadBaseline()
    ]);

    try {
      const data = await API.get(`/status/${this.state.homeId}`);
      this.state.elderlyName = data.elderly_name || '';
    } catch (e) {}

    this._hideLoading();
    this._startPolling();
  },

  _renderShell() {
    document.getElementById('app-root').innerHTML = `
      <div class="app-shell">
        <header class="app-header">
          <div class="app-logo"><span class="app-logo__dot"></span>Casa Biônica</div>
          <div class="app-actions">
            <button class="app-btn" id="btn-config" title="Configurar">Ajustes</button>
          </div>
        </header>
        <div class="app-error" id="app-error"></div>
        <div id="app-loading">
          <div class="app-loading"><div class="app-loading__spinner"></div><div class="app-loading__text">Carregando Casa Biônica...</div></div>
        </div>
        <div id="app-content" style="display:none">
          <div class="app-grid__full" id="floor-plan-container"></div>
          <div class="app-grid">
            <div id="timeline-container"></div>
            <div>
              <div id="baseline-container"></div>
              <div id="care-network-container"></div>
            </div>
          </div>
        </div>
        <footer class="app-footer">Casa Biônica · v2.2</footer>
      </div>`;
    document.getElementById('btn-config').addEventListener('click', () => Wizard.open());
    window.addEventListener('popstate', () => { this.state.homeId = Utils.getHomeId(); this.refresh(); });
  },

  async _loadBaseline() {
    await Baseline.render('baseline-container', this.state.homeId);
  },

  _hideLoading() {
    document.getElementById('app-loading').style.display = 'none';
    document.getElementById('app-content').style.display = 'block';
  },

  _showError(msg) {
    const el = document.getElementById('app-error');
    el.textContent = '⚠️ ' + msg;
    el.classList.add('app-error--visible');
  },

  _startPolling() {
    setInterval(() => FloorPlan.refresh(this.state.homeId), 30000);
    setInterval(() => Timeline.refresh(this.state.homeId), 60000);
  },

  async refresh() {
    document.getElementById('app-loading').style.display = 'block';
    document.getElementById('app-content').style.display = 'none';
    await this.init();
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
