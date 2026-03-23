(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  function closeTaskDetailsDialog() {
    const modal = document.getElementById('task-details-modal');
    if (modal) {
      modal.remove();
    }
  }

  function openTaskDetailsDialog(taskId, tasks, employees, projects) {
    const h = helpers();
    if (!h) {
      return;
    }

    const taskList = tasks || h.getDashboardCollection('tasks');
    const employeeList = employees || h.getDashboardCollection('employees');
    const projectList = projects || h.getDashboardCollection('projects');
    const task = (taskList || []).find((item) => String(item.id) === String(taskId));
    if (!task) {
      h.notify('Task not found', 'error');
      return;
    }

    const project = (projectList || []).find((item) => String(item.id) === String(task.project_id || ''));
    const assigneeName = task.assignee_name || h.getEmployeeName(task.assignee_id, employeeList) || 'Unassigned';

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'task-details-modal';
    overlay.innerHTML = `
      <div class="modal modal-lg details-modal" role="dialog" aria-modal="true" aria-labelledby="task-details-title">
        <div class="modal-header">
          <div>
            <h3 id="task-details-title">${h.escapeHtml(task.title || 'Task')}</h3>
            <p class="modal-subtitle">${h.escapeHtml(task.description || 'No description provided')}</p>
          </div>
          <button class="modal-close" type="button" aria-label="Close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="details-grid">
            <div class="detail-card">
              <span class="detail-label">Assignee</span>
              <span class="detail-value">${h.escapeHtml(assigneeName)}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Project</span>
              <span class="detail-value">${h.escapeHtml(task.project_name || (project && project.name) || 'No project')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Due Date</span>
              <span class="detail-value">${h.escapeHtml(task.due_date || task.dueDate || 'Not set')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Priority</span>
              <span class="priority-badge ${h.escapeHtml(task.priority || 'medium')}">${h.escapeHtml(task.priority || 'medium')}</span>
            </div>
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Progress</h4>
              <span>${h.escapeHtml(String(task.progress || 0))}%</span>
            </div>
            <div class="detail-progress">
              <div class="detail-progress-bar">
                <span style="width:${Math.max(0, Math.min(100, Number(task.progress || 0)))}%"></span>
              </div>
            </div>
          </div>

          <div class="details-grid compact">
            <div class="detail-card">
              <span class="detail-label">Status</span>
              <span class="status-badge ${h.escapeHtml(task.status || 'pending')}">${h.escapeHtml(task.status || 'pending')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Estimated Hours</span>
              <span class="detail-value">${h.escapeHtml(String(task.estimated_hours || task.estimatedHours || 0))}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Actual Hours</span>
              <span class="detail-value">${h.escapeHtml(String(task.actual_hours || task.actualHours || 0))}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Created</span>
              <span class="detail-value">${h.escapeHtml(task.created_at || 'Unknown')}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" type="button">Close</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const close = () => closeTaskDetailsDialog();
    overlay.querySelector('.modal-close').addEventListener('click', close);
    overlay.querySelector('.btn-outline').addEventListener('click', close);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        close();
      }
    });
  }

  window.openTaskDetailsDialog = openTaskDetailsDialog;
})();
