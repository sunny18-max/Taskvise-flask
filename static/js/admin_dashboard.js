// Admin Dashboard Main JavaScript
class AdminDashboard {
    constructor() {
        this.currentView = 'dashboard';
        this.employees = [];
        this.tasks = [];
        this.projects = [];
        this.stats = {};
        this.currentUserId = null;
        this.systemSettings = {};
        this.init();
    }

    init() {
        this.loadInitialData();
        this.setupEventListeners();
        this.checkDatabaseStatus();
        // Check database status every 30 seconds
        setInterval(() => this.checkDatabaseStatus(), 30000);
    }

    async loadInitialData(forceFetch = false) {
        try {
            // Try to seed from JSON script tags first
            const seeded = forceFetch ? false : this.seedFromScriptTags();
            if (!seeded) {
                await Promise.all([
                    this.loadEmployees(),
                    this.loadTasks(),
                    this.loadProjects(),
                    this.loadStats()
                ]);
            }
            this.updateCurrentView();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading dashboard data', 'error');
        }
    }

    seedFromScriptTags() {
        try {
            const dataTag = document.getElementById('initial-admin-data');
            if (!dataTag) return false;
            const json = JSON.parse(dataTag.textContent || '{}');
            this.employees = Array.isArray(json.employees) ? json.employees : [];
            this.projects = Array.isArray(json.projects) ? json.projects : [];
            this.tasks = Array.isArray(json.tasks) ? json.tasks : [];
            this.stats = typeof json.stats === 'object' && json.stats ? json.stats : {};
            this.currentUserId = json.current_user_id || null;
            this.systemSettings = typeof json.system_settings === 'object' && json.system_settings ? json.system_settings : {};
            return true;
        } catch (e) {
            console.warn('Failed to parse initial admin data:', e);
            return false;
        }
    }

    async checkDatabaseStatus() {
        try {
            const response = await fetch('/api/system/health');
            const health = await response.json();
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (statusDot && statusText) {
                if (health.mongodb.connected && health.mysql && health.mysql.connected) {
                    statusDot.classList.add('connected');
                    statusText.textContent = 'MongoDB + MySQL Ready';
                } else if (health.mongodb.connected) {
                    statusDot.classList.add('connected');
                    statusText.textContent = 'MongoDB Connected';
                } else if (health.mysql && health.mysql.connected) {
                    statusDot.classList.add('connected');
                    statusText.textContent = 'MySQL Connected';
                } else {
                    statusDot.classList.remove('connected');
                    statusText.textContent = 'Database Offline';
                }
            }
        } catch (error) {
            console.warn('Could not check database status:', error);
            const statusText = document.getElementById('statusText');
            if (statusText) {
                statusText.textContent = 'Status Unknown';
            }
        }
    }

    async loadEmployees() {
        const response = await this.makeAuthenticatedRequest('/api/admin/employees');
        this.employees = response || [];
        return this.employees;
    }

    async loadTasks() {
        const response = await this.makeAuthenticatedRequest('/api/admin/tasks');
        this.tasks = response || [];
        return this.tasks;
    }

    async loadProjects() {
        const response = await this.makeAuthenticatedRequest('/api/admin/projects');
        this.projects = response || [];
        return this.projects;
    }

    async loadStats() {
        // This would be replaced with actual API call
        const response = await this.makeAuthenticatedRequest('/api/admin/stats');
        this.stats = response || {};
        return this.stats;
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('.btn-outline[onclick="adminDashboard.refreshData()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Live data refresh each 30 seconds
        this.liveRefreshInterval = setInterval(() => {
            this.refreshData();
        }, 30000);
    }

    updateCurrentView() {
        // Update stats on dashboard
        this.updateDashboardStats();
    }

    updateDashboardStats() {
        // Update stat cards with actual data
        const stats = {
            totalEmployees: this.employees.length,
            activeProjects: this.projects.filter(p => p.status === 'active').length,
            completedTasks: this.tasks.filter(t => t.status === 'completed').length,
            totalTasks: this.tasks.length
        };

        // Update DOM elements
        const totalEmployeesEl = document.getElementById('total-employees');
        const activeProjectsEl = document.getElementById('active-projects');
        const completedTasksEl = document.getElementById('completed-tasks');
        const totalTasksEl = document.getElementById('total-tasks');
        if (totalEmployeesEl) totalEmployeesEl.textContent = stats.totalEmployees;
        if (activeProjectsEl) activeProjectsEl.textContent = stats.activeProjects;
        if (completedTasksEl) completedTasksEl.textContent = stats.completedTasks;
        if (totalTasksEl) totalTasksEl.textContent = stats.totalTasks;
    }

    async refreshData() {
        window.location.reload();
    }

    async makeAuthenticatedRequest(endpoint, options = {}) {
        try {
            const opts = {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {}),
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
            };
            const response = await fetch(endpoint, opts);
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (e) {
            console.warn('API request failed, using local fallback:', endpoint, e);
            // fallback for dashboard stats / project / tasks (non-core)
            if (endpoint.includes('/admin/projects')) {
                return this.projects;
            }
            if (endpoint.includes('/admin/tasks')) {
                return this.tasks;
            }
            if (endpoint.includes('/admin/stats')) {
                return this.stats;
            }
            return [];
        }
    }

    showNotification(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add styles if not already present
        if (!document.querySelector('#toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    min-width: 300px;
                    animation: slideInRight 0.3s ease;
                }
                .toast-content {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }
                .toast.success {
                    border-left: 4px solid #10b981;
                }
                .toast.error {
                    border-left: 4px solid #ef4444;
                }
                .toast.warning {
                    border-left: 4px solid #f59e0b;
                }
                .toast.info {
                    border-left: 4px solid #3b82f6;
                }
                .toast-close {
                    background: none;
                    border: none;
                    color: #94a3b8;
                    cursor: pointer;
                    padding: 0.25rem;
                    border-radius: 4px;
                    transition: background-color 0.2s ease;
                }
                .toast-close:hover {
                    background: #f1f5f9;
                }
            `;
            document.head.appendChild(styles);
        }

        toastContainer.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility methods
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }
}

// Global admin dashboard instance
let adminDashboard;

function initAdminDashboard() {
    adminDashboard = new AdminDashboard();
    // Expose collections for dialogs
    window.adminDashboard = adminDashboard;
}

function refreshAdminData() {
    if (adminDashboard) {
        adminDashboard.refreshData();
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

// Make functions globally available
window.initAdminDashboard = initAdminDashboard;
window.refreshAdminData = refreshAdminData;
window.toggleSidebar = toggleSidebar;
