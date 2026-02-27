class OpenClawBoardCard extends HTMLElement {
  setConfig(config) {
    this.config = {
      title: 'OpenClaw Board',
      icon: 'mdi:robot-outline',
      board_url: '',
      storage_key: 'openclaw_board_v2',
      sync_with_openclaw: true,
      ...config,
    };

    this.columns = [
      { id: 'todo', title: 'Offen', icon: '📋' },
      { id: 'in-progress', title: 'In Arbeit', icon: '⚡' },
      { id: 'review', title: 'Review', icon: '👀' },
      { id: 'done', title: 'Erledigt', icon: '✅' },
    ];

    this.tasks = this._loadTasks();
    this.newTaskInputs = {};
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  _loadTasks() {
    try {
      const raw = localStorage.getItem(this.config.storage_key);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  _saveTasks() {
    localStorage.setItem(this.config.storage_key, JSON.stringify(this.tasks));
  }

  _uid() {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }

  async _notifyOpenClaw(text) {
    if (!this.config.sync_with_openclaw) return;
    try {
      await this._hass.callService('openclaw', 'run_task', { task: text });
    } catch (e) {
      this._last = `OpenClaw sync failed: ${e?.message || e}`;
    }
  }

  async _addTask(columnId) {
    const title = (this.newTaskInputs[columnId] || '').trim();
    if (!title) return;

    const task = {
      id: this._uid(),
      title,
      status: columnId,
      priority: 'medium',
      createdAt: new Date().toISOString(),
    };

    this.tasks.unshift(task);
    this.newTaskInputs[columnId] = '';
    this._saveTasks();
    this._last = `Task erstellt: ${title}`;

    await this._notifyOpenClaw(`Erstelle Kanban-Task: "${title}" in Spalte "${columnId}".`);
    this.render();
  }

  async _moveTask(taskId, targetColumnId) {
    const task = this.tasks.find((t) => t.id === taskId);
    if (!task || task.status === targetColumnId) return;

    const old = task.status;
    task.status = targetColumnId;
    task.updatedAt = new Date().toISOString();
    this._saveTasks();
    this._last = `Task verschoben: ${task.title} (${old} → ${targetColumnId})`;

    await this._notifyOpenClaw(`Verschiebe Kanban-Task: "${task.title}" von "${old}" nach "${targetColumnId}".`);
    this.render();
  }

  _deleteTask(taskId) {
    const idx = this.tasks.findIndex((t) => t.id === taskId);
    if (idx === -1) return;
    const [removed] = this.tasks.splice(idx, 1);
    this._saveTasks();
    this._last = `Task gelöscht: ${removed.title}`;
    this.render();
  }

  _priorityBadge(priority) {
    const p = (priority || '').toLowerCase();
    if (!p) return '';
    return `<span class="task-priority priority-${p}">${p}</span>`;
  }

  render() {
    if (!this._hass || !this.config) return;

    const statusState = this._hass.states['sensor.openclaw_status'];
    const status = statusState?.state ?? 'unknown';

    if (!this.content) {
      const card = document.createElement('ha-card');
      this.content = document.createElement('div');
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const boardHtml = this.columns
      .map((column) => {
        const columnTasks = this.tasks.filter((t) => t.status === column.id);

        const tasksHtml =
          columnTasks.length === 0
            ? `<div class="empty-state">Keine Aufgaben</div>`
            : columnTasks
                .map(
                  (task) => `
                <div class="task-card" draggable="true" data-task-id="${task.id}">
                  <div class="task-top">
                    <div class="task-title">${task.title}</div>
                    <button class="delete-task" data-delete-id="${task.id}" title="Löschen">✕</button>
                  </div>
                  <div class="task-meta">
                    ${this._priorityBadge(task.priority)}
                  </div>
                </div>
              `,
                )
                .join('');

        return `
          <div class="kanban-column" data-column-id="${column.id}">
            <div class="column-header">
              <span class="column-icon">${column.icon}</span>
              <span class="column-title">${column.title}</span>
              <span class="task-count">${columnTasks.length}</span>
            </div>
            <div class="tasks-list" data-drop-column="${column.id}">
              ${tasksHtml}
            </div>
            <div class="add-task-input">
              <input
                type="text"
                class="task-input"
                data-input-column="${column.id}"
                placeholder="Aufgabe hinzufügen..."
                value="${this.newTaskInputs[column.id] || ''}"
              />
            </div>
          </div>
        `;
      })
      .join('');

    this.content.innerHTML = `
      <style>
        .shell{padding:14px}
        .head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
        .titleWrap{display:flex;align-items:center;gap:10px}
        .title{font-weight:700}
        .muted{opacity:.72;font-size:12px}

        .kanban-board{display:grid;grid-template-columns:repeat(4,minmax(220px,1fr));gap:12px;min-height:420px}
        .kanban-column{background:var(--secondary-background-color);border:1px solid var(--divider-color);border-radius:10px;display:flex;flex-direction:column;min-height:340px}
        .column-header{display:flex;align-items:center;gap:8px;padding:10px;border-bottom:1px solid var(--divider-color);font-weight:600}
        .column-title{flex:1}
        .task-count{font-size:12px;opacity:.75;background:var(--card-background-color);padding:2px 8px;border-radius:999px}

        .tasks-list{flex:1;display:flex;flex-direction:column;gap:8px;padding:10px}
        .empty-state{opacity:.6;font-size:12px;text-align:center;padding:22px 8px}

        .task-card{background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:8px;padding:9px;cursor:grab}
        .task-card:active{cursor:grabbing}
        .task-top{display:flex;gap:8px;align-items:flex-start}
        .task-title{font-size:13px;line-height:1.35;flex:1}
        .delete-task{border:none;background:transparent;color:var(--secondary-text-color);cursor:pointer;font-size:12px}
        .delete-task:hover{color:var(--error-color)}
        .task-meta{margin-top:6px;display:flex;gap:6px;flex-wrap:wrap}

        .task-priority{font-size:10px;text-transform:uppercase;border-radius:999px;padding:2px 6px}
        .priority-high{background:rgba(244,67,54,.14);color:#f44336}
        .priority-medium{background:rgba(255,152,0,.14);color:#ff9800}
        .priority-low{background:rgba(158,158,158,.14);color:#9e9e9e}

        .add-task-input{padding:9px;border-top:1px solid var(--divider-color)}
        .task-input{width:100%;padding:8px;border-radius:8px;border:1px solid var(--divider-color);background:var(--card-background-color);color:var(--primary-text-color)}

        .toolbar{display:flex;gap:8px;align-items:center}
        .btn{border:1px solid var(--divider-color);background:var(--card-background-color);padding:6px 10px;border-radius:8px;cursor:pointer}

        @media (max-width:1200px){.kanban-board{grid-template-columns:repeat(2,minmax(200px,1fr));}}
        @media (max-width:760px){.kanban-board{grid-template-columns:1fr;}}
      </style>

      <div class="shell">
        <div class="head">
          <div class="titleWrap">
            <ha-icon icon="${this.config.icon}"></ha-icon>
            <div>
              <div class="title">${this.config.title}</div>
              <div class="muted">OpenClaw: ${status}</div>
            </div>
          </div>
          <div class="toolbar">
            ${this.config.board_url ? `<a class="btn" href="${this.config.board_url}" target="_blank" rel="noreferrer">Open Board ↗</a>` : ''}
            <button class="btn" id="refreshStatus">Update</button>
            <button class="btn" id="healthCheck">Health</button>
          </div>
        </div>

        <div class="kanban-board">${boardHtml}</div>

        <div class="muted" style="margin-top:10px">${this._last || 'Ready'}</div>
      </div>
    `;

    this.content.querySelector('#refreshStatus')?.addEventListener('click', async () => {
      await this._hass.callService('openclaw', 'refresh_status', {});
      this._last = 'Status aktualisiert';
      this.render();
    });

    this.content.querySelector('#healthCheck')?.addEventListener('click', async () => {
      try {
        await this._hass.callService('openclaw', 'health_check', {});
        this._last = 'Health check erfolgreich';
      } catch (e) {
        this._last = `Health check Fehler: ${e?.message || e}`;
      }
      this.render();
    });

    this.content.querySelectorAll('[data-input-column]').forEach((input) => {
      const col = input.dataset.inputColumn;
      input.addEventListener('input', (e) => {
        this.newTaskInputs[col] = e.target.value;
      });
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') this._addTask(col);
      });
    });

    this.content.querySelectorAll('[data-delete-id]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this._deleteTask(btn.dataset.deleteId);
      });
    });

    this.content.querySelectorAll('.task-card').forEach((card) => {
      card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/task-id', card.dataset.taskId);
      });
    });

    this.content.querySelectorAll('[data-drop-column]').forEach((colEl) => {
      colEl.addEventListener('dragover', (e) => e.preventDefault());
      colEl.addEventListener('drop', (e) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData('text/task-id');
        const targetColumn = colEl.dataset.dropColumn;
        this._moveTask(taskId, targetColumn);
      });
    });
  }

  getCardSize() {
    return 6;
  }
}

customElements.define('openclaw-board-card', OpenClawBoardCard);
