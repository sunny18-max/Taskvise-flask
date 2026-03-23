let tlAssignTaskDialog = null;
let tlEmployees = [];
let tlProjects = [];
let tlAssignEscHandlerBound = false;

function openTLAssignTaskDialog() {
  if (!tlAssignTaskDialog) {
    createTLAssignTaskDialog();
  }
  tlAssignTaskDialog.style.display = 'flex';
  loadTLAssignTaskDialogData();
}

function createTLAssignTaskDialog() {
  tlAssignTaskDialog = document.createElement('div');
  tlAssignTaskDialog.className = 'modal-overlay';
  tlAssignTaskDialog.style.display = 'none';
  tlAssignTaskDialog.innerHTML = `
    <div class="modal modal-lg assign-task-dialog" role="dialog" aria-modal="true" aria-labelledby="tl-assign-task-title">
      <div class="modal-header">
        <div>
          <h3 id="tl-assign-task-title">Assign New Task</h3>
          <p class="modal-subtitle">Create and assign a new task to a team member.</p>
        </div>
        <button class="modal-close" type="button" aria-label="Close" onclick="closeTLAssignTaskDialog()">&times;</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label" for="tlTaskTitle">Task Title *</label>
          <input id="tlTaskTitle" class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label" for="tlTaskDescription">Description</label>
          <textarea id="tlTaskDescription" class="form-textarea"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="tlAssignedTo">Assign To *</label>
            <select id="tlAssignedTo" class="form-select"></select>
          </div>
          <div class="form-group">
            <label class="form-label" for="tlPriority">Priority</label>
            <select id="tlPriority" class="form-select">
              <option value="low">Low</option>
              <option value="medium" selected>Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="tlDueDate">Due Date *</label>
            <input type="date" id="tlDueDate" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label" for="tlProject">Project</label>
            <select id="tlProject" class="form-select"></select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" type="button" onclick="closeTLAssignTaskDialog()">Cancel</button>
        <button class="btn btn-primary" type="button" onclick="tlAssignTask()" id="tlAssignTaskBtn">Assign Task</button>
      </div>
    </div>`;
  document.body.appendChild(tlAssignTaskDialog);

  tlAssignTaskDialog.addEventListener('click', (e) => {
    if (e.target === tlAssignTaskDialog) closeTLAssignTaskDialog();
  });

  if (!tlAssignEscHandlerBound) {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && tlAssignTaskDialog && tlAssignTaskDialog.style.display === 'flex') {
        closeTLAssignTaskDialog();
      }
    });
    tlAssignEscHandlerBound = true;
  }
}

function closeTLAssignTaskDialog() {
  if (!tlAssignTaskDialog) return;
  tlAssignTaskDialog.style.display = 'none';
}

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function loadTLAssignTaskDialogData() {
  try {
    const dueDate = document.getElementById('tlDueDate');
    if (dueDate) dueDate.min = new Date().toISOString().split('T')[0];

    const employeesResponse = await fetch('/api/teamlead/employees');
    if (!employeesResponse.ok) throw new Error('Failed to load employees');
    tlEmployees = await employeesResponse.json();
    const assignedTo = document.getElementById('tlAssignedTo');
    if (assignedTo) {
      assignedTo.innerHTML = '<option value="">Select employee</option>' +
        tlEmployees.map((e) => `<option value="${escapeHtml(e.id)}">${escapeHtml(e.name)} - ${escapeHtml(e.position)}</option>`).join('');
    }

    const projectsResponse = await fetch('/api/teamlead/projects');
    if (!projectsResponse.ok) throw new Error('Failed to load projects');
    tlProjects = await projectsResponse.json();
    const projectSelect = document.getElementById('tlProject');
    if (projectSelect) {
      projectSelect.innerHTML = '<option value="">Select project</option>' +
        tlProjects.map((p) => `<option value="${escapeHtml(p.id)}">${escapeHtml(p.name)}</option>`).join('');
    }
  } catch (err) {
    console.error(err);
    if (window.teamLeadDashboard) window.teamLeadDashboard.showNotification('Error loading dialog data', 'error');
  }
}

async function tlAssignTask() {
  const payload = {
    title: document.getElementById('tlTaskTitle').value,
    description: document.getElementById('tlTaskDescription').value,
    assignedTo: document.getElementById('tlAssignedTo').value,
    project: document.getElementById('tlProject').value,
    priority: document.getElementById('tlPriority').value,
    due_date: document.getElementById('tlDueDate').value
  };

  if (!payload.title || !payload.assignedTo || !payload.due_date) {
    return window.teamLeadDashboard?.showNotification('Please fill required fields', 'error');
  }

  const btn = document.getElementById('tlAssignTaskBtn');
  btn.disabled = true;
  btn.textContent = 'Assigning...';
  try {
    const res = await fetch('/api/teamlead/tasks/assign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed');
    window.teamLeadDashboard?.showNotification('Task assigned', 'success');
    closeTLAssignTaskDialog();
    window.teamLeadDashboard?.refreshData();
  } catch (e) {
    console.error(e);
    window.teamLeadDashboard?.showNotification('Error assigning task', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Assign Task';
  }
}

window.openTLAssignTaskDialog = openTLAssignTaskDialog;
window.closeTLAssignTaskDialog = closeTLAssignTaskDialog;
window.tlAssignTask = tlAssignTask;
