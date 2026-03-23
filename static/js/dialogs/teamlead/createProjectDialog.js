let tlCreateProjectDialog = null;
let tlCreateEmployees = [];
let tlCreateEscHandlerBound = false;

function openTLCreateProjectDialog() {
  if (!tlCreateProjectDialog) {
    createTLCreateProjectDialog();
  }
  tlCreateProjectDialog.style.display = 'flex';
  loadTLCreateDialogData();
}

function createTLCreateProjectDialog() {
  tlCreateProjectDialog = document.createElement('div');
  tlCreateProjectDialog.className = 'modal-overlay';
  tlCreateProjectDialog.style.display = 'none';
  tlCreateProjectDialog.innerHTML = `
    <div class="modal modal-lg create-project-dialog" role="dialog" aria-modal="true" aria-labelledby="tl-create-project-title">
      <div class="modal-header">
        <div>
          <h3 id="tl-create-project-title">Create Project</h3>
          <p class="modal-subtitle">Define a new project and add team members.</p>
        </div>
        <button class="modal-close" type="button" aria-label="Close" onclick="closeTLCreateProjectDialog()">&times;</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label" for="tlProjectName">Project Name *</label>
          <input id="tlProjectName" class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label" for="tlProjectDesc">Description</label>
          <textarea id="tlProjectDesc" class="form-textarea"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="tlDeadline">Deadline</label>
            <input type="date" id="tlDeadline" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label" for="tlStatus">Status</label>
            <select id="tlStatus" class="form-select">
              <option value="planning" selected>Planning</option>
              <option value="active">Active</option>
              <option value="on-hold">On Hold</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" for="tlMembers">Team Members</label>
          <select id="tlMembers" multiple class="form-select"></select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" type="button" onclick="closeTLCreateProjectDialog()">Cancel</button>
        <button class="btn btn-primary" type="button" onclick="tlCreateProject()" id="tlCreateProjectBtn">Create</button>
      </div>
    </div>`;
  document.body.appendChild(tlCreateProjectDialog);

  tlCreateProjectDialog.addEventListener('click', (e) => {
    if (e.target === tlCreateProjectDialog) closeTLCreateProjectDialog();
  });

  if (!tlCreateEscHandlerBound) {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && tlCreateProjectDialog && tlCreateProjectDialog.style.display === 'flex') {
        closeTLCreateProjectDialog();
      }
    });
    tlCreateEscHandlerBound = true;
  }
}

function closeTLCreateProjectDialog() {
  if (tlCreateProjectDialog) {
    tlCreateProjectDialog.style.display = 'none';
  }
}

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function loadTLCreateDialogData() {
  try {
    const deadline = document.getElementById('tlDeadline');
    if (deadline) deadline.min = new Date().toISOString().split('T')[0];

    const res = await fetch('/api/teamlead/employees');
    if (!res.ok) throw new Error('Failed to load employees');
    tlCreateEmployees = await res.json();
    const sel = document.getElementById('tlMembers');
    if (!sel) return;
    sel.innerHTML = tlCreateEmployees.map((e) =>
      `<option value="${escapeHtml(e.id)}">${escapeHtml(e.name)} - ${escapeHtml(e.position)}</option>`
    ).join('');
  } catch (e) {
    console.error(e);
    window.teamLeadDashboard?.showNotification('Error loading employees', 'error');
  }
}

async function tlCreateProject() {
  const name = document.getElementById('tlProjectName').value;
  const description = document.getElementById('tlProjectDesc').value;
  const deadline = document.getElementById('tlDeadline').value;
  const status = document.getElementById('tlStatus').value;
  const members = Array.from(document.getElementById('tlMembers').selectedOptions).map((o) => o.value);
  if (!name) {
    return window.teamLeadDashboard?.showNotification('Project name is required', 'error');
  }
  const btn = document.getElementById('tlCreateProjectBtn');
  btn.disabled = true;
  btn.textContent = 'Creating...';
  try {
    const res = await fetch('/api/teamlead/projects/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, deadline, status, teamMembers: members })
    });
    if (!res.ok) throw new Error('Failed');
    window.teamLeadDashboard?.showNotification('Project created', 'success');
    closeTLCreateProjectDialog();
    window.teamLeadDashboard?.refreshData();
  } catch (e) {
    console.error(e);
    window.teamLeadDashboard?.showNotification('Error creating project', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create';
  }
}

window.openTLCreateProjectDialog = openTLCreateProjectDialog;
window.closeTLCreateProjectDialog = closeTLCreateProjectDialog;
window.tlCreateProject = tlCreateProject;
