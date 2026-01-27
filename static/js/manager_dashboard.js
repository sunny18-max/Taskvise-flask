// Manager Dashboard Main JavaScript
class ManagerDashboard {
    constructor() {
        this.currentView = 'overview';
        this.employees = [];
        this.tasks = [];
        this.projects = [];
        this.stats = {};
        this.init();
    }

    init() {
        this.loadInitialData();
        this.setupEventListeners();
        this.setupNavigation();
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadEmployees(),
                this.loadTasks(),
                this.loadProjects(),
                this.loadStats()
            ]);
            this.updateCurrentView();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading dashboard data', 'error');
        }
    }

    async getProjects() {
        if (Array.isArray(this.projects) && this.projects.length) return this.projects;
        return await this.loadProjects();
    }

    async updateProject(projectId, updateData) {
        try {
            await this.makeAuthenticatedRequest(`/api/manager/projects/${projectId}`, {
                method: 'PUT',
                body: JSON.stringify(updateData)
            });
            await this.loadProjects();
            return true;
        } catch (e) {
            console.error('updateProject failed', e);
            return false;
        }
    }

    async loadEmployees() {
        const response = await this.makeAuthenticatedRequest('/api/manager/employees');
        this.employees = response || [];
        return this.employees;
    }

    async loadTasks() {
        const response = await this.makeAuthenticatedRequest('/api/manager/tasks');
        this.tasks = response || [];
        return this.tasks;
    }

    async loadProjects() {
        const response = await this.makeAuthenticatedRequest('/api/manager/projects');
        this.projects = response || [];
        return this.projects;
    }

    async loadStats() {
        const response = await this.makeAuthenticatedRequest('/api/manager/stats');
        this.stats = response || {};
        return this.stats;
    }

    // Public getters used by dialogs/views to ensure data availability
    async getEmployees() {
        if (Array.isArray(this.employees) && this.employees.length) return this.employees;
        return await this.loadEmployees();
    }

    async getTasks() {
        if (Array.isArray(this.tasks) && this.tasks.length) return this.tasks;
        return await this.loadTasks();
    }

    async updateTask(taskId, updateData) {
        try {
            await this.makeAuthenticatedRequest(`/api/manager/tasks/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify(updateData)
            });
            await this.loadTasks();
            // Update any widgets relying on tasks
            this.renderRecentTasks();
            return true;
        } catch (e) {
            console.error('updateTask failed', e);
            return false;
        }
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('.btn-icon[onclick="refreshManagerData()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Navigation items
        const navItems = document.querySelectorAll('.nav-item[data-view]');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.getAttribute('data-view');
                this.navigateToView(view);
            });
        });

        // Navigation sections
        const navSections = document.querySelectorAll('.nav-item[data-toggle]');
        navSections.forEach(section => {
            section.addEventListener('click', (e) => {
                e.preventDefault();
                const target = section.getAttribute('data-toggle');
                this.toggleNavSection(target);
            });
        });
    }

    setupNavigation() {
        // Handle browser back/forward buttons
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.view) {
                this.updateView(event.state.view);
            }
        });
    }

    toggleNavSection(section) {
        const submenu = document.getElementById(`${section}-submenu`);
        const icon = document.querySelector(`[data-toggle="${section}"] .dropdown-icon`);
        
        if (submenu) {
            submenu.classList.toggle('active');
            if (icon) {
                icon.textContent = submenu.classList.contains('active') ? '▲' : '▼';
            }
        }
    }

    navigateToView(view) {
        // Update URL without page reload
        const url = `/manager/${view === 'overview' ? 'dashboard' : view}`;
        window.history.pushState({ view }, '', url);
        this.updateView(view);
    }

    updateView(view) {
        this.currentView = view;
        
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-view="${view}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }

        this.updateCurrentView();
    }

    updateCurrentView() {
        // Update dynamic widgets if present on the page (e.g., recent tasks list)
        this.renderRecentTasks();
    }

    async refreshData() {
        this.showNotification('Refreshing data...', 'info');
        
        try {
            await this.loadInitialData();
            this.showNotification('Data refreshed successfully', 'success');
            // Update overview widgets immediately if visible
            this.renderRecentTasks();
            
            // Dispatch custom event for views to listen to
            window.dispatchEvent(new CustomEvent('managerDataRefreshed', {
                detail: {
                    employees: this.employees,
                    tasks: this.tasks,
                    projects: this.projects,
                    stats: this.stats
                }
            }));
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showNotification('Error refreshing data', 'error');
        }
    }

    renderRecentTasks() {
        const list = document.getElementById('recent-tasks-list');
        if (!list) return;
        const top = (this.tasks || []).slice(0, 5);
        if (!top.length) {
            list.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-tasks"></i>
                    <p>No tasks found</p>
                </div>
            `;
            return;
        }
        const getAssigneeName = (task) => {
            const emp = (this.employees || []).find(e => String(e.id) === String(task.assignee_id || task.assigneeId || task.assignedTo));
            return emp ? (emp.name || emp.fullName || 'Unknown') : 'Unassigned';
        };
        list.innerHTML = top.map(task => `
            <div class="task-item">
                <div class="task-main">
                    <div class="task-title">${task.title || 'Untitled Task'}</div>
                    <div class="task-meta">
                        <i class="fas fa-user"></i>
                        ${getAssigneeName(task)}
                    </div>
                </div>
                <div class="task-status">
                    <span class="status-badge ${task.status || 'pending'}">
                        ${(task.status || 'pending').replace('-', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </span>
                </div>
            </div>
        `).join('');
    }

    async makeAuthenticatedRequest(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(endpoint, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add styles if not already present
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 1rem;
                    right: 1rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    border-left: 4px solid #3b82f6;
                    z-index: 1000;
                    max-width: 350px;
                    animation: slideInRight 0.3s ease-out;
                }
                .notification-success { border-left-color: #10b981; }
                .notification-error { border-left-color: #ef4444; }
                .notification-warning { border-left-color: #f59e0b; }
                .notification-info { border-left-color: #3b82f6; }
                .notification-content {
                    padding: 1rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                }
                .notification-message {
                    flex: 1;
                    margin-right: 1rem;
                }
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 1.25rem;
                    cursor: pointer;
                    color: #64748b;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Utility methods
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    calculateProductivityLevel(productivity) {
        if (productivity >= 80) return { level: 'excellent', label: 'Excellent' };
        if (productivity >= 60) return { level: 'good', label: 'Good' };
        return { level: 'needs-improvement', label: 'Needs Improvement' };
    }

    getPriorityBadge(priority) {
        const classes = {
            'high': 'badge-danger',
            'medium': 'badge-warning',
            'low': 'badge-outline'
        };
        return classes[priority] || 'badge-outline';
    }

    getStatusBadge(status) {
        const classes = {
            'completed': 'badge-success',
            'in-progress': 'badge-warning',
            'pending': 'badge-outline',
            'overdue': 'badge-danger'
        };
        return classes[status] || 'badge-outline';
    }
}

// Global manager dashboard instance
let managerDashboard;

function initManagerDashboard() {
    managerDashboard = new ManagerDashboard();
}

function refreshManagerData() {
    if (managerDashboard) {
        managerDashboard.refreshData();
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

// Make functions globally available
window.initManagerDashboard = initManagerDashboard;
window.refreshManagerData = refreshManagerData;
window.toggleSidebar = toggleSidebar;