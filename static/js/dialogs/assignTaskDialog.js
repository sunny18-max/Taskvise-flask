// Assign Task Dialog
let assignTaskDialog = null;
let employees = [];
let projects = [];

function openAssignTaskDialog() {
    if (!assignTaskDialog) {
        createAssignTaskDialog();
    }
    assignTaskDialog.style.display = 'flex';
    loadAssignTaskDialogData();
}

function createAssignTaskDialog() {
    assignTaskDialog = document.createElement('div');
    assignTaskDialog.className = 'dialog-overlay';
    assignTaskDialog.innerHTML = `
        <div class="dialog assign-task-dialog">
            <div class="dialog-header">
                <h2 class="dialog-title">Assign New Task</h2>
                <p class="dialog-description">Create and assign a new task to a team member</p>
                <button class="dialog-close" onclick="closeAssignTaskDialog()">×</button>
            </div>
            
            <div class="dialog-content">
                <div class="form-group">
                    <label for="taskTitle" class="form-label">Task Title *</label>
                    <input type="text" id="taskTitle" class="form-input" placeholder="Enter task title">
                </div>
                
                <div class="form-group">
                    <label for="taskDescription" class="form-label">Description</label>
                    <textarea id="taskDescription" class="form-textarea" placeholder="Enter task description"></textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="assignedTo" class="form-label">Assign To *</label>
                        <select id="assignedTo" class="form-select">
                            <option value="">Select employee</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="priority" class="form-label">Priority</label>
                        <select id="priority" class="form-select">
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="dueDate" class="form-label">Due Date *</label>
                        <input type="date" id="dueDate" class="form-input">
                    </div>
                    
                    <div class="form-group">
                        <label for="estimatedHours" class="form-label">Estimated Hours</label>
                        <input type="number" id="estimatedHours" class="form-input" placeholder="0" min="0">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="project" class="form-label">Project</label>
                        <select id="project" class="form-select">
                            <option value="">Select project</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="area" class="form-label">Area/Department</label>
                        <input type="text" id="area" class="form-input" placeholder="e.g., Development, Marketing">
                    </div>
                </div>
            </div>
            
            <div class="dialog-actions">
                <button class="btn btn-outline" onclick="closeAssignTaskDialog()">Cancel</button>
                <button class="btn btn-primary" onclick="assignTask()" id="assignTaskBtn">Assign Task</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(assignTaskDialog);
}

function closeAssignTaskDialog() {
    if (assignTaskDialog) {
        assignTaskDialog.style.display = 'none';
        // Reset form
        document.getElementById('taskTitle').value = '';
        document.getElementById('taskDescription').value = '';
        document.getElementById('assignedTo').value = '';
        document.getElementById('priority').value = 'medium';
        document.getElementById('dueDate').value = '';
        document.getElementById('estimatedHours').value = '';
        document.getElementById('project').value = '';
        document.getElementById('area').value = '';
    }
}

async function loadAssignTaskDialogData() {
    try {
        // Load employees
        const employeesResponse = await fetch('/api/manager/employees');
        employees = await employeesResponse.json();
        
        const assignedToSelect = document.getElementById('assignedTo');
        assignedToSelect.innerHTML = '<option value="">Select employee</option>' +
            employees.map(emp => 
                `<option value="${emp.id}">${emp.name} - ${emp.position}</option>`
            ).join('');

        // Load projects
        const projectsResponse = await fetch('/api/manager/projects');
        projects = await projectsResponse.json();
        
        const projectSelect = document.getElementById('project');
        projectSelect.innerHTML = '<option value="">Select project</option>' +
            projects.map(project => 
                `<option value="${project.id}">${project.name}</option>`
            ).join('');

    } catch (error) {
        console.error('Error loading dialog data:', error);
        showNotification('Error loading dialog data', 'error');
    }
}

async function assignTask() {
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        assignedTo: document.getElementById('assignedTo').value,
        project: document.getElementById('project').value,
        priority: document.getElementById('priority').value,
        due_date: document.getElementById('dueDate').value,
        estimatedHours: parseInt(document.getElementById('estimatedHours').value) || 0,
        area: document.getElementById('area').value
    };

    // Validate required fields
    if (!taskData.title || !taskData.assignedTo || !taskData.due_date) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }

    const assignBtn = document.getElementById('assignTaskBtn');
    assignBtn.disabled = true;
    assignBtn.textContent = 'Assigning...';

    try {
        const response = await fetch('/api/manager/tasks/assign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        if (!response.ok) {
            throw new Error('Failed to assign task');
        }

        const result = await response.json();
        showNotification('Task assigned successfully', 'success');
        closeAssignTaskDialog();
        
        // Refresh data if manager dashboard is initialized
        if (window.managerDashboard) {
            // If currently on tasks view, navigate to force re-render of server-side list
            const onTasksView = window.location.pathname.includes('/manager/tasks');
            await window.managerDashboard.refreshData();
            if (onTasksView) {
                window.location.href = '/manager/tasks';
            } else {
                // Update recent tasks widget on overview if present
                if (typeof window.managerDashboard.renderRecentTasks === 'function') {
                    window.managerDashboard.renderRecentTasks();
                }
            }
        }
    } catch (error) {
        console.error('Error assigning task:', error);
        showNotification('Error assigning task', 'error');
    } finally {
        assignBtn.disabled = false;
        assignBtn.textContent = 'Assign Task';
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
window.openAssignTaskDialog = openAssignTaskDialog;
window.closeAssignTaskDialog = closeAssignTaskDialog;
window.assignTask = assignTask;