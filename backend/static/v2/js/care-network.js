/* Care Network JS — Professional contact rows */

const CareNetwork = {
  async render(containerId, homeId) {
    const c = document.getElementById(containerId);
    if (!c) return;
    c.innerHTML = `<div class="card care-panel" id="care-inner"></div>`;
    try {
      const data = await API.get(`/status/${homeId}`);
      this._render(data);
    } catch (e) { this._renderEmpty(); }
  },

  _render(data) {
    const contacts = data.emergency_contacts || [];
    let html = `<div class="care-panel__header"><span class="care-panel__title">Rede de Cuidado</span><span style="font-size:0.72rem;color:var(--color-text-muted)">${contacts.length} contato${contacts.length!==1?'s':''}</span></div>`;

    if (!contacts.length) {
      html += `<div style="padding:var(--space-4);color:var(--color-text-muted);text-align:center;font-size:0.85rem">Nenhum contato cadastrado</div>`;
    } else {
      html += `<div class="care-contacts">`;
      contacts.forEach(c => {
        const lvl = c.priority || 1;
        const lvlClass = `contact-row__level--n${Math.min(lvl,3)}`;
        html += `
          <div class="contact-row">
            <div>
              <div class="contact-row__name">${c.name}</div>
              <div class="contact-row__relation">${c.relationship || 'Contato'}</div>
            </div>
            <span class="contact-row__level ${lvlClass}">N${lvl}</span>
            <span class="contact-row__channel">📱 ${c.phone || '---'}</span>
          </div>`;
      });
      html += `</div>`;
    }

    html += `
      <div class="care-escalation">
        <strong>Escalação:</strong> N1 (5 min) → N2 (15 min) → SAMU (192)<br>
        <strong>Alerta:</strong> WhatsApp — após 60 min inativo ou desvio &gt; 2σ
      </div>
      <button class="care-add-btn" onclick="alert('Wizard em desenvolvimento')">+ Adicionar contato</button>`;

    document.getElementById('care-inner').innerHTML = html;
  },

  _renderEmpty() {
    document.getElementById('care-inner').innerHTML = `
      <div class="care-panel__header"><span class="care-panel__title">Rede de Cuidado</span></div>
      <div style="padding:var(--space-4);color:var(--color-text-muted);text-align:center">Não foi possível carregar os contatos.</div>`;
  }
};
