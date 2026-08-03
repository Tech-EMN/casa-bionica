/* Wizard JS — 4-step onboarding modal */

const Wizard = {
  steps: [
    { title: 'Quem vamos cuidar?', fields: ['elderly_name', 'elderly_age'] },
    { title: 'Onde fica a casa?', fields: ['address', 'home_name'] },
    { title: 'Quem avisar?', fields: ['contact_name', 'contact_phone'] },
    { title: 'Parear sensores', fields: [] }
  ],

  currentStep: 0,

  open() {
    this.currentStep = 0;

    const overlay = document.createElement('div');
    overlay.className = 'wizard-overlay';
    overlay.id = 'wizard-overlay';
    overlay.innerHTML = this._template();
    document.body.appendChild(overlay);

    this._bindEvents(overlay);
    this._renderStep();
  },

  close() {
    const overlay = document.getElementById('wizard-overlay');
    if (overlay) overlay.remove();
  },

  _template() {
    return `
      <div class="wizard-modal">
        <div class="wizard-header">
          <h2 class="wizard-header__title" id="wizard-title">Configurar Casa Biônica</h2>
          <button class="wizard-header__close" id="wizard-close">✕</button>
        </div>
        <div class="wizard-steps" id="wizard-steps">
          ${this.steps.map((_, i) =>
            `<div class="wizard-step-dot ${i === 0 ? 'wizard-step-dot--active' : ''}" id="wizard-dot-${i}"></div>`
          ).join('')}
        </div>
        <div class="wizard-body" id="wizard-body"></div>
        <div class="wizard-footer">
          <button class="wizard-btn wizard-btn--secondary" id="wizard-back" ${this.currentStep === 0 ? 'disabled' : ''}>Voltar</button>
          <button class="wizard-btn wizard-btn--primary" id="wizard-next">Próximo</button>
        </div>
      </div>`;
  },

  _bindEvents(overlay) {
    overlay.querySelector('#wizard-close').addEventListener('click', () => this.close());
    overlay.querySelector('#wizard-back').addEventListener('click', () => {
      if (this.currentStep > 0) {
        this.currentStep--;
        this._renderStep();
      }
    });
    overlay.querySelector('#wizard-next').addEventListener('click', () => {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++;
        this._renderStep();
      } else {
        this._finish();
      }
    });
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) this.close();
    });
  },

  _renderStep() {
    const step = this.steps[this.currentStep];
    document.getElementById('wizard-title').textContent = step.title;

    // Update step dots
    document.querySelectorAll('.wizard-step-dot').forEach((dot, i) => {
      dot.className = 'wizard-step-dot';
      if (i < this.currentStep) dot.classList.add('wizard-step-dot--done');
      if (i === this.currentStep) dot.classList.add('wizard-step-dot--active');
    });

    // Back button
    const backBtn = document.getElementById('wizard-back');
    backBtn.disabled = this.currentStep === 0;

    // Next button
    const nextBtn = document.getElementById('wizard-next');
    nextBtn.textContent = this.currentStep === this.steps.length - 1 ? 'Finalizar' : 'Próximo';

    // Body
    const body = document.getElementById('wizard-body');
    body.innerHTML = this._stepContent(step);
  },

  _stepContent(step) {
    if (this.currentStep === 0) {
      return `
        <div class="wizard-field">
          <label class="wizard-field__label">Nome do idoso</label>
          <input class="wizard-field__input" id="wiz-elderly-name" placeholder="Ex: Dona Cida" value="">
          <span class="wizard-field__hint">Como o idoso gosta de ser chamado</span>
        </div>
        <div class="wizard-field">
          <label class="wizard-field__label">Idade</label>
          <input class="wizard-field__input" id="wiz-elderly-age" type="number" placeholder="Ex: 78" min="60" max="120">
        </div>`;
    } else if (this.currentStep === 1) {
      return `
        <div class="wizard-field">
          <label class="wizard-field__label">Nome da casa</label>
          <input class="wizard-field__input" id="wiz-home-name" placeholder="Ex: Casa da Mãe" value="">
          <span class="wizard-field__hint">Um nome para identificar esta residência</span>
        </div>
        <div class="wizard-field">
          <label class="wizard-field__label">Endereço</label>
          <input class="wizard-field__input" id="wiz-address" placeholder="Ex: Rua das Flores, 42, São Paulo - SP">
          <span class="wizard-field__hint">Necessário para emergências (SAMU)</span>
        </div>`;
    } else if (this.currentStep === 2) {
      return `
        <div class="wizard-field">
          <label class="wizard-field__label">Nome do contato</label>
          <input class="wizard-field__input" id="wiz-contact-name" placeholder="Ex: Eduardo (filho)">
        </div>
        <div class="wizard-field">
          <label class="wizard-field__label">WhatsApp</label>
          <input class="wizard-field__input" id="wiz-contact-phone" placeholder="Ex: (11) 99999-9999">
          <span class="wizard-field__hint">Primeiro a ser avisado (N1)</span>
        </div>`;
    } else {
      return `
        <div style="text-align:center;padding:var(--space-xl)">
          <div style="font-size:3rem;margin-bottom:var(--space-md)">📱</div>
          <p style="font-size:0.95rem;color:var(--color-text);margin-bottom:var(--space-sm)">
            <strong>Escaneie o QR Code</strong> do sensor ESP32
          </p>
          <p style="font-size:0.8rem;color:var(--color-muted)">
            O técnico fará o pareamento durante a instalação.<br>
            Você receberá um link por WhatsApp quando tudo estiver pronto.
          </p>
        </div>`;
    }
  },

  _finish() {
    const name = document.getElementById('wiz-elderly-name')?.value || '';
    alert(`✅ Configuração da casa para "${name}" concluída!\n\nO técnico fará a instalação dos sensores. Você receberá um link de acesso por WhatsApp.`);
    this.close();
  }
};
