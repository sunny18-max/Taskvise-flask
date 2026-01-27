// Team Lead Assign Task Dialog
let tlAssignTaskDialog = null;
let tlEmployees = [];
let tlProjects = [];

function openTLAssignTaskDialog(){
  if(!tlAssignTaskDialog){ createTLAssignTaskDialog(); }
  tlAssignTaskDialog.style.display = 'flex';
  loadTLAssignTaskDialogData();
}

function createTLAssignTaskDialog(){
  tlAssignTaskDialog = document.createElement('div');
  tlAssignTaskDialog.className = 'dialog-overlay';
  tlAssignTaskDialog.innerHTML = `
    <div class="dialog assign-task-dialog">
      <div class="dialog-header">
        <h2 class="dialog-title">Assign New Task</h2>
        <p class="dialog-description">Create and assign a new task to a team member</p>
        <button class="dialog-close" onclick="closeTLAssignTaskDialog()">×</button>
      </div>
      <div class="dialog-content">
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
      <div class="dialog-actions">
        <button class="btn btn-outline" onclick="closeTLAssignTaskDialog()">Cancel</button>
        <button class="btn btn-primary" onclick="tlAssignTask()" id="tlAssignTaskBtn">Assign Task</button>
      </div>
    </div>`;
  document.body.appendChild(tlAssignTaskDialog);
}

function closeTLAssignTaskDialog(){
  if(tlAssignTaskDialog){ tlAssignTaskDialog.style.display = 'none'; }
}

async function loadTLAssignTaskDialogData(){
  try{
    const employeesResponse = await fetch('/api/teamlead/employees');
    tlEmployees = await employeesResponse.json();
    const assignedTo = document.getElementById('tlAssignedTo');
    assignedTo.innerHTML = '<option value="">Select employee</option>' + tlEmployees.map(e=>`<option value="${e.id}">${e.name} - ${e.position}</option>`).join('');

    const projectsResponse = await fetch('/api/teamlead/projects');
    tlProjects = await projectsResponse.json();
    const projectSelect = document.getElementById('tlProject');
    projectSelect.innerHTML = '<option value="">Select project</option>' + tlProjects.map(p=>`<option value="${p.id}">${p.name}</option>`).join('');
  }catch(err){
    console.error(err);
    if(window.teamLeadDashboard) window.teamLeadDashboard.showNotification('Error loading dialog data','error');
  }
}

async function tlAssignTask(){
  const payload = {
    title: document.getElementById('tlTaskTitle').value,
    description: document.getElementById('tlTaskDescription').value,
    assignedTo: document.getElementById('tlAssignedTo').value,
    project: document.getElementById('tlProject').value,
    priority: document.getElementById('tlPriority').value,
    due_date: document.getElementById('tlDueDate').value
  };
  if(!payload.title || !payload.assignedTo || !payload.due_date){
    return window.teamLeadDashboard?.showNotification('Please fill required fields','error');
  }
  const btn = document.getElementById('tlAssignTaskBtn');
  btn.disabled = true; btn.textContent = 'Assigning...';
  try{
    const res = await fetch('/api/teamlead/tasks/assign', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    if(!res.ok) throw new Error('Failed');
    window.teamLeadDashboard?.showNotification('Task assigned','success');
    closeTLAssignTaskDialog();
    window.teamLeadDashboard?.refreshData();
  }catch(e){
    console.error(e);
    window.teamLeadDashboard?.showNotification('Error assigning task','error');
  }finally{
    btn.disabled = false; btn.textContent = 'Assign Task';
  }
}

window.openTLAssignTaskDialog = openTLAssignTaskDialog;
window.closeTLAssignTaskDialog = closeTLAssignTaskDialog;
window.tlAssignTask = tlAssignTask;
