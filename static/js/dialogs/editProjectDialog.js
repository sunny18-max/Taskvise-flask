// Minimal, robust Edit Project Dialog
// Usage: openEditProjectDialog(projectId, projects, _employeesIgnored, updateProjectCallback)
// updateProjectCallback(projectId, { name, description, status, deadline, progress })

(function(){
  function openEditProjectDialog(projectId, projects, _employeesIgnored, updateProjectCallback) {
    try {
      const project = (projects || []).find(p => String(p.id) === String(projectId));
      if (!project) {
        showNotification(`Project not found: ${projectId}`, 'error');
        return;
      }

      // Normalize fields
      const deadlineStr = (project.deadline || project.endDate || project.end_date || '').toString().split('T')[0];
      const edited = {
        name: project.name || '',
        description: project.description || '',
        status: (project.status || 'planning').toLowerCase(),
        deadline: deadlineStr,
        progress: parseInt(project.progress || 0) || 0
      };

      // Build modal
      const overlay = document.createElement('div');
      overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:10000;';
      const modal = document.createElement('div');
      modal.style.cssText = 'background:#fff;border-radius:12px;box-shadow:0 20px 45px rgba(2,6,23,.16);width:92%;max-width:640px;max-height:90vh;overflow:auto;';
      modal.innerHTML = `
        <div style="padding:20px;border-bottom:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
          <h3 style="margin:0;font-size:1.1rem;font-weight:700;color:#111827;">Edit Project</h3>
          <button id="epx" style="background:none;border:0;font-size:1.25rem;color:#64748b;cursor:pointer">×</button>
        </div>
        <div style="padding:20px;display:flex;flex-direction:column;gap:14px;">
          <div>
            <label style="display:block;margin:0 0 6px 0;font-weight:500;color:#374151;">Project Name *</label>
            <input id="ep-name" class="form-input" value="${escapeHtml(edited.name)}" placeholder="Enter project name">
          </div>
          <div>
            <label style="display:block;margin:0 0 6px 0;font-weight:500;color:#374151;">Description</label>
            <textarea id="ep-desc" class="form-input" style="min-height:96px;">${escapeHtml(edited.description)}</textarea>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
            <div>
              <label style="display:block;margin:0 0 6px 0;font-weight:500;color:#374151;">Deadline *</label>
              <input type="date" id="ep-deadline" class="form-input" value="${escapeHtml(edited.deadline)}">
            </div>
            <div>
              <label style="display:block;margin:0 0 6px 0;font-weight:500;color:#374151;">Status</label>
              <select id="ep-status" class="form-input">
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on-hold">On Hold</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
          <div>
            <label style="display:block;margin:0 0 6px 0;font-weight:500;color:#374151;">Progress</label>
            <input type="range" id="ep-progress" min="0" max="100" value="${edited.progress}" style="width:100%;accent-color:#3b82f6;">
          </div>
          <div id="ep-err" style="display:none;color:#b91c1c;font-size:.875rem;"></div>
        </div>
        <div style="padding:16px 20px;border-top:1px solid #e5e7eb;display:flex;gap:10px;justify-content:flex-end;">
          <button id="ep-cancel" class="btn btn-outline" style="padding:.6rem 1rem;border-radius:8px;">Cancel</button>
          <button id="ep-save" class="btn btn-primary" style="padding:.6rem 1rem;border-radius:8px;">Update Project</button>
        </div>
      `;
      overlay.appendChild(modal);
      document.body.appendChild(overlay);

      // Set selects
      modal.querySelector('#ep-status').value = edited.status;

      function close(){ document.body.removeChild(overlay); }
      modal.querySelector('#epx').onclick = close;
      modal.querySelector('#ep-cancel').onclick = (e)=>{ e.preventDefault(); close(); };
      overlay.addEventListener('click', (e)=>{ if (e.target===overlay) close(); });
      modal.addEventListener('keydown', (e)=>{ if (e.key==='Escape') close(); });

      modal.querySelector('#ep-save').onclick = async (e)=>{
        e.preventDefault();
        const err = modal.querySelector('#ep-err');
        err.style.display='none'; err.textContent='';
        const payload = {
          name: modal.querySelector('#ep-name').value.trim(),
          description: modal.querySelector('#ep-desc').value.trim(),
          status: modal.querySelector('#ep-status').value,
          deadline: modal.querySelector('#ep-deadline').value,
          progress: parseInt(modal.querySelector('#ep-progress').value)||0
        };
        if (!payload.name || !payload.deadline) { err.textContent='Please fill required fields'; err.style.display='block'; return; }
        try {
          const ok = await (updateProjectCallback && updateProjectCallback(projectId, payload));
          if (!ok) throw new Error('Update failed');
          if (window.managerDashboard && window.managerDashboard.showNotification) {
            window.managerDashboard.showNotification('Project updated successfully','success');
          }
          close();
        } catch (ex) {
          if (window.managerDashboard && window.managerDashboard.showNotification) {
            window.managerDashboard.showNotification('Failed to update project','error');
          }
        }
      };
    } catch (e) {
      try { window.managerDashboard && window.managerDashboard.showNotification('Failed to open edit project dialog','error'); } catch(_) {}
    }
  }

  function escapeHtml(s){
    return String(s||'').replace(/[&<>"]+/g, c=>({"&":"&amp;","<":"&lt;",
    ">":"&gt;","\"":"&quot;"}[c]));
  }

  window.openEditProjectDialog = openEditProjectDialog;
  })();