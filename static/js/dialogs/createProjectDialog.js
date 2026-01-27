// Create Project Dialog
let createProjectDialog = null;
let selectedTeamMembers = [];

function openCreateProjectDialog() {
    if (!createProjectDialog) {
        createCreateProjectDialog();
    }
    selectedTeamMembers = [];
    createProjectDialog.style.display = 'flex';
    loadCreateProjectDialogData();
}

function createCreateProjectDialog() {
    createProjectDialog = document.createElement('div');
    createProjectDialog.className = 'dialog-overlay';
    createProjectDialog.innerHTML = `
        <div class="dialog create-project-dialog">
            <div class="dialog-header">
                <h2 class="dialog-title">Create New Project</h2>
                <p class="dialog-description">Set up a new project and assign team members</p>
                <button class="dialog-close" onclick="closeCreateProjectDialog()">×</button>
            </div>
            
            <div class="dialog-content">
                <div class="form-group">
                    <label for="projectName" class="form-label">Project Name *</label>
                    <input type="text" id="projectName" class="form-input" placeholder="Enter project name">
                </div>
                
                <div class="form-group">
                    <label for="projectDescription" class="form-label">Description</label>
                    <textarea id="projectDescription" class="form-textarea" placeholder="Enter project description"></textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="projectDeadline" class="form-label">Deadline *</label>
                        <input type="date" id="projectDeadline" class="form-input">
                    </div>
                    
                    <div class="form-group">
                        <label for="projectStatus" class="form-label">Status</label>
                        <select id="projectStatus" class="form-select">
                            <option value="planning">Planning</option>
                            <option value="active">Active</option>
                            <option value="on-hold">On Hold</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="teamMembers" class="form-label">Team Members</label>
                    <select id="teamMembers" class="form-select">
                        <option value="">Add team members</option>
                    </select>
                    <div id="selectedMembers" class="selected-members"></div>
                </div>
            </div>
            
            <div class="dialog-actions">
                <button class="btn btn-outline" onclick="closeCreateProjectDialog()">Cancel</button>
                <button class="btn btn-primary" onclick="createProject()" id="createProjectBtn">Create Project</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(createProjectDialog);
    
    // Add event listener for team members select
    setTimeout(() => {
        const teamMembersSelect = document.getElementById('teamMembers');
        if (teamMembersSelect) {
            teamMembersSelect.addEventListener('change', function() {
                if (this.value) {
                    addTeamMember(this.value);
                    this.value = '';
                }
            });
        }
    }, 100);
}

function closeCreateProjectDialog() {
    if (createProjectDialog) {
        createProjectDialog.style.display = 'none';
        // Reset form
        document.getElementById('projectName').value = '';
        document.getElementById('projectDescription').value = '';
        document.getElementById('projectDeadline').value = '';
        document.getElementById('projectStatus').value = 'planning';
        selectedTeamMembers = [];
        updateSelectedMembersDisplay();
    }
}

async function loadCreateProjectDialogData() {
    try {
        const employeesResponse = await fetch('/api/manager/employees');
        const employees = await employeesResponse.json();
        
        const teamMembersSelect = document.getElementById('teamMembers');
        teamMembersSelect.innerHTML = '<option value="">Add team members</option>' +
            employees.map(emp => 
                `<option value="${emp.id}">${emp.name} - ${emp.position}</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading dialog data:', error);
        showNotification('Error loading dialog data', 'error');
    }
}

function addTeamMember(memberId) {
    if (!memberId || selectedTeamMembers.includes(memberId)) return;
    
    selectedTeamMembers.push(memberId);
    updateSelectedMembersDisplay();
}

function removeTeamMember(memberId) {
    selectedTeamMembers = selectedTeamMembers.filter(id => id !== memberId);
    updateSelectedMembersDisplay();
}

async function updateSelectedMembersDisplay() {
    const container = document.getElementById('selectedMembers');
    
    try {
        const employeesResponse = await fetch('/api/manager/employees');
        const employees = await employeesResponse.json();
        
        const selectedMembers = employees.filter(emp => 
            selectedTeamMembers.includes(emp.id)
        );
        
        container.innerHTML = selectedMembers.map(emp => `
            <span class="member-tag">
                ${emp.name}
                <button type="button" onclick="removeTeamMember('${emp.id}')" class="tag-remove">×</button>
            </span>
        `).join('');
    } catch (error) {
        console.error('Error updating selected members:', error);
    }
}

async function createProject() {
    const projectData = {
        name: document.getElementById('projectName').value,
        description: document.getElementById('projectDescription').value,
        deadline: document.getElementById('projectDeadline').value,
        teamMembers: selectedTeamMembers,
        status: document.getElementById('projectStatus').value
    };

    // Validate required fields
    if (!projectData.name || !projectData.deadline) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }

    const createBtn = document.getElementById('createProjectBtn');
    createBtn.disabled = true;
    createBtn.textContent = 'Creating...';

    try {
        const response = await fetch('/api/manager/projects/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });

        if (!response.ok) {
            throw new Error('Failed to create project');
        }

        const result = await response.json();
        showNotification('Project created successfully', 'success');
        closeCreateProjectDialog();
        
        // Refresh data if manager dashboard is initialized
        if (window.managerDashboard) {
            window.managerDashboard.refreshData();
        }
    } catch (error) {
        console.error('Error creating project:', error);
        showNotification('Error creating project', 'error');
    } finally {
        createBtn.disabled = false;
        createBtn.textContent = 'Create Project';
    }
}

function showNotification(message, type = 'info') {
    if (window.managerDashboard) {
        window.managerDashboard.showNotification(message, type);
    } else {
        // Fallback notification
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

// Make functions globally available
window.openCreateProjectDialog = openCreateProjectDialog;
window.closeCreateProjectDialog = closeCreateProjectDialog;
window.createProject = createProject;
window.addTeamMember = addTeamMember;
window.removeTeamMember = removeTeamMember;