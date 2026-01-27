// Employee Details Dialog
function openEmployeeDetails(employeeId, employees) {
  const normalizeId = (v) => String(v || '').trim();
  const employee = (employees || []).find(emp => normalizeId(emp.id) === normalizeId(employeeId));
  if (!employee) {
    // Fallback: try managerDashboard method first
    if (window.managerDashboard && typeof window.managerDashboard.getEmployees === 'function') {
      window.managerDashboard.getEmployees().then(list => retryOpen(employeeId, list));
      return;
    }
    // Final fallback: direct fetch to API
    fetch('/api/manager/employees')
      .then(r => r.ok ? r.json() : [])
      .then(list => retryOpen(employeeId, list))
      .catch(() => showNotification('Employee not found', 'error'));
    return;
  }

  function retryOpen(id, list) {
    const found = (list || []).find(emp => normalizeId(emp.id) === normalizeId(id));
    if (found) {
      openEmployeeDetails(id, list);
    } else {
      showNotification('Employee not found', 'error');
    }
  }

  // Create dialog overlay
  const overlay = document.createElement('div');
  overlay.className = 'dialog-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  `;

  const fullName = employee.fullName || employee.name || 'Employee';
  const role = employee.role || employee.position || '';
  const department = employee.department || '';
  const email = employee.email || '';
  const initials = fullName.split(' ').map(n => n[0]).join('').toUpperCase();

  // Compute stats from current dashboard tasks if available
  let tasks = [];
  try {
    if (window.managerDashboard && Array.isArray(window.managerDashboard.tasks)) {
      tasks = window.managerDashboard.tasks;
    }
  } catch {}
  const myTasks = tasks.filter(t => String(t.assignee_id) === normalizeId(employee.id));
  const completed = myTasks.filter(t => (t.status || '').toLowerCase() === 'completed').length;
  const total = myTasks.length;
  const productivity = total > 0 ? Math.floor((completed / total) * 100) : 0;

  // Create dialog content
  const dialog = document.createElement('div');
  dialog.className = 'dialog-content';
  dialog.style.cssText = `
    background: white;
    padding: 24px;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  `;

  dialog.innerHTML = `
    <div class="dialog-header" style="margin-bottom: 20px;">
      <h2 style="font-size: 1.5rem; font-weight: 600; margin: 0;">Employee Details</h2>
    </div>
    
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1.125rem;">
          ${initials}
        </div>
        <div>
          <h3 style="font-size: 1.25rem; font-weight: 600; margin: 0 0 4px 0;">${fullName}</h3>
          <p style="color: #6b7280; margin: 0 0 4px 0;">${role}</p>
          <p style="color: #6b7280; margin: 0; font-size: 0.875rem;">${department}</p>
        </div>
      </div>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 0.875rem;">
        <div>
          <p style="color: #6b7280; margin: 0 0 4px 0;">Email</p>
          <p style="font-weight: 500; margin: 0;">${email}</p>
        </div>
        <div>
          <p style="color: #6b7280; margin: 0 0 4px 0;">Productivity</p>
          <p style="font-weight: 500; margin: 0;">${productivity}%</p>
        </div>
        <div>
          <p style="color: #6b7280; margin: 0 0 4px 0;">Total Tasks</p>
          <p style="font-weight: 500; margin: 0;">${completed}/${total}</p>
        </div>
        <div>
          <p style="color: #6b7280; margin: 0 0 4px 0;">Total Hours</p>
          <p style="font-weight: 500; margin: 0;">0h</p>
        </div>
      </div>
      
      <div>
        <p style="color: #6b7280; font-size: 0.875rem; margin: 0 0 8px 0;">Performance</p>
        <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
          <div style="background: #10b981; height: 100%; width: ${productivity}%;"></div>
        </div>
      </div>
      
      <div>
        <p style="color: #6b7280; font-size: 0.875rem; margin: 0 0 8px 0;">Last Active</p>
        <p style="font-weight: 500; margin: 0;">${employee.last_login ? new Date(employee.last_login).toLocaleString() : 'N/A'}</p>
      </div>
    </div>
    
    <div style="display: flex; justify-content: flex-end; margin-top: 24px;">
      <button 
        id="closeBtn" 
        style="padding: 8px 16px; border: none; border-radius: 4px; background: #3b82f6; color: white; cursor: pointer;"
      >
        Close
      </button>
    </div>
  `;

  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  function closeDialog() {
    document.body.removeChild(overlay);
  }

  document.getElementById('closeBtn').addEventListener('click', closeDialog);
  
  // Close on overlay click
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      closeDialog();
    }
  });
}

window.openEmployeeDetails = openEmployeeDetails;