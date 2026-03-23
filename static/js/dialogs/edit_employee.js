class EditEmployeeDialog {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listeners will be added when dialog opens
    }

    open(employee) {
        this.employee = employee;
        this.createDialog();
    }

    createDialog() {
        const dialogHTML = `
            <div class="modal-overlay" id="edit-employee-modal">
                <div class="modal">
                    <div class="modal-header">
                        <div>
                            <h3>Edit Employee</h3>
                            <p class="modal-subtitle">Update employee profile details.</p>
                        </div>
                        <button class="modal-close" type="button" aria-label="Close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="edit-employee-form">
                            <div class="form-group">
                                <label for="edit-employee-name">Full Name *</label>
                                <input type="text" id="edit-employee-name" class="form-input" value="${this.employee.name}" required>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-email">Email *</label>
                                <input type="email" id="edit-employee-email" class="form-input" value="${this.employee.email}" required>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-position">Position *</label>
                                <input type="text" id="edit-employee-position" class="form-input" value="${this.employee.position}" required>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-company">Company *</label>
                                <input type="text" id="edit-employee-company" class="form-input" value="${this.employee.company || ''}" required>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-department">Department *</label>
                                <select id="edit-employee-department" class="form-select" required>
                                    <option value="">Select Department</option>
                                    <option value="Engineering" ${this.employee.department === 'Engineering' ? 'selected' : ''}>Engineering</option>
                                    <option value="Product" ${this.employee.department === 'Product' ? 'selected' : ''}>Product</option>
                                    <option value="Design" ${this.employee.department === 'Design' ? 'selected' : ''}>Design</option>
                                    <option value="Marketing" ${this.employee.department === 'Marketing' ? 'selected' : ''}>Marketing</option>
                                    <option value="Sales" ${this.employee.department === 'Sales' ? 'selected' : ''}>Sales</option>
                                    <option value="HR" ${this.employee.department === 'HR' ? 'selected' : ''}>Human Resources</option>
                                    <option value="Finance" ${this.employee.department === 'Finance' ? 'selected' : ''}>Finance</option>
                                    <option value="Operations" ${this.employee.department === 'Operations' ? 'selected' : ''}>Operations</option>
                                    <option value="IT" ${this.employee.department === 'IT' ? 'selected' : ''}>IT</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-role">Role *</label>
                                <select id="edit-employee-role" class="form-select" required>
                                    <option value="">Select Role</option>
                                    <option value="employee" ${this.employee.role === 'employee' ? 'selected' : ''}>Employee</option>
                                    <option value="manager" ${this.employee.role === 'manager' ? 'selected' : ''}>Manager</option>
                                    <option value="hr" ${this.employee.role === 'hr' ? 'selected' : ''}>HR</option>
                                    <option value="teamlead" ${this.employee.role === 'teamlead' ? 'selected' : ''}>Team Lead</option>
                                    <option value="admin" ${this.employee.role === 'admin' ? 'selected' : ''}>Admin</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-status">Status</label>
                                <select id="edit-employee-status" class="form-select">
                                    <option value="active" ${this.employee.status === 'active' ? 'selected' : ''}>Active</option>
                                    <option value="inactive" ${this.employee.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="edit-employee-productivity">Productivity</label>
                                <input type="number" id="edit-employee-productivity" class="form-input" min="0" max="100" value="${this.employee.productivity || 0}">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outline" type="button" onclick="editEmployeeDialog.close()">Cancel</button>
                        <button class="btn btn-danger" type="button" onclick="editEmployeeDialog.deleteEmployee()" style="margin-right: auto;">Delete</button>
                        <button class="btn btn-primary" type="button" onclick="editEmployeeDialog.submit()">Save Changes</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        this.bindDialogEvents();
    }

    bindDialogEvents() {
        const modal = document.getElementById('edit-employee-modal');
        const closeBtn = modal.querySelector('.modal-close');
        
        closeBtn.addEventListener('click', () => this.close());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.close();
        });
        document.addEventListener('keydown', this.handleEscClose, { once: true });
    }

    handleEscClose(e) {
        if (e.key === 'Escape') {
            editEmployeeDialog.close();
        }
    }

    close() {
        const modal = document.getElementById('edit-employee-modal');
        if (modal) {
            modal.remove();
        }
    }

    async submit() {
        const form = document.getElementById('edit-employee-form');
        
        const updatedEmployee = {
            ...this.employee,
            name: document.getElementById('edit-employee-name').value,
            email: document.getElementById('edit-employee-email').value,
            position: document.getElementById('edit-employee-position').value,
            company: document.getElementById('edit-employee-company').value,
            department: document.getElementById('edit-employee-department').value,
            role: document.getElementById('edit-employee-role').value,
            status: document.getElementById('edit-employee-status').value,
            productivity: document.getElementById('edit-employee-productivity').value
        };

        if (!this.validateForm(updatedEmployee)) {
            return;
        }

        try {
            await this.updateEmployee(updatedEmployee);
            this.close();
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Employee updated successfully', 'success');
                window.location.reload();
            }
        } catch (error) {
            console.error('Error updating employee:', error);
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Error updating employee', 'error');
            }
        }
    }

    async deleteEmployee() {
        if (!confirm('Are you sure you want to delete this employee?')) {
            return;
        }

        try {
            await this.performDelete();
            this.close();
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Employee deleted successfully', 'success');
                window.location.reload();
            }
        } catch (error) {
            console.error('Error deleting employee:', error);
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Error deleting employee', 'error');
            }
        }
    }

    validateForm(employee) {
        if (!employee.name || !employee.email || !employee.position || !employee.company || !employee.department || !employee.role) {
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Please fill in all required fields', 'error');
            }
            return false;
        }
        return true;
    }

    async updateEmployee(employee) {
        const response = await fetch(`/api/admin/employees/${encodeURIComponent(employee.id)}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: employee.name,
                email: employee.email,
                position: employee.position,
                company: employee.company,
                department: employee.department,
                role: employee.role,
                status: employee.status,
                productivity: employee.productivity
            })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.error || 'Failed to update employee');
        }

        return await response.json();
    }

    async performDelete() {
        const response = await fetch(`/api/admin/employees/${encodeURIComponent(this.employee.id)}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.error || 'Failed to delete employee');
        }

        return await response.json();
    }
}

// Initialize dialog
const editEmployeeDialog = new EditEmployeeDialog();
