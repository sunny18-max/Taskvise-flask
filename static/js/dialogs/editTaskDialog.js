(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  function closeEditTaskDialog() {
    const modal = document.getElementById('edit-task-modal');
    if (modal) {
      modal.remove();
    }
  }

  async function openEditTaskDialog(taskId, tasks, updateTaskCallback) {
    const h = helpers();
    const context = h.getDashboardContext();
    const taskList = Array.isArray(tasks) ? tasks : h.getDashboardCollection('tasks');
    let employeeList = h.getDashboardCollection('employees');
    let projectList = h.getDashboardCollection('projects');
    if (!employeeList.length && context.dashboard && typeof context.dashboard.getEmployees === 'function') {
      employeeList = await context.dashboard.getEmployees();
    }
    if (!projectList.length && context.dashboard && typeof context.dashboard.getProjects === 'function') {
      projectList = await context.dashboard.getProjects();
    }
    const task = (taskList || []).find((item) => String(item.id) === String(taskId));
    if (!task) {
      h.notify('Task not found', 'error');
      return;
    }

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'edit-task-modal';
    overlay.innerHTML = `
      <div class="modal modal-lg" role="dialog" aria-modal="true" aria-labelledby="edit-task-title">
        <div class="modal-header">
          <div>
            <h3 id="edit-task-title">Edit Task</h3>
            <p class="modal-subtitle">Adjust ownership, timing, and delivery status.</p>
          </div>
          <button class="modal-close" type="button" aria-label="Close">&times;</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="et-title">Task Title *</label>
            <input id="et-title" class="form-input" type="text" value="${h.escapeHtml(task.title || '')}">
          </div>
          <div class="form-group">
            <label for="et-description">Description</label>
            <textarea id="et-description" class="form-textarea">${h.escapeHtml(task.description || '')}</textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="et-assignee">Assignee</label>
              <select id="et-assignee" class="form-select">
                <option value="">Unassigned</option>
                ${employeeList
                  .map((employee) => `<option value="${h.escapeHtml(employee.id)}">${h.escapeHtml(employee.name)} - ${h.escapeHtml(employee.position || employee.role || '')}</option>`)
                  .join('')}
              </select>
            </div>
            <div class="form-group">
              <label for="et-project">Project</label>
              <select id="et-project" class="form-select">
                <option value="">No project</option>
                ${projectList
                  .map((project) => `<option value="${h.escapeHtml(project.id)}">${h.escapeHtml(project.name)}</option>`)
                  .join('')}
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="et-priority">Priority</label>
              <select id="et-priority" class="form-select">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div class="form-group">
              <label for="et-status">Status</label>
              <select id="et-status" class="form-select">
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
              <label for="et-due-date">Due Date *</label>
              <input id="et-due-date" class="form-input" type="date" value="${h.escapeHtml(task.due_date || task.dueDate || '')}">
            </div>
            <div class="form-group">
              <label for="et-estimated-hours">Estimated Hours</label>
              <input id="et-estimated-hours" class="form-input" type="number" min="0" value="${h.escapeHtml(String(task.estimated_hours || task.estimatedHours || 0))}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="et-actual-hours">Actual Hours</label>
              <input id="et-actual-hours" class="form-input" type="number" min="0" value="${h.escapeHtml(String(task.actual_hours || task.actualHours || 0))}">
            </div>
            <div class="form-group">
              <label for="et-progress">Progress</label>
              <input id="et-progress" class="form-input" type="number" min="0" max="100" value="${h.escapeHtml(String(task.progress || 0))}">
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-outline" type="button">Cancel</button>
          <button class="btn btn-primary" type="button" id="et-save">Save Changes</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    document.getElementById('et-assignee').value = String(task.assignee_id || '');
    document.getElementById('et-project').value = String(task.project_id || '');
    document.getElementById('et-priority').value = String(task.priority || 'medium').toLowerCase();
    document.getElementById('et-status').value = String(task.status || 'pending').toLowerCase();

    const close = () => closeEditTaskDialog();
    overlay.querySelector('.modal-close').addEventListener('click', close);
    overlay.querySelector('.btn-outline').addEventListener('click', close);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        close();
      }
    });

    document.getElementById('et-save').addEventListener('click', async () => {
      const payload = {
        title: document.getElementById('et-title').value.trim(),
        description: document.getElementById('et-description').value.trim(),
        assignee_id: document.getElementById('et-assignee').value,
        project_id: document.getElementById('et-project').value,
        priority: document.getElementById('et-priority').value,
        status: document.getElementById('et-status').value,
        dueDate: document.getElementById('et-due-date').value,
        estimatedHours: document.getElementById('et-estimated-hours').value,
        actualHours: document.getElementById('et-actual-hours').value,
        progress: document.getElementById('et-progress').value,
      };

      if (!payload.title || !payload.dueDate) {
        h.notify('Task title and due date are required.', 'error');
        return;
      }

      const saveButton = document.getElementById('et-save');
      saveButton.disabled = true;
      saveButton.textContent = 'Saving...';

      try {
        if (typeof updateTaskCallback === 'function') {
          const ok = await updateTaskCallback(taskId, payload);
          if (!ok) {
            throw new Error('Failed to update task');
          }
        } else {
          await h.requestJson(`${context.apiBase}/tasks/${encodeURIComponent(taskId)}`, {
            method: 'PUT',
            body: payload,
          });
        }
        h.notify('Task updated successfully', 'success');
        close();
        await h.refreshView();
      } catch (error) {
        console.error(error);
        h.notify(error.message || 'Failed to update task', 'error');
      } finally {
        saveButton.disabled = false;
        saveButton.textContent = 'Save Changes';
      }
    });
  }

  window.openEditTaskDialog = openEditTaskDialog;
})();
