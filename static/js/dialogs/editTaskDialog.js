// Edit Task Dialog
function openEditTaskDialog(taskId, tasks, updateTaskCallback) {
  const task = (tasks || []).find(t => String(t.id) === String(taskId));
  if (!task) {
    showNotification(`Task not found: ${taskId}`, 'error');
    return;
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

  // Current task data
  let editedTask = {
    title: task.title || '',
    description: task.description || '',
    priority: task.priority || 'medium',
    dueDate: task.dueDate ? task.dueDate.split('T')[0] : '',
    status: task.status || 'pending',
    estimatedHours: task.estimatedHours || 0,
    actualHours: task.actualHours || 0
  };

  let saving = false;

  // Create dialog content
  const dialog = document.createElement('div');
  dialog.className = 'dialog-content';
  dialog.style.cssText = `
    background: #ffffff;
    padding: 24px;
    border-radius: 12px;
    width: 92%;
    max-width: 680px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 45px rgba(2,6,23,0.16);
  `;

  dialog.innerHTML = `
    <div class="dialog-header" style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px;">
      <div>
        <h2 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 6px 0; color:#111827;">Edit Task</h2>
        <p style="color: #6b7280; margin: 0; font-size:0.9rem;">Update task details and status</p>
      </div>
      <button id="closeX" aria-label="Close" style="background:none;border:0;color:#64748b;font-size:1.25rem;line-height:1;cursor:pointer;border-radius:8px;padding:2px 6px;">×</button>
    </div>
    
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div>
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">Task Title *</label>
        <input 
          type="text" 
          id="editTaskTitle" 
          placeholder="Enter task title" 
          value="${editedTask.title}"
          style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
        />
      </div>
      
      <div>
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">Description</label>
        <textarea 
          id="editTaskDescription" 
          placeholder="Enter task description"
          style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px; min-height: 80px;"
        >${editedTask.description}</textarea>
      </div>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div>
          <label style="display: block; margin-bottom: 8px; font-weight: 500;">Priority</label>
          <select 
            id="editPriority" 
            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        
        <div>
          <label style="display: block; margin-bottom: 8px; font-weight: 500;">Status</label>
          <select 
            id="editStatus" 
            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
          >
            <option value="pending">Pending</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>
      </div>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div>
          <label style="display: block; margin-bottom: 8px; font-weight: 500;">Due Date *</label>
          <input 
            type="date" 
            id="editDueDate" 
            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
          />
        </div>
        
        <div>
          <label style="display: block; margin-bottom: 8px; font-weight: 500;">Estimated Hours</label>
          <input 
            type="number" 
            id="editEstimatedHours" 
            placeholder="0" 
            style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
          />
        </div>
      </div>

      <div>
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">Actual Hours</label>
        <input 
          type="number" 
          id="editActualHours" 
          placeholder="0" 
          style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
        />
      </div>
    </div>
    
    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
      <button id="cancelBtn" style="padding: 10px 16px; border: 1px solid #d1d5db; border-radius: 8px; background: white; cursor: pointer; font-weight:600;">Cancel</button>
      <button id="updateBtn" style="padding: 10px 16px; border: none; border-radius: 8px; background: #3b82f6; color: white; cursor: pointer; font-weight:600;">Update Task</button>
    </div>
    <div id="errorHint" style="display:none;margin-top:10px;color:#b91c1c;font-size:0.85rem;">Please fill in required fields.</div>
  `;

  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  // Event listeners
  document.getElementById('editTaskTitle').addEventListener('input', (e) => {
    editedTask.title = e.target.value;
    validateForm();
  });
  
  document.getElementById('editTaskDescription').addEventListener('input', (e) => {
    editedTask.description = e.target.value;
  });
  
  document.getElementById('editPriority').addEventListener('change', (e) => {
    editedTask.priority = e.target.value;
  });
  
  document.getElementById('editStatus').addEventListener('change', (e) => {
    editedTask.status = e.target.value;
  });
  
  document.getElementById('editDueDate').addEventListener('input', (e) => {
    editedTask.dueDate = e.target.value;
    validateForm();
  });
  
  document.getElementById('editEstimatedHours').addEventListener('input', (e) => {
    editedTask.estimatedHours = parseInt(e.target.value) || 0;
  });
  
  document.getElementById('editActualHours').addEventListener('input', (e) => {
    editedTask.actualHours = parseInt(e.target.value) || 0;
  });

  function validateForm() {
    const isValid = editedTask.title.trim() !== '' && editedTask.dueDate !== '';
    document.getElementById('updateBtn').disabled = saving || !isValid;
  }

  // Update task function
  async function updateTask() {
    if (saving) return;

    saving = true;
    document.getElementById('updateBtn').disabled = true;
    document.getElementById('updateBtn').textContent = 'Updating...';

    try {
      const success = await updateTaskCallback(taskId, editedTask);
      if (success) {
        showNotification('Task updated successfully', 'success');
        closeDialog();
      } else {
        throw new Error('Failed to update task');
      }
    } catch (error) {
      console.error('Error updating task:', error);
      showNotification(error.message || 'Failed to update task', 'error');
    } finally {
      saving = false;
      document.getElementById('updateBtn').disabled = false;
      document.getElementById('updateBtn').textContent = 'Update Task';
    }
  }

  function closeDialog() {
    document.body.removeChild(overlay);
  }

  document.getElementById('cancelBtn').addEventListener('click', closeDialog);
  document.getElementById('closeX').addEventListener('click', closeDialog);
  document.getElementById('updateBtn').addEventListener('click', updateTask);
  
  // Close on overlay click
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      closeDialog();
    }
  });

  // ESC to close, Enter to submit (except in textarea)
  dialog.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDialog();
    if (e.key === 'Enter' && e.target.tagName.toLowerCase() !== 'textarea') {
      e.preventDefault();
      if (!document.getElementById('updateBtn').disabled) updateTask();
    }
  });

  validateForm();
}

window.openEditTaskDialog = openEditTaskDialog;