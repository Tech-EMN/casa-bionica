/* Care Network JS — emergency contacts with escalation chain */

const CareNetwork = {
  async render(containerId, homeId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="care-network">
        <h2 class="care-network__title">📞 Rede de Cuidado</h2>
        <p class="care-network__subtitle">Quem será avisado se algo acontecer</p>
        <div class="care-network__contacts" id="care-contacts"></div>
        <div class="care-network__escalation" id="care-escalation"></div>
      </div>`;

    try {
      const data = await API.get(`/status/${homeId}`);
      this._populate(data);
    } catch (e) {
      document.getElementById('care-contacts').innerHTML =
        '<div style="color:var(--color-muted);padding:var(--space-md)">Não foi possível carregar os contatos.</div>';
    }
  },

  _populate(data) {
    const contacts = data.emergency_contacts || [];
    const contactsEl = document.getElementById('care-contacts');

    if (contacts.length === 0) {
      contactsEl.innerHTML = `
        <div style="color:var(--color-muted);padding:var(--space-md)">Nenhum contato cadastrado.</div>
        ${this._addButton()}`;
    } else {
      contactsEl.innerHTML = contacts.map(c => {
        const levelClass = `contact-card__level--n${c.priority || 1}`;
        const levelLabel = c.priority === 3 ? 'N3' : c.priority === 2 ? 'N2' : 'N1';
        return `
          <div class="contact-card">
            <div class="contact-card__name">${c.name}</div>
            <div class="contact-card__relation">${c.relationship || 'Familiar'}</div>
            <span class="contact-card__level ${levelClass}">${levelLabel}</span>
            <div class="contact-card__channel">📱 ${c.phone || '---'}</div>
            <span class="contact-card__status contact-card__status--available">🟢 Disponível</span>
          </div>`;
      }).join('') + this._addButton();
    }

    // Escalation info
    document.getElementById('care-escalation').innerHTML = `
      <strong>⏱️ Escalação:</strong> N1 (5min sem resposta) → N2 (15min) → SAMU (192)<br>
      <strong>Alerta via:</strong> WhatsApp — após 60min inativo ou desvio de rotina
    `;
  },

  _addButton() {
    return `
      <button class="care-network__add" onclick="alert('Onboarding Wizard em desenvolvimento')">
        <span class="care-network__add-icon">+</span>
        Adicionar Contato
      </button>`;
  }
};
