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
        const dialogHTML = `
            <div class="modal-overlay" id="add-employee-modal">
                <div class="modal">
                    <div class="modal-header">
                        <h3>Add New Employee</h3>
                        <button class="modal-close">&times;</button>
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
                                <label for="employee-department">Department *</label>
                                <select id="employee-department" class="form-select" required>
                                    <option value="">Select Department</option>
                                    <option value="Engineering">Engineering</option>
                                    <option value="Design">Design</option>
                                    <option value="Marketing">Marketing</option>
                                    <option value="Sales">Sales</option>
                                    <option value="HR">Human Resources</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="employee-role">Role *</label>
                                <select id="employee-role" class="form-select" required>
                                    <option value="">Select Role</option>
                                    <option value="employee">Employee</option>
                                    <option value="manager">Manager</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-outline" onclick="addEmployeeDialog.close()">Cancel</button>
                        <button class="btn-primary" onclick="addEmployeeDialog.submit()">Add Employee</button>
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
            department: document.getElementById('employee-department').value,
            role: document.getElementById('employee-role').value
        };

        if (!this.validateForm(employee)) {
            return;
        }

        try {
            await this.saveEmployee(employee);
            this.close();
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Employee added successfully', 'success');
                window.adminDashboard.refreshData();
            }
        } catch (error) {
            console.error('Error adding employee:', error);
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Error adding employee', 'error');
            }
        }
    }

    validateForm(employee) {
        if (!employee.name || !employee.email || !employee.position || !employee.department || !employee.role) {
            if (window.adminDashboard) {
                window.adminDashboard.showNotification('Please fill in all required fields', 'error');
            }
            return false;
        }
        return true;
    }

    async saveEmployee(employee) {
        // Simulate API call
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('Employee saved:', employee);
                resolve(employee);
            }, 1000);
        });
    }
}

// Initialize dialog
const addEmployeeDialog = new AddEmployeeDialog();