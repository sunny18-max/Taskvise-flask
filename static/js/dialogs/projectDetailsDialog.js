(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  function closeProjectDetailsDialog() {
    const modal = document.getElementById('project-details-modal');
    if (modal) {
      modal.remove();
    }
  }

  function openProjectDetailsDialog(projectId, projects, employees, tasks) {
    const h = helpers();
    if (!h) {
      return;
    }

    const projectList = projects || h.getDashboardCollection('projects');
    const employeeList = employees || h.getDashboardCollection('employees');
    const taskList = tasks || h.getDashboardCollection('tasks');
    const project = (projectList || []).find((item) => String(item.id) === String(projectId));
    if (!project) {
      h.notify('Project not found', 'error');
      return;
    }

    const teamMemberIds = h.parseTeamMembers(project);
    const teamMembers = teamMemberIds.map((memberId) => ({
      id: memberId,
      name: h.getEmployeeName(memberId, employeeList) || memberId,
    }));
    const relatedTasks = (taskList || []).filter((task) => String(task.project_id || '') === String(project.id));
    const completedTasks = relatedTasks.filter((task) => String(task.status || '').toLowerCase() === 'completed').length;

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'project-details-modal';
    overlay.innerHTML = `
      <div class="modal modal-lg details-modal" role="dialog" aria-modal="true" aria-labelledby="project-details-title">
        <div class="modal-header">
          <div>
            <h3 id="project-details-title">${h.escapeHtml(project.name || 'Project')}</h3>
            <p class="modal-subtitle">${h.escapeHtml(project.description || 'No description provided')}</p>
          </div>
          <button class="modal-close" type="button" aria-label="Close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="details-grid">
            <div class="detail-card">
              <span class="detail-label">Status</span>
              <span class="status-badge ${h.escapeHtml(project.status || 'planning')}">${h.escapeHtml(project.status || 'planning')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Deadline</span>
              <span class="detail-value">${h.escapeHtml(project.deadline || project.end_date || 'Not set')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Owner</span>
              <span class="detail-value">${h.escapeHtml(project.owner_name || 'Unassigned')}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Company</span>
              <span class="detail-value">${h.escapeHtml(project.company || h.getDefaultCompanyName())}</span>
            </div>
            <div class="detail-card">
              <span class="detail-label">Progress</span>
              <span class="detail-value">${h.escapeHtml(String(project.progress || 0))}%</span>
            </div>
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Project Health</h4>
              <span>${completedTasks}/${relatedTasks.length} tasks completed</span>
            </div>
            <div class="detail-progress">
              <div class="detail-progress-bar">
                <span style="width:${Math.max(0, Math.min(100, Number(project.progress || 0)))}%"></span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Team Members</h4>
              <span>${teamMembers.length}</span>
            </div>
            ${
              teamMembers.length
                ? `<div class="tag-list">${teamMembers
                    .map((member) => `<span class="member-tag">${h.escapeHtml(member.name)}</span>`)
                    .join('')}</div>`
                : '<p class="detail-empty">No team members assigned yet.</p>'
            }
          </div>

          <div class="detail-section">
            <div class="detail-section-header">
              <h4>Recent Tasks</h4>
              <span>${relatedTasks.length}</span>
            </div>
            ${
              relatedTasks.length
                ? `<div class="detail-list">${relatedTasks
                    .slice(0, 5)
                    .map(
                      (task) => `
                        <div class="detail-list-item">
                          <div>
                            <strong>${h.escapeHtml(task.title || 'Untitled task')}</strong>
                            <p>${h.escapeHtml(task.assignee_name || 'Unassigned')}</p>
                          </div>
                          <span class="status-badge ${h.escapeHtml(task.status || 'pending')}">${h.escapeHtml(task.status || 'pending')}</span>
                        </div>
                      `
                    )
                    .join('')}</div>`
                : '<p class="detail-empty">No tasks linked to this project.</p>'
            }
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" type="button">Close</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const close = () => closeProjectDetailsDialog();
    overlay.querySelector('.modal-close').addEventListener('click', close);
    overlay.querySelector('.btn-outline').addEventListener('click', close);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        close();
      }
    });
  }

  window.openProjectDetailsDialog = openProjectDetailsDialog;
})();
