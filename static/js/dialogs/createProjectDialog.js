(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  class CreateProjectDialog {
    constructor() {
      this.modalId = 'create-project-modal';
      this.selectedTeamMembers = [];
    }

    open() {
      this.selectedTeamMembers = [];
      this.render();
      this.bind();
      this.populate();
    }

    close() {
      const modal = document.getElementById(this.modalId);
      if (modal) {
        modal.remove();
      }
    }

    render() {
      const h = helpers();
      if (!h) {
        return;
      }

      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.id = this.modalId;
      overlay.innerHTML = `
        <div class="modal modal-lg" role="dialog" aria-modal="true" aria-labelledby="create-project-title">
          <div class="modal-header">
            <div>
              <h3 id="create-project-title">Create Project</h3>
              <p class="modal-subtitle">Set up a project, owner, timeline, and team.</p>
            </div>
            <button class="modal-close" type="button" aria-label="Close">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="cp-name">Project Name *</label>
              <input id="cp-name" class="form-input" type="text" placeholder="Enter project name">
            </div>
            <div class="form-group">
              <label for="cp-description">Description</label>
              <textarea id="cp-description" class="form-textarea" placeholder="Summarize the project scope"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="cp-company">Company</label>
                <input id="cp-company" class="form-input" type="text" value="${h.escapeHtml(h.getDefaultCompanyName())}">
              </div>
              <div class="form-group">
                <label for="cp-deadline">Deadline *</label>
                <input id="cp-deadline" class="form-input" type="date">
              </div>
              <div class="form-group">
                <label for="cp-status">Status</label>
                <select id="cp-status" class="form-select">
                  <option value="planning">Planning</option>
                  <option value="active">Active</option>
                  <option value="on-hold">On Hold</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="cp-owner">Owner</label>
                <select id="cp-owner" class="form-select">
                  <option value="">Select project owner</option>
                </select>
              </div>
              <div class="form-group">
                <label for="cp-progress">Initial Progress</label>
                <input id="cp-progress" class="form-input" type="number" min="0" max="100" value="0">
              </div>
            </div>
            <div class="form-group">
              <label for="cp-team-members">Team Members</label>
              <select id="cp-team-members" class="form-select">
                <option value="">Add team member</option>
              </select>
              <div id="cp-selected-members" class="tag-list" style="margin-top:0.75rem;"></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" type="button">Cancel</button>
            <button class="btn btn-primary" type="button" id="cp-save">Create Project</button>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);
    }

    bind() {
      const modal = document.getElementById(this.modalId);
      if (!modal) {
        return;
      }

      modal.querySelector('.modal-close').addEventListener('click', () => this.close());
      modal.querySelector('.btn-outline').addEventListener('click', () => this.close());
      modal.addEventListener('click', (event) => {
        if (event.target === modal) {
          this.close();
        }
      });
      modal.querySelector('#cp-save').addEventListener('click', () => this.submit());
      modal.querySelector('#cp-team-members').addEventListener('change', (event) => {
        const memberId = String(event.target.value || '').trim();
        if (!memberId) {
          return;
        }
        this.selectedTeamMembers = helpers().uniqueStrings([...this.selectedTeamMembers, memberId]);
        event.target.value = '';
        this.renderSelectedMembers();
      });
    }

    async populate() {
      const h = helpers();
      const context = h.getDashboardContext();
      let employees = h.getDashboardCollection('employees');
      if (!employees.length && context.dashboard && typeof context.dashboard.getEmployees === 'function') {
        employees = await context.dashboard.getEmployees();
      }
      const ownerSelect = document.getElementById('cp-owner');
      const teamSelect = document.getElementById('cp-team-members');
      const deadlineInput = document.getElementById('cp-deadline');
      if (deadlineInput) {
        deadlineInput.min = new Date().toISOString().split('T')[0];
      }
      if (!ownerSelect || !teamSelect) {
        return;
      }

      const ownerOptions = employees
        .map((employee) => `<option value="${h.escapeHtml(employee.id)}">${h.escapeHtml(employee.name)} - ${h.escapeHtml(employee.position || employee.role || '')}</option>`)
        .join('');

      ownerSelect.innerHTML = `<option value="">Select project owner</option>${ownerOptions}`;
      if (context.dashboard && context.dashboard.currentUserId) {
        ownerSelect.value = context.dashboard.currentUserId;
      }
      teamSelect.innerHTML = `<option value="">Add team member</option>${ownerOptions}`;
      this.renderSelectedMembers();
    }

    renderSelectedMembers() {
      const h = helpers();
      const employees = h.getDashboardCollection('employees');
      const employeeMap = h.buildEmployeeMap(employees);
      const container = document.getElementById('cp-selected-members');
      if (!container) {
        return;
      }
      if (!this.selectedTeamMembers.length) {
        container.innerHTML = '<p class="detail-empty">No team members selected yet.</p>';
        return;
      }
      container.innerHTML = this.selectedTeamMembers
        .map((memberId) => {
          const employee = employeeMap.get(String(memberId));
          const label = employee ? employee.name : memberId;
          return `
            <span class="member-tag">
              ${h.escapeHtml(label)}
              <button type="button" class="tag-remove" data-member-id="${h.escapeHtml(memberId)}" aria-label="Remove ${h.escapeHtml(label)}">&times;</button>
            </span>
          `;
        })
        .join('');

      container.querySelectorAll('.tag-remove').forEach((button) => {
        button.addEventListener('click', () => {
          this.selectedTeamMembers = this.selectedTeamMembers.filter((memberId) => memberId !== button.dataset.memberId);
          this.renderSelectedMembers();
        });
      });
    }

    async submit() {
      const h = helpers();
      const context = h.getDashboardContext();
      const name = document.getElementById('cp-name').value.trim();
      const deadline = document.getElementById('cp-deadline').value;
      if (!name || !deadline) {
        h.notify('Project name and deadline are required.', 'error');
        return;
      }

      const payload = {
        name,
        description: document.getElementById('cp-description').value.trim(),
        company: document.getElementById('cp-company').value.trim(),
        deadline,
        status: document.getElementById('cp-status').value,
        owner_id: document.getElementById('cp-owner').value,
        progress: document.getElementById('cp-progress').value,
        teamMembers: this.selectedTeamMembers,
      };

      const saveButton = document.getElementById('cp-save');
      saveButton.disabled = true;
      saveButton.textContent = 'Creating...';

      try {
        const endpoint = context.scope === 'manager' ? '/api/manager/projects/create' : `${context.apiBase}/projects`;
        await h.requestJson(endpoint, { method: 'POST', body: payload });
        h.notify('Project created successfully', 'success');
        this.close();
        await h.refreshView();
      } catch (error) {
        console.error(error);
        h.notify(error.message || 'Failed to create project', 'error');
      } finally {
        saveButton.disabled = false;
        saveButton.textContent = 'Create Project';
      }
    }
  }

  const dialog = new CreateProjectDialog();
  window.createProjectDialog = dialog;
  window.openCreateProjectDialog = function () {
    dialog.open();
  };
  window.closeCreateProjectDialog = function () {
    dialog.close();
  };
})();
