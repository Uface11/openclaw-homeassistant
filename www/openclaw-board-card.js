class OpenClawBoardCard extends HTMLElement {
  setConfig(config) {
    this.config = {
      title: 'OpenClaw Board',
      icon: 'mdi:robot-outline',
      board_url: '',
      quick_actions: ['Status check', 'Create Kanban task', 'Summarize updates'],
      ...config,
    };
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  async _send(text) {
    const message = (text || '').trim();
    if (!message) return;
    this._pending = true;
    this.render();
    try {
      await this._hass.callService('openclaw', 'send_message', { message });
      this._last = `Sent: ${message}`;
      this._input = '';
    } catch (e) {
      this._last = `Error: ${e?.message || e}`;
    } finally {
      this._pending = false;
      this.render();
    }
  }

  render() {
    if (!this._hass || !this.config) return;
    const status = this._hass.states['sensor.openclaw_status']?.state ?? 'unknown';
    const lastResponse = this._hass.states['sensor.openclaw_status']?.attributes?.last_response ?? '-';

    if (!this.content) {
      const card = document.createElement('ha-card');
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const quick = (this.config.quick_actions || [])
      .map((q) => `<button class="quick" data-q="${q}">${q}</button>`)
      .join('');

    this.content.innerHTML = `
      <style>
        .head{display:flex;align-items:center;gap:10px;margin-bottom:12px}
        .title{font-weight:600}
        .muted{opacity:.7;font-size:12px}
        .row{display:flex;gap:8px}
        input{flex:1;padding:10px;border-radius:10px;border:1px solid var(--divider-color);background:var(--card-background-color);color:var(--primary-text-color)}
        button{padding:10px 12px;border-radius:10px;border:none;background:var(--primary-color);color:white;cursor:pointer}
        button[disabled]{opacity:.5;cursor:not-allowed}
        .quick-wrap{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
        .quick{background:var(--secondary-background-color);color:var(--primary-text-color);border:1px solid var(--divider-color)}
        .meta{margin-top:12px;font-size:12px;display:grid;gap:4px}
      </style>
      <div class="head">
        <ha-icon icon="${this.config.icon}"></ha-icon>
        <div>
          <div class="title">${this.config.title}</div>
          <div class="muted">Status: ${status}</div>
        </div>
      </div>
      <div class="row">
        <input id="prompt" placeholder="Frag OpenClaw oder erstelle ein Board-Task..." value="${this._input || ''}" />
        <button id="send" ${this._pending ? 'disabled' : ''}>${this._pending ? '…' : 'Send'}</button>
      </div>
      <div class="quick-wrap">${quick}</div>
      ${this.config.board_url ? `<div style="margin-top:10px"><a href="${this.config.board_url}" target="_blank" rel="noreferrer">Open Board ↗</a></div>` : ''}
      <div class="meta">
        <div>Gateway last response: ${lastResponse}</div>
        <div>${this._last || 'Ready'}</div>
      </div>
    `;

    this.content.querySelector('#prompt')?.addEventListener('input', (e) => {
      this._input = e.target.value;
    });

    this.content.querySelector('#prompt')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this._send(this._input);
    });

    this.content.querySelector('#send')?.addEventListener('click', () => this._send(this._input));

    this.content.querySelectorAll('.quick').forEach((btn) => {
      btn.addEventListener('click', () => this._send(btn.dataset.q));
    });
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('openclaw-board-card', OpenClawBoardCard);
