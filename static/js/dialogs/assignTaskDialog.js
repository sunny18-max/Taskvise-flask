(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  class AssignTaskDialog {
    constructor() {
      this.modalId = 'assign-task-modal';
    }

    open() {
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
      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.id = this.modalId;
      overlay.innerHTML = `
        <div class="modal modal-lg" role="dialog" aria-modal="true" aria-labelledby="assign-task-title">
          <div class="modal-header">
            <div>
              <h3 id="assign-task-title">Create Task</h3>
              <p class="modal-subtitle">Assign a task, deadline, and delivery status.</p>
            </div>
            <button class="modal-close" type="button" aria-label="Close">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="at-title">Task Title *</label>
              <input id="at-title" class="form-input" type="text" placeholder="Enter task title">
            </div>
            <div class="form-group">
              <label for="at-description">Description</label>
              <textarea id="at-description" class="form-textarea" placeholder="Describe the expected outcome"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="at-assignee">Assignee *</label>
                <select id="at-assignee" class="form-select">
                  <option value="">Select employee</option>
                </select>
              </div>
              <div class="form-group">
                <label for="at-project">Project</label>
                <select id="at-project" class="form-select">
                  <option value="">Select project</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="at-priority">Priority</label>
                <select id="at-priority" class="form-select">
                  <option value="low">Low</option>
                  <option value="medium" selected>Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div class="form-group">
                <label for="at-status">Status</label>
                <select id="at-status" class="form-select">
                  <option value="pending">Pending</option>
                  <option value="in-progress">In Progress</option>
                  <option value="review">In Review</option>
                  <option value="completed">Completed</option>
                  <option value="blocked">Blocked</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="at-due-date">Due Date *</label>
                <input id="at-due-date" class="form-input" type="date">
              </div>
              <div class="form-group">
                <label for="at-estimated-hours">Estimated Hours</label>
                <input id="at-estimated-hours" class="form-input" type="number" min="0" value="0">
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" type="button">Cancel</button>
            <button class="btn btn-primary" type="button" id="at-save">Create Task</button>
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
      modal.querySelector('#at-save').addEventListener('click', () => this.submit());
    }

    async populate() {
      const h = helpers();
      const context = h.getDashboardContext();
      let employees = h.getDashboardCollection('employees');
      let projects = h.getDashboardCollection('projects');
      if (!employees.length && context.dashboard && typeof context.dashboard.getEmployees === 'function') {
        employees = await context.dashboard.getEmployees();
      }
      if (!projects.length && context.dashboard && typeof context.dashboard.getProjects === 'function') {
        projects = await context.dashboard.getProjects();
      }
      const assigneeSelect = document.getElementById('at-assignee');
      const projectSelect = document.getElementById('at-project');
      const dueDateInput = document.getElementById('at-due-date');
      if (dueDateInput) {
        dueDateInput.min = new Date().toISOString().split('T')[0];
      }
      if (assigneeSelect) {
        assigneeSelect.innerHTML = `<option value="">Select employee</option>${employees
          .map((employee) => `<option value="${h.escapeHtml(employee.id)}">${h.escapeHtml(employee.name)} - ${h.escapeHtml(employee.position || employee.role || '')}</option>`)
          .join('')}`;
      }
      if (projectSelect) {
        projectSelect.innerHTML = `<option value="">Select project</option>${projects
          .map((project) => `<option value="${h.escapeHtml(project.id)}">${h.escapeHtml(project.name)}</option>`)
          .join('')}`;
      }
    }

    async submit() {
      const h = helpers();
      const context = h.getDashboardContext();
      const payload = {
        title: document.getElementById('at-title').value.trim(),
        description: document.getElementById('at-description').value.trim(),
        assignedTo: document.getElementById('at-assignee').value,
        project: document.getElementById('at-project').value,
        priority: document.getElementById('at-priority').value,
        status: document.getElementById('at-status').value,
        due_date: document.getElementById('at-due-date').value,
        estimatedHours: document.getElementById('at-estimated-hours').value,
      };

      if (!payload.title || !payload.assignedTo || !payload.due_date) {
        h.notify('Title, assignee, and due date are required.', 'error');
        return;
      }

      const saveButton = document.getElementById('at-save');
      saveButton.disabled = true;
      saveButton.textContent = 'Creating...';

      try {
        const endpoint = context.scope === 'manager' ? '/api/manager/tasks/assign' : `${context.apiBase}/tasks`;
        await h.requestJson(endpoint, { method: 'POST', body: payload });
        h.notify('Task created successfully', 'success');
        this.close();
        await h.refreshView();
      } catch (error) {
        console.error(error);
        h.notify(error.message || 'Failed to create task', 'error');
      } finally {
        saveButton.disabled = false;
        saveButton.textContent = 'Create Task';
      }
    }
  }

  const dialog = new AssignTaskDialog();
  window.assignTaskDialog = dialog;
  window.openAssignTaskDialog = function () {
    dialog.open();
  };
  window.closeAssignTaskDialog = function () {
    dialog.close();
  };
})();
