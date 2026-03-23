class AddEmployeeDialog {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listeners will be added when dialog opens
    }

    open() {
        this.createDialog();
    }

    createDialog() {
        const defaultCompany = (window.TaskViseDashboardHelpers && window.TaskViseDashboardHelpers.getDefaultCompanyName)
            ? window.TaskViseDashboardHelpers.getDefaultCompanyName()
            : 'TaskVise HyperScale Operations Consortium';
        const dialogHTML = `
            <div class="modal-overlay" id="add-employee-modal">
                <div class="modal">
                    <div class="modal-header">
                        <div>
                            <h3>Add New Employee</h3>
                            <p class="modal-subtitle">Create a new employee profile.</p>
                        </div>
                        <button class="modal-close" type="button" aria-label="Close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="add-employee-form">
                            <div class="form-group">
                                <label for="employee-name">Full Name *</label>
                                <input type="text" id="employee-name" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label for="employee-email">Email *</label>
                                <input type="email" id="employee-email" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label for="employee-position">Position *</label>
                                <input type="text" id="employee-position" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label for="employee-company">Company *</label>
                                <input type="text" id="employee-company" class="form-input" value="${defaultCompany}" required>
                            </div>
                            <div class="form-group">
                                <label for="employee-department">Department *</label>
                                <select id="employee-department" class="form-select" required>
                                    <option value="">Select Department</option>
                                    <option value="Engineering">Engineering</option>
                                    <option value="Product">Product</option>
                                    <option value="Design">Design</option>
                                    <option value="Marketing">Marketing</option>
                                    <option value="Sales">Sales</option>
                                    <option value="HR">Human Resources</option>
                                    <option value="Finance">Finance</option>
                                    <option value="Operations">Operations</option>
                                    <option value="IT">IT</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="employee-role">Role *</label>
                                <select id="employee-role" class="form-select" required>
                                    <option value="">Select Role</option>
                                    <option value="employee">Employee</option>
                                    <option value="manager">Manager</option>
                                    <option value="hr">HR</option>
                                    <option value="teamlead">Team Lead</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="employee-productivity">Initial Productivity</label>
                                <input type="number" id="employee-productivity" class="form-input" min="0" max="100" value="78">
                            </div>
                            <div class="form-group">
                                <label for="employee-password">Password</label>
                                <input type="text" id="employee-password" class="form-input" placeholder="Leave blank to auto-generate">
                                <small class="form-hint">If blank, TaskVise will generate a temporary password.</small>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outline" type="button" onclick="addEmployeeDialog.close()">Cancel</button>
                        <button class="btn btn-primary" type="button" onclick="addEmployeeDialog.submit()">Add Employee</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        this.bindDialogEvents();
    }

    bindDialogEvents() {
        const modal = document.getElementById('add-employee-modal');
        const closeBtn = modal.querySelector('.modal-close');
        
        closeBtn.addEventListener('click', () => this.close());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.close();
        });
        document.addEventListener('keydown', this.handleEscClose, { once: true });
    }

    handleEscClose(e) {
        if (e.key === 'Escape') {
            addEmployeeDialog.close();
        }
    }

    close() {
        const modal = document.getElementById('add-employee-modal');
        if (modal) {
            modal.remove();
        }
    }

    async submit() {
        const form = document.getElementById('add-employee-form');
        const formData = new FormData(form);
        
        const employee = {
            name: document.getElementById('employee-name').value,
            email: document.getElementById('employee-email').value,
            position: document.getElementById('employee-position').value,
            company: document.getElementById('employee-company').value,
            department: document.getElementById('employee-department').value,
            role: document.getElementById('employee-role').value,
            productivity: document.getElementById('employee-productivity').value,
            password: document.getElementById('employee-password').value.trim()
        };

        if (!this.validateForm(employee)) {
            return;
        }

        try {
            const result = await this.saveEmployee(employee);
            this.close();
            if (window.adminDashboard) {
                const tempPassword = result && result.temporary_password;
                const newId = result && result.id;
                const employeeLabel = newId ? `Employee ${newId}` : 'Employee';
                const message = tempPassword
                    ? `${employeeLabel} added. Temporary password: ${tempPassword}`
                    : `${employeeLabel} added successfully`;
                window.adminDashboard.showNotification(message, 'success');
                if (result && result.storage_status && Array.isArray(result.storage_status.warnings) && result.storage_status.warnings.length) {
                    window.adminDashboard.showNotification(result.storage_status.warnings[0], 'warning');
                }
                window.location.reload();
            }
        } catch (error) {
            console.error('Error adding employee:', error);
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Error adding employee', 'error');
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

    async saveEmployee(employee) {
        const response = await fetch('/api/admin/employees', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(employee)
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.error || 'Failed to create employee');
        }
        return await response.json();
    }
}

// Initialize dialog
const addEmployeeDialog = new AddEmployeeDialog();
