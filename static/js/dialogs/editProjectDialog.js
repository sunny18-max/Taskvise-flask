(function () {
  const helpers = () => window.TaskViseDashboardHelpers;

  function normalizeProjectArgs(projectId, projects, employees, updateProjectCallback) {
    let projectList = Array.isArray(projects) ? projects : null;
    let employeeList = Array.isArray(employees) ? employees : null;
    let callback = typeof updateProjectCallback === 'function' ? updateProjectCallback : null;

    if (!projectList || !employeeList) {
      const h = helpers();
      projectList = projectList || h.getDashboardCollection('projects');
      employeeList = employeeList || h.getDashboardCollection('employees');
    }

    return { projectId, projectList, employeeList, callback };
  }

  function closeEditProjectDialog() {
    const modal = document.getElementById('edit-project-modal');
    if (modal) {
      modal.remove();
    }
  }

  function renderTeamMembers(selectedIds, employees) {
    const h = helpers();
    const employeeMap = h.buildEmployeeMap(employees);
    const container = document.getElementById('ep-selected-members');
    if (!container) {
      return;
    }
    if (!selectedIds.length) {
      container.innerHTML = '<p class="detail-empty">No team members selected.</p>';
      return;
    }
    container.innerHTML = selectedIds
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
        const nextValue = (document.getElementById('ep-team-data').value || '').split(',').filter(Boolean);
        const filtered = nextValue.filter((memberId) => memberId !== button.dataset.memberId);
        document.getElementById('ep-team-data').value = filtered.join(',');
        renderTeamMembers(filtered, employees);
      });
    });
  }

  async function openEditProjectDialog(projectId, projects, employees, updateProjectCallback) {
    const h = helpers();
    const context = h.getDashboardContext();
    const args = normalizeProjectArgs(projectId, projects, employees, updateProjectCallback);
    if ((!args.projectList || !args.projectList.length) && context.dashboard && typeof context.dashboard.getProjects === 'function') {
      args.projectList = await context.dashboard.getProjects();
    }
    if ((!args.employeeList || !args.employeeList.length) && context.dashboard && typeof context.dashboard.getEmployees === 'function') {
      args.employeeList = await context.dashboard.getEmployees();
    }
    const project = (args.projectList || []).find((item) => String(item.id) === String(args.projectId));
    if (!project) {
      h.notify('Project not found', 'error');
      return;
    }

    const selectedMembers = h.parseTeamMembers(project);
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'edit-project-modal';
    overlay.innerHTML = `
      <div class="modal modal-lg" role="dialog" aria-modal="true" aria-labelledby="edit-project-title">
        <div class="modal-header">
          <div>
            <h3 id="edit-project-title">Edit Project</h3>
            <p class="modal-subtitle">Update scope, owner, delivery date, and team.</p>
          </div>
          <button class="modal-close" type="button" aria-label="Close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="ep-name">Project Name *</label>
            <input id="ep-name" class="form-input" type="text" value="${h.escapeHtml(project.name || '')}">
          </div>
          <div class="form-group">
            <label for="ep-description">Description</label>
            <textarea id="ep-description" class="form-textarea">${h.escapeHtml(project.description || '')}</textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="ep-company">Company</label>
              <input id="ep-company" class="form-input" type="text" value="${h.escapeHtml(project.company || h.getDefaultCompanyName())}">
            </div>
            <div class="form-group">
              <label for="ep-deadline">Deadline *</label>
              <input id="ep-deadline" class="form-input" type="date" value="${h.escapeHtml(project.deadline || project.end_date || '')}">
            </div>
            <div class="form-group">
              <label for="ep-status">Status</label>
              <select id="ep-status" class="form-select">
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on-hold">On Hold</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="ep-owner">Owner</label>
              <select id="ep-owner" class="form-select">
                <option value="">Select project owner</option>
                ${args.employeeList
                  .map((employee) => `<option value="${h.escapeHtml(employee.id)}">${h.escapeHtml(employee.name)} - ${h.escapeHtml(employee.position || employee.role || '')}</option>`)
                  .join('')}
              </select>
            </div>
            <div class="form-group">
              <label for="ep-progress">Progress</label>
              <input id="ep-progress" class="form-input" type="number" min="0" max="100" value="${h.escapeHtml(String(project.progress || 0))}">
            </div>
          </div>
          <div class="form-group">
            <label for="ep-team-members">Team Members</label>
            <select id="ep-team-members" class="form-select">
              <option value="">Add team member</option>
              ${args.employeeList
                .map((employee) => `<option value="${h.escapeHtml(employee.id)}">${h.escapeHtml(employee.name)} - ${h.escapeHtml(employee.position || employee.role || '')}</option>`)
                .join('')}
            </select>
            <input id="ep-team-data" type="hidden" value="${h.escapeHtml(selectedMembers.join(','))}">
            <div id="ep-selected-members" class="tag-list" style="margin-top:0.75rem;"></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" type="button">Cancel</button>
          <button class="btn btn-primary" type="button" id="ep-save">Save Changes</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const statusSelect = document.getElementById('ep-status');
    const ownerSelect = document.getElementById('ep-owner');
    statusSelect.value = String(project.status || 'planning').toLowerCase();
    ownerSelect.value = String(project.owner_id || '');
    renderTeamMembers(selectedMembers, args.employeeList);

    const teamSelect = document.getElementById('ep-team-members');
    teamSelect.addEventListener('change', (event) => {
      const nextMemberId = String(event.target.value || '').trim();
      if (!nextMemberId) {
        return;
      }
      const current = (document.getElementById('ep-team-data').value || '').split(',').filter(Boolean);
      const next = h.uniqueStrings([...current, nextMemberId]);
      document.getElementById('ep-team-data').value = next.join(',');
      event.target.value = '';
      renderTeamMembers(next, args.employeeList);
    });

    const close = () => closeEditProjectDialog();
    overlay.querySelector('.modal-close').addEventListener('click', close);
    overlay.querySelector('.btn-outline').addEventListener('click', close);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        close();
      }
    });

    document.getElementById('ep-save').addEventListener('click', async () => {
      const payload = {
        name: document.getElementById('ep-name').value.trim(),
        description: document.getElementById('ep-description').value.trim(),
        company: document.getElementById('ep-company').value.trim(),
        deadline: document.getElementById('ep-deadline').value,
        status: document.getElementById('ep-status').value,
        owner_id: document.getElementById('ep-owner').value,
        progress: document.getElementById('ep-progress').value,
        teamMembers: (document.getElementById('ep-team-data').value || '').split(',').filter(Boolean),
      };
      if (!payload.name || !payload.deadline) {
        h.notify('Project name and deadline are required.', 'error');
        return;
      }

      const saveButton = document.getElementById('ep-save');
      saveButton.disabled = true;
      saveButton.textContent = 'Saving...';

      try {
        if (args.callback) {
          const ok = await args.callback(args.projectId, payload);
          if (!ok) {
            throw new Error('Failed to update project');
          }
        } else {
          await h.requestJson(`${context.apiBase}/projects/${encodeURIComponent(args.projectId)}`, {
            method: 'PUT',
            body: payload,
          });
        }
        h.notify('Project updated successfully', 'success');
        close();
        await h.refreshView();
      } catch (error) {
        console.error(error);
        h.notify(error.message || 'Failed to update project', 'error');
      } finally {
        saveButton.disabled = false;
        saveButton.textContent = 'Save Changes';
      }
    });
  }

  window.openEditProjectDialog = openEditProjectDialog;
})();
