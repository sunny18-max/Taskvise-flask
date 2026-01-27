// Team Lead Create Project Dialog
let tlCreateProjectDialog = null;
let tlCreateEmployees = [];

function openTLCreateProjectDialog(){
  if(!tlCreateProjectDialog){ createTLCreateProjectDialog(); }
  tlCreateProjectDialog.style.display = 'flex';
  loadTLCreateDialogData();
}

function createTLCreateProjectDialog(){
  tlCreateProjectDialog = document.createElement('div');
  tlCreateProjectDialog.className = 'dialog-overlay';
  tlCreateProjectDialog.innerHTML = `
    <div class="dialog create-project-dialog">
      <div class="dialog-header">
        <h2 class="dialog-title">Create Project</h2>
        <p class="dialog-description">Define a new project and add members</p>
        <button class="dialog-close" onclick="closeTLCreateProjectDialog()">×</button>
      </div>
      <div class="dialog-content">
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
      <div class="dialog-actions">
        <button class="btn btn-outline" onclick="closeTLCreateProjectDialog()">Cancel</button>
        <button class="btn btn-primary" onclick="tlCreateProject()" id="tlCreateProjectBtn">Create</button>
      </div>
    </div>`;
  document.body.appendChild(tlCreateProjectDialog);
}

function closeTLCreateProjectDialog(){ if(tlCreateProjectDialog){ tlCreateProjectDialog.style.display='none'; } }

async function loadTLCreateDialogData(){
  try{
    const res = await fetch('/api/teamlead/employees');
    tlCreateEmployees = await res.json();
    const sel = document.getElementById('tlMembers');
    sel.innerHTML = tlCreateEmployees.map(e=>`<option value="${e.id}">${e.name} - ${e.position}</option>`).join('');
  }catch(e){ console.error(e); window.teamLeadDashboard?.showNotification('Error loading employees','error'); }
}

async function tlCreateProject(){
  const name = document.getElementById('tlProjectName').value;
  const description = document.getElementById('tlProjectDesc').value;
  const deadline = document.getElementById('tlDeadline').value;
  const status = document.getElementById('tlStatus').value;
  const members = Array.from(document.getElementById('tlMembers').selectedOptions).map(o=>o.value);
  if(!name){ return window.teamLeadDashboard?.showNotification('Project name is required','error'); }
  const btn = document.getElementById('tlCreateProjectBtn');
  btn.disabled = true; btn.textContent = 'Creating...';
  try{
    const res = await fetch('/api/teamlead/projects/create', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ name, description, deadline, status, teamMembers: members }) });
    if(!res.ok) throw new Error('Failed');
    window.teamLeadDashboard?.showNotification('Project created','success');
    closeTLCreateProjectDialog();
    window.teamLeadDashboard?.refreshData();
  }catch(e){ console.error(e); window.teamLeadDashboard?.showNotification('Error creating project','error'); }
  finally{ btn.disabled=false; btn.textContent='Create'; }
}

window.openTLCreateProjectDialog = openTLCreateProjectDialog;
window.closeTLCreateProjectDialog = closeTLCreateProjectDialog;
window.tlCreateProject = tlCreateProject;
