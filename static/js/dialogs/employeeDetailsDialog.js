(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  function closeEmployeeDetailsDialog() {
    const modal = document.getElementById('employee-details-modal');
    if (modal) {
      modal.remove();
    }
  }

  async function fetchCanonicalEmployee(employeeId) {
    const h = helpers();
    const context = h.getDashboardContext();
    if (!['admin', 'manager', 'hr', 'teamlead'].includes(context.scope)) {
      return null;
    }
    try {
      return await h.requestJson(`/api/employee/${encodeURIComponent(employeeId)}`);
    } catch (_error) {
      return null;
    }
  }

  async function openEmployeeDetails(employeeId, employees, tasks) {
    const h = helpers();
    if (!h) {
      return;
    }

    const context = h.getDashboardContext();
    let employeeList = employees || h.getDashboardCollection('employees');
    let taskList = tasks || h.getDashboardCollection('tasks');
    if ((!employeeList || !employeeList.length) && context.dashboard && typeof context.dashboard.getEmployees === 'function') {
      employeeList = await context.dashboard.getEmployees();
    }
    if ((!taskList || !taskList.length) && context.dashboard && typeof context.dashboard.getTasks === 'function') {
      taskList = await context.dashboard.getTasks();
    }

    let employee = (employeeList || []).find((item) => String(item.id) === String(employeeId));
    const canonicalEmployee = await fetchCanonicalEmployee(employeeId);
    if (canonicalEmployee) {
      employee = { ...(employee || {}), ...canonicalEmployee };
    }
    if (!employee) {
      h.notify('Employee not found', 'error');
      return;
    }

    const myTasks = (taskList || []).filter((task) => String(task.assignee_id || task.assigneeId || task.assignedTo || '') === String(employee.id));
    const completedTasks = myTasks.length
      ? myTasks.filter((task) => String(task.status || '').toLowerCase() === 'completed').length
      : Number(employee.completedTasks || 0);
    const totalTasks = myTasks.length || Number(employee.totalTasks || 0);
    const productivity = Number(employee.productivity || employee.completionRate || (totalTasks ? Math.round((completedTasks / totalTasks) * 100) : 0));
    const skills = String(employee.skills || '').split(',').map((item) => item.trim()).filter(Boolean);

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'employee-details-modal';
    overlay.innerHTML = `
      <div class="modal modal-lg details-modal" role="dialog" aria-modal="true" aria-labelledby="employee-details-title">
        <div class="modal-header">
          <div>
            <h3 id="employee-details-title">${h.escapeHtml(employee.name || employee.fullName || 'Employee')}</h3>
            <p class="modal-subtitle">${h.escapeHtml(employee.email || '')}</p>
          </div>
          <button class="modal-close" type="button" aria-label="Close">&times;</button>
        </div>

        <div class="modal-body">
          <div class="details-grid">
            <div class="detail-card">
              <span class="detail-label">ID</span>
              <span class="detail-value">${h.escapeHtml(employee.id || 'Not assigned')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Role</span>
              <span class="detail-value">${h.escapeHtml(employee.role || employee.position || 'Employee')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Department</span>
              <span class="detail-value">${h.escapeHtml(employee.department || 'Unassigned')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Company</span>
              <span class="detail-value">${h.escapeHtml(employee.company || 'TaskVise')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Team</span>
              <span class="detail-value">${h.escapeHtml(employee.team_name || 'Shared Services')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Phone</span>
              <span class="detail-value">${h.escapeHtml(employee.phone || 'Not provided')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Location</span>
              <span class="detail-value">${h.escapeHtml(employee.location || 'Not set')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Status</span>
              <span class="detail-value">${h.escapeHtml(employee.status || 'active')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Reports</span>
              <span class="detail-value">${h.escapeHtml(employee.manager_id || 'N/A')} / ${h.escapeHtml(employee.teamlead_id || 'N/A')}</span>
            </div>
          </div>

          <div class="details-grid compact">
            <div class="detail-card">
              <span class="detail-label">Tasks</span>
              <span class="detail-value">${completedTasks}/${totalTasks}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Productivity</span>
              <span class="detail-value">${h.escapeHtml(String(productivity))}%</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Joined</span>
              <span class="detail-value">${h.escapeHtml(employee.join_date || 'Unknown')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Last Login</span>
              <span class="detail-value">${h.escapeHtml(employee.last_login || 'Never')}</span>
            </div>
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Performance</h4>
              <span>${h.escapeHtml(String(productivity))}%</span>
            </div>
            <div class="detail-progress">
              <div class="detail-progress-bar">
                <span style="width:${Math.max(0, Math.min(100, productivity))}%"></span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Skills</h4>
              <span>${skills.length}</span>
            </div>
            ${
              skills.length
                ? `<div class="tag-list">${skills.map((skill) => `<span class="member-tag">${h.escapeHtml(skill)}</span>`).join('')}</div>`
                : '<p class="detail-empty">No skills recorded for this employee.</p>'
            }
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Assigned Tasks</h4>
              <span>${myTasks.length}</span>
            </div>
            ${
              myTasks.length
                ? `<div class="detail-list">${myTasks
                    .slice(0, 5)
                    .map(
                      (task) => `
                        <div class="detail-list-item">
                          <div>
                            <strong>${h.escapeHtml(task.title || 'Untitled task')}</strong>
                            <p>${h.escapeHtml(task.project_name || 'No project')}</p>
                          </div>
                          <span class="status-badge ${h.escapeHtml(task.status || 'pending')}">${h.escapeHtml(task.status || 'pending')}</span>
                        </div>
                      `
                    )
                    .join('')}</div>`
                : '<p class="detail-empty">No tasks assigned yet.</p>'
            }
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-outline" type="button">Close</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const close = () => closeEmployeeDetailsDialog();
    overlay.querySelector('.modal-close').addEventListener('click', close);
    overlay.querySelector('.btn-outline').addEventListener('click', close);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        close();
      }
    });
  }

  window.openEmployeeDetails = openEmployeeDetails;
})();
