// Employee Dashboard JavaScript
const EMPLOYEE_TRANSLATIONS = {
    en: {},
    es: {
        'Overview': 'Resumen',
        'My Tasks': 'Mis tareas',
        'My Projects': 'Mis proyectos',
        'Workload & Help': 'Carga y ayuda',
        'Leave Management': 'Gestión de permisos',
        'Reports': 'Informes',
        'Notifications': 'Notificaciones',
        'Profile': 'Perfil',
        'Settings': 'Ajustes',
        'Dashboard Overview': 'Resumen del panel',
        "Welcome back! Here's what's happening today.": 'Bienvenido de nuevo. Esto es lo que sucede hoy.',
        'Manage your assigned tasks and track progress': 'Gestiona tus tareas asignadas y su progreso',
        'Track and manage your assigned projects': 'Sigue y gestiona tus proyectos asignados',
        'Monitor your workload and request assistance when needed': 'Monitorea tu carga y solicita ayuda cuando sea necesario',
        'Manage your leave requests and calendar': 'Gestiona tus solicitudes de permiso y calendario',
        'View your performance reports and analytics': 'Consulta tus informes y analíticas',
        'Stay updated with your notifications': 'Mantente al día con tus notificaciones',
        'View and manage your personal information': 'Ver y gestionar información personal',
        'Customize your preferences and account settings': 'Personaliza tus preferencias y ajustes de cuenta',
    },
    fr: {
        'Overview': 'Aperçu',
        'My Tasks': 'Mes tâches',
        'My Projects': 'Mes projets',
        'Workload & Help': 'Charge et aide',
        'Leave Management': 'Gestion des congés',
        'Reports': 'Rapports',
        'Notifications': 'Notifications',
        'Profile': 'Profil',
        'Settings': 'Paramètres',
        'Dashboard Overview': 'Aperçu du tableau de bord',
        "Welcome back! Here's what's happening today.": "Bon retour. Voici ce qui se passe aujourd'hui.",
        'Manage your assigned tasks and track progress': 'Gérez vos tâches assignées et suivez la progression',
        'Track and manage your assigned projects': 'Suivez et gérez vos projets assignés',
        'Monitor your workload and request assistance when needed': "Surveillez votre charge et demandez de l'aide si besoin",
        'Manage your leave requests and calendar': 'Gérez vos demandes de congé et calendrier',
        'View your performance reports and analytics': 'Consultez vos rapports et analyses',
        'Stay updated with your notifications': 'Restez informé avec vos notifications',
        'View and manage your personal information': 'Voir et gérer vos informations personnelles',
        'Customize your preferences and account settings': 'Personnalisez vos préférences et paramètres de compte',
    },
    de: {
        'Overview': 'Übersicht',
        'My Tasks': 'Meine Aufgaben',
        'My Projects': 'Meine Projekte',
        'Workload & Help': 'Auslastung & Hilfe',
        'Leave Management': 'Urlaubsverwaltung',
        'Reports': 'Berichte',
        'Notifications': 'Benachrichtigungen',
        'Profile': 'Profil',
        'Settings': 'Einstellungen',
        'Dashboard Overview': 'Dashboard-Übersicht',
        "Welcome back! Here's what's happening today.": 'Willkommen zurück! Das passiert heute.',
        'Manage your assigned tasks and track progress': 'Verwalte deine zugewiesenen Aufgaben und den Fortschritt',
        'Track and manage your assigned projects': 'Verfolge und verwalte deine zugewiesenen Projekte',
        'Monitor your workload and request assistance when needed': 'Überwache deine Auslastung und bitte bei Bedarf um Hilfe',
        'Manage your leave requests and calendar': 'Verwalte deine Urlaubsanträge und Kalender',
        'View your performance reports and analytics': 'Sieh dir Leistungsberichte und Analysen an',
        'Stay updated with your notifications': 'Bleibe mit Benachrichtigungen auf dem Laufenden',
        'View and manage your personal information': 'Persönliche Informationen ansehen und verwalten',
        'Customize your preferences and account settings': 'Präferenzen und Kontoeinstellungen anpassen',
    }
};

let activeEmployeeLanguage = localStorage.getItem('taskvise_employee_language') || 'en';

function tEmployee(text) {
    const bundle = EMPLOYEE_TRANSLATIONS[activeEmployeeLanguage] || EMPLOYEE_TRANSLATIONS.en;
    return bundle[text] || text;
}

function resolveThemeMode(theme) {
    const raw = String(theme || 'system').toLowerCase();
    if (raw === 'dark' || raw === 'light') return raw;
    return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
}

function applyEmployeeTheme(theme = 'system') {
    const mode = String(theme || 'system').toLowerCase();
    const resolved = resolveThemeMode(mode);
    document.documentElement.setAttribute('data-theme', resolved);
    document.documentElement.setAttribute('data-theme-mode', mode);
    localStorage.setItem('taskvise_employee_theme', mode);
}

function applyEmployeeLanguage(language = 'en') {
    const lang = EMPLOYEE_TRANSLATIONS[language] ? language : 'en';
    activeEmployeeLanguage = lang;
    localStorage.setItem('taskvise_employee_language', lang);
    document.documentElement.setAttribute('lang', lang);

    const labelMap = [
        ['a[href="/employee/overview"] span', 'Overview'],
        ['a[href="/employee/tasks"] span', 'My Tasks'],
        ['a[href="/employee/projects"] span', 'My Projects'],
        ['a[href="/employee/workload"] span', 'Workload & Help'],
        ['a[href="/employee/leave"] span', 'Leave Management'],
        ['a[href="/employee/reports"] span', 'Reports'],
        ['a[href="/employee/notifications"] span', 'Notifications'],
        ['a[href="/employee/profile"] span', 'Profile'],
        ['a[href="/employee/settings"] span', 'Settings'],
        ['.dropdown-item[data-view="profile"] span', 'Profile'],
        ['.dropdown-item[data-view="settings"] span', 'Settings'],
    ];

    labelMap.forEach(([selector, key]) => {
        const el = document.querySelector(selector);
        if (el) el.textContent = tEmployee(key);
    });

    const titleElement = document.getElementById('page-title');
    const subtitleElement = document.getElementById('page-subtitle');
    if (titleElement) {
        const base = titleElement.getAttribute('data-base-value') || titleElement.textContent.trim();
        titleElement.setAttribute('data-base-value', base);
        titleElement.textContent = tEmployee(base);
    }
    if (subtitleElement) {
        const base = subtitleElement.getAttribute('data-base-value') || subtitleElement.textContent.trim();
        subtitleElement.setAttribute('data-base-value', base);
        subtitleElement.textContent = tEmployee(base);
    }
}

async function loadUserPreferences() {
    const storedTheme = localStorage.getItem('taskvise_employee_theme') || 'system';
    const storedLanguage = localStorage.getItem('taskvise_employee_language') || 'en';
    applyEmployeeTheme(storedTheme);
    applyEmployeeLanguage(storedLanguage);

    try {
        const response = await fetch('/api/employee/settings', { cache: 'no-store' });
        if (!response.ok) return;
        const result = await response.json();
        if (!(result.ok || result.success)) return;
        const settings = result.settings || {};
        applyEmployeeTheme(settings.theme || storedTheme);
        applyEmployeeLanguage(settings.language || storedLanguage);
    } catch (_error) {
        // Keep local preferences if server settings are unavailable.
    }
}

window.applyEmployeeTheme = applyEmployeeTheme;
window.applyEmployeeLanguage = applyEmployeeLanguage;

if (!window.__employeeThemeMediaWatcherBound && window.matchMedia) {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const listener = () => {
        const mode = localStorage.getItem('taskvise_employee_theme') || 'system';
        if (mode === 'system') applyEmployeeTheme('system');
    };
    if (typeof mq.addEventListener === 'function') {
        mq.addEventListener('change', listener);
    } else if (typeof mq.addListener === 'function') {
        mq.addListener(listener);
    }
    window.__employeeThemeMediaWatcherBound = true;
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Employee Dashboard Initialized');

    loadUserPreferences();

    // Initialize dashboard
    initDashboard();
    
    // Event listeners
    setupEventListeners();
    
    // Load initial data based on current view
    loadCurrentView();
});

function initDashboard() {
    console.log('Initializing dashboard...');
    
    // Set up navigation
    setupNavigation();
    
    // Update notification badges
    updateNotificationBadges();
    
    // Initialize workload indicator
    updateWorkloadIndicator();
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Menu toggle for mobile
    const menuToggle = document.getElementById('menuToggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function(event) {
            toggleSidebar(event);
        });
    }

    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            closeSidebar();
        });
    }

    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeSidebar();
        });
    }
    
    // User dropdown
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        if (userDropdown) {
            userDropdown.classList.remove('show');
        }
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeSidebar();
        }
    });

    window.addEventListener('resize', function() {
        if (!isMobileSidebarViewport()) {
            closeSidebar();
        }
    });
    
    // Navigation items
    setupNavigationListeners();
}

function setupNavigation() {
    console.log('Setting up navigation...');
    
    // Get current path to determine active state
    const currentPath = window.location.pathname;
    console.log('Current path:', currentPath);
    
    // Set active nav item based on current path
    const navItems = document.querySelectorAll('.nav-item, .nav-subitem');
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href.replace('/employee/', ''))) {
            item.classList.add('active');
            
            // If it's a subitem, also activate parent section
            if (item.classList.contains('nav-subitem')) {
                const parentSection = item.closest('.nav-section');
                if (parentSection) {
                    parentSection.classList.add('active');
                }
            }
        }
    });
}

function setupNavigationListeners() {
    console.log('Setting up navigation listeners...');
    
    // Main navigation items
    const navItems = document.querySelectorAll('.nav-item[data-view]');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const view = this.getAttribute('data-view');
            const href = this.getAttribute('href');
            
            console.log('Navigation clicked:', view, href);
            
            // If this item has a dropdown chevron, toggle submenu but still navigate
            const hasDropdown = !!this.querySelector('.fa-chevron-down');
            if (hasDropdown) {
                const parentSection = this.closest('.nav-section');
                if (parentSection) parentSection.classList.toggle('active');
            }
            if (isMobileSidebarViewport()) closeSidebar();
            if (href && href !== '#') window.location.href = href;
        });
    });
    
    // Submenu items
    const subItems = document.querySelectorAll('.nav-subitem[data-view]');
    subItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const view = this.getAttribute('data-view');
            const filter = this.getAttribute('data-filter');
            const href = this.getAttribute('href');
            
            console.log('Submenu clicked:', view, filter, href);
            
            if (isMobileSidebarViewport()) closeSidebar();
            if (href && href !== '#') {
                window.location.href = href;
            }
        });
    });
}

function loadCurrentView() {
    const currentPath = window.location.pathname;
    console.log('Loading current view for path:', currentPath);
    
    let view = 'overview';
    // If the server has already rendered content into #dashboard-view, do not inject hardcoded HTML
    const container = document.getElementById('dashboard-view');
    const hasServerContent = !!(container && container.children && container.children.length > 0);
    
    if (currentPath.includes('/employee/tasks')) {
        view = 'tasks';
        if (!hasServerContent) {
            const urlParams = new URLSearchParams(window.location.search);
            const filter = urlParams.get('filter');
            loadTasksData(filter);
        }
    } else if (currentPath.includes('/employee/projects')) {
        view = 'projects';
        // If the server rendered the real projects view, don't override it
        if (!hasServerContent && !document.querySelector('.projects-view')) {
            const urlParams = new URLSearchParams(window.location.search);
            const filter = urlParams.get('filter');
            loadProjectsData(filter);
        }
    } else if (currentPath.includes('/employee/workload')) {
        view = 'workload';
        if (!hasServerContent) loadWorkloadData();
    } else if (currentPath.includes('/employee/leave')) {
        view = 'leave';
        // If the server has included the full leave template, do not override it
        if (!hasServerContent && !document.querySelector('.leave-management')) {
            const urlParams = new URLSearchParams(window.location.search);
            const filter = urlParams.get('filter');
            loadLeaveData(filter);
        }
    } else if (currentPath.includes('/employee/reports')) {
        view = 'reports';
        if (!hasServerContent) loadReportsData();
    } else if (currentPath.includes('/employee/notifications')) {
        view = 'notifications';
        if (!hasServerContent) loadNotificationsData();
    } else if (currentPath.includes('/employee/profile')) {
        view = 'profile';
        if (!hasServerContent) loadProfileData();
    } else if (currentPath.includes('/employee/settings')) {
        view = 'settings';
        if (!hasServerContent) loadSettingsData();
    } else {
        // Default to overview
        if (!hasServerContent) loadOverviewData();
    }
    
    updatePageTitle(view);
}

function updatePageTitle(view) {
    const titleMap = {
        'overview': { title: 'Dashboard Overview', subtitle: 'Welcome back! Here\'s what\'s happening today.' },
        'tasks': { title: 'My Tasks', subtitle: 'Manage your assigned tasks and track progress' },
        'projects': { title: 'My Projects', subtitle: 'Track and manage your assigned projects' },
        'workload': { title: 'Workload & Help', subtitle: 'Monitor your workload and request assistance when needed' },
        'leave': { title: 'Leave Management', subtitle: 'Manage your leave requests and calendar' },
        'reports': { title: 'Reports', subtitle: 'View your performance reports and analytics' },
        'notifications': { title: 'Notifications', subtitle: 'Stay updated with your notifications' },
        'profile': { title: 'My Profile', subtitle: 'View and manage your personal information' },
        'settings': { title: 'Settings', subtitle: 'Customize your preferences and account settings' }
    };
    
    const pageInfo = titleMap[view] || titleMap['overview'];
    
    const titleElement = document.getElementById('page-title');
    const subtitleElement = document.getElementById('page-subtitle');
    
    if (titleElement) {
        titleElement.setAttribute('data-base-value', pageInfo.title);
        titleElement.textContent = tEmployee(pageInfo.title);
    }
    if (subtitleElement) {
        subtitleElement.setAttribute('data-base-value', pageInfo.subtitle);
        subtitleElement.textContent = tEmployee(pageInfo.subtitle);
    }
}

function isMobileSidebarViewport() {
    return window.innerWidth <= 1024;
}

function setSidebarOpen(isOpen) {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!sidebar) return;

    sidebar.classList.toggle('active', !!isOpen);
    if (overlay) {
        overlay.classList.toggle('active', !!isOpen);
    }
}

function closeSidebar() {
    setSidebarOpen(false);
}

function toggleSidebar(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    if (!isMobileSidebarViewport()) {
        closeSidebar();
        return;
    }

    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    setSidebarOpen(!sidebar.classList.contains('active'));
}

function loadOverviewData() {
    console.log('Loading overview data...');
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    
    Promise.all([
        fetch('/api/employee/tasks').then(r => r.json()).catch(() => []),
        fetch('/api/employee/projects').then(r => r.json()).catch(() => [])
    ]).then(([tasks, projects]) => {
        const totalTasks = tasks.length;
        const completedTasks = tasks.filter(t => t.status === 'completed').length;
        const pendingTasks = tasks.filter(t => (t.status || 'pending') === 'pending').length;
        const overdueTasks = tasks.filter(t => {
            if (!t.due_date) return false;
            try { return new Date(t.due_date) < new Date() && t.status !== 'completed'; } catch { return false; }
        }).length;
        const activeProjects = projects.filter(p => (p.status || 'planning') === 'active').length;
        const recentTasks = [...tasks]
            .sort((a,b) => new Date(b.created_at||b.due_date||0) - new Date(a.created_at||a.due_date||0))
            .slice(0,5)
            .map(t => ({
                id: t.id,
                title: t.title || 'Untitled',
                project: t.project_id || '',
                priority: (t.priority||'medium'),
                dueDate: t.due_date,
                status: t.status||'pending',
                progress: parseInt(t.progress) || 0
            }));
        const activeProjectsList = projects.filter(p => (p.status||'planning') !== 'completed').slice(0,5).map(p => ({
            id: p.id, name: p.name||'Unnamed', description: p.description||'', status: p.status||'planning', progress: parseInt(p.progress) || 0
        }));

        const html = `
        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-content">
                    <div>
                        <div class="stat-value">${totalTasks}</div>
                        <div class="stat-label">Total Tasks</div>
                        <div class="stat-badge badge-primary">Assigned</div>
                    </div>
                    <div class="stat-icon">
                        <i class="fas fa-tasks"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-content">
                    <div>
                        <div class="stat-value">${completedTasks}</div>
                        <div class="stat-label">Completed</div>
                        <div class="stat-badge badge-success">Done</div>
                    </div>
                    <div class="stat-icon">
                        <i class="fas fa-check-circle"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-content">
                    <div>
                        <div class="stat-value">${pendingTasks}</div>
                        <div class="stat-label">Pending</div>
                        <div class="stat-badge badge-warning">In Progress</div>
                    </div>
                    <div class="stat-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-content">
                    <div>
                        <div class="stat-value">${overdueTasks}</div>
                        <div class="stat-label">Overdue</div>
                        <div class="stat-badge badge-danger">Attention</div>
                    </div>
                    <div class="stat-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Content Grid -->
        <div class="content-grid">
            <!-- Recent Tasks -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-clock"></i> Recent Tasks</h3>
                </div>
                <div class="card-body">
                    <div class="task-list">
                        ${recentTasks.map(task => `
                            <div class="task-item" onclick="viewTask('${task.id}')">
                                <div class="task-info">
                                    <div class="task-title">${task.title}</div>
                                    <div class="task-project">${task.project || ''}</div>
                                </div>
                                <div class="task-meta">
                                    <span class="task-priority priority-${task.priority}">${task.priority}</span>
                                    <span><i class="far fa-calendar"></i> ${task.dueDate ? formatDate(task.dueDate) : ''}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="text-center mt-3">
                        <a href="/employee/tasks" class="btn btn-outline" data-view="tasks">
                            View All Tasks
                        </a>
                    </div>
                </div>
            </div>

            <!-- Active Projects -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-target"></i> Active Projects</h3>
                </div>
                <div class="card-body">
                    <div class="project-list">
                        ${activeProjectsList.map(project => `
                            <div class="project-item" onclick="viewProject('${project.id}')">
                                <div class="project-info">
                                    <div class="project-name">${project.name}</div>
                                    <div class="project-description">${project.description}</div>
                                    <div class="project-meta">
                                        <span class="project-status status-${project.status}">${project.status}</span>
                                        <span><i class="fas fa-chart-line"></i> ${project.progress}%</span>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="text-center mt-3">
                        <a href="/employee/projects" class="btn btn-outline" data-view="projects">
                            View All Projects
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
        contentArea.innerHTML = html;
    });
}

async function loadTasksData(filter = null) {
    console.log('Loading tasks data with filter:', filter);
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    const tasks = await fetch('/api/employee/tasks').then(r => r.json()).catch(() => []);
    window.__employeeTasks = tasks;
    let filteredTasks = tasks.slice();
    if (filter === 'in-progress') {
        filteredTasks = filteredTasks.filter(t => (t.status||'') === 'in-progress');
    } else if (filter === 'active') {
        filteredTasks = filteredTasks.filter(t => (t.status||'') !== 'completed');
    } else if (filter === 'overdue') {
        filteredTasks = filteredTasks.filter(t => {
            if (!t.due_date) return false;
            try { return new Date(t.due_date) < new Date() && t.status !== 'completed'; } catch { return false; }
        });
    }
    const html = `
        <!-- Filters -->
        <div class="filters-grid">
            <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" class="form-input" placeholder="Search tasks..." id="taskSearch">
            </div>
            <select class="form-select" id="statusFilter">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
            </select>
            <select class="form-select" id="priorityFilter">
                <option value="">All Priority</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <button class="btn btn-outline" onclick="applyTaskFilters()">
                <i class="fas fa-filter"></i>
                Apply
            </button>
        </div>

        <!-- Tasks List -->
        <div class="task-list">
            ${filteredTasks.length > 0 ? filteredTasks.map(task => `
                <div class="task-card" onclick="viewTask('${task.id}')">
                    <div class="task-card-header">
                        <h3 class="task-title">${task.title || 'Untitled Task'}</h3>
                        <div class="task-badges">
                            <span class="badge badge-${(task.priority||'medium') === 'high' ? 'danger' : (task.priority||'medium') === 'medium' ? 'warning' : 'success'}">
                                ${(task.priority||'medium')} priority
                            </span>
                            <span class="badge badge-outline">
                                ${(task.status||'pending')}
                            </span>
                        </div>
                    </div>
                    <div class="task-description">
                        ${task.description||''}
                    </div>
                    <div class="task-meta">
                        <span><i class="fas fa-project-diagram"></i> ${task.project_id || ''}</span>
                        <span><i class="far fa-calendar"></i> ${task.due_date ? 'Due: '+formatDate(task.due_date) : ''}</span>
                    </div>
                    <div class="task-actions">
                        <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); startEmployeeTaskTimer('${task.id}')">
                            <i class="fas fa-play"></i> Start
                        </button>
                        <button class="btn btn-sm btn-success" onclick="event.stopPropagation(); updateTaskStatus('${task.id}', 'completed')">
                            <i class="fas fa-check"></i> Complete
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); requestTaskHelp('${task.id}')">
                            <i class="fas fa-question-circle"></i> Need Help
                        </button>
                    </div>
                </div>
            `).join('') : `
                <div class="empty-state">
                    <i class="fas fa-tasks"></i>
                    <h3>No tasks found</h3>
                    <p class="empty-subtext">${filter ? `No ${filter} tasks available` : 'No tasks assigned yet'}</p>
                </div>
            `}
        </div>
    `;
    
    contentArea.innerHTML = html;

    // Wire live search
    const search = document.getElementById('taskSearch');
    if (search) search.addEventListener('input', applyTaskFilters);
}

async function loadProjectsData(filter = null) {
    console.log('Loading projects data with filter:', filter);
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    const projects = await fetch('/api/employee/projects').then(r => r.json()).catch(() => []);
    window.__employeeProjects = projects;
    let filteredProjects = projects.slice();
    if (filter === 'active') {
        filteredProjects = filteredProjects.filter(project => (project.status||'') === 'active');
    } else if (filter === 'on-hold') {
        filteredProjects = filteredProjects.filter(project => (project.status||'') === 'on-hold');
    }
    const html = `
        <div class="projects-grid">
            ${filteredProjects.length > 0 ? filteredProjects.map(project => `
                <div class="project-card">
                    <div class="project-card-header">
                        <h3 class="project-name">${project.name}</h3>
                        <div class="project-badges">
                            <span class="badge badge-${(project.status||'planning') === 'active' ? 'success' : 'warning'}">
                                ${project.status||'planning'}
                            </span>
                        </div>
                    </div>
                    <div class="project-description">
                        ${project.description||''}
                    </div>
                    
                    <div class="project-progress">
                        <div class="progress-header">
                            <span>Progress</span>
                            <span>${project.progress||0}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${project.progress||0}%"></div>
                        </div>
                    </div>
                    
                    <div class="project-stats">
                        
                    </div>
                    
                    <div class="project-dates">
                        <div class="date-item">
                            <i class="fas fa-play-circle"></i>
                            <span>Start: ${project.startDate ? formatDate(project.startDate) : ''}</span>
                        </div>
                        <div class="date-item">
                            <i class="fas fa-flag-checkered"></i>
                            <span>End: ${project.endDate ? formatDate(project.endDate) : ''}</span>
                        </div>
                    </div>
                    
                    <div class="project-actions">
                        <button class="btn btn-sm btn-primary" onclick="viewProject('${project.id}')">
                            <i class="fas fa-eye"></i> View Details
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="viewProjectTasks('${project.id}')">
                            <i class="fas fa-list"></i> Tasks
                        </button>
                    </div>
                </div>
            `).join('') : `
                <div class="empty-state">
                    <i class="fas fa-target"></i>
                    <h3>No projects found</h3>
                    <p class="empty-subtext">${filter ? `No ${filter} projects available` : 'No projects assigned yet'}</p>
                </div>
            `}
        </div>
    `;
    
    contentArea.innerHTML = html;
}

async function updateTaskStatus(taskId, status) {
    try {
        const resp = await fetch('/api/employee/tasks/update-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId, status })
        });
        if (!resp.ok) throw new Error('Update failed');
        showToast('Task updated', 'success');
        // Reload current view
        const path = window.location.pathname;
        if (path.includes('/employee/tasks')) {
            const urlParams = new URLSearchParams(window.location.search);
            const filter = urlParams.get('filter');
            loadTasksData(filter);
        } else {
            loadOverviewData();
        }
    } catch (e) {
        showToast('Failed to update task', 'error');
    }
}

function applyTaskFilters() {
    const search = (document.getElementById('taskSearch')?.value || '').toLowerCase();
    const status = document.getElementById('statusFilter')?.value || '';
    const priority = document.getElementById('priorityFilter')?.value || '';
    const tasks = (window.__employeeTasks || []).slice();
    let filtered = tasks.filter(t => {
        const matchesSearch = !search || (t.title||'').toLowerCase().includes(search) || (t.description||'').toLowerCase().includes(search);
        const matchesStatus = !status || (t.status||'') === status;
        const matchesPriority = !priority || (t.priority||'') === priority;
        return matchesSearch && matchesStatus && matchesPriority;
    });
    // Re-render list only
    const list = document.querySelector('.task-list');
    if (!list) return;
    list.innerHTML = filtered.length ? filtered.map(task => `
        <div class="task-card" onclick="viewTask('${task.id}')">
            <div class="task-card-header">
                <h3 class="task-title">${task.title || 'Untitled Task'}</h3>
                <div class="task-badges">
                    <span class="badge badge-${(task.priority||'medium') === 'high' ? 'danger' : (task.priority||'medium') === 'medium' ? 'warning' : 'success'}">
                        ${(task.priority||'medium')} priority
                    </span>
                    <span class="badge badge-outline">
                        ${(task.status||'pending')}
                    </span>
                </div>
            </div>
            <div class="task-description">
                ${task.description||''}
            </div>
            <div class="task-meta">
                <span><i class="fas fa-project-diagram"></i> ${task.project_id || ''}</span>
                <span><i class="far fa-calendar"></i> ${task.due_date ? 'Due: '+formatDate(task.due_date) : ''}</span>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); startEmployeeTaskTimer('${task.id}')">
                    <i class="fas fa-play"></i> Start
                </button>
                <button class="btn btn-sm btn-success" onclick="event.stopPropagation(); updateTaskStatus('${task.id}', 'completed')">
                    <i class="fas fa-check"></i> Complete
                </button>
                <button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); requestTaskHelp('${task.id}')">
                    <i class="fas fa-question-circle"></i> Need Help
                </button>
            </div>
        </div>
    `).join('') : `
        <div class="empty-state">
            <i class="fas fa-tasks"></i>
            <h3>No tasks found</h3>
            <p class="empty-subtext">No tasks match your filters</p>
        </div>
    `;
}

function loadWorkloadData() {
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    // ... rest of the code remains the same ...
    
    const workloadData = {
        currentWorkload: 'balanced',
        tasksThisWeek: 15,
        tasksCompleted: 8,
        tasksPending: 5,
        tasksOverdue: 2,
        productivityScore: 78,
        weeklyTrend: 'improving',
        recommendations: [
            'Consider delegating 2 low-priority tasks',
            'Schedule focused work blocks for high-priority items',
            'Request extension for overdue tasks if needed'
        ]
    };
    
    const html = `
        <div class="workload-content">
            <!-- Workload Overview -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-chart-pie"></i> Workload Overview</h3>
                </div>
                <div class="card-body">
                    <div class="workload-stats">
                        <div class="workload-stat">
                            <div class="stat-value">${workloadData.tasksThisWeek}</div>
                            <div class="stat-label">Tasks This Week</div>
                        </div>
                        <div class="workload-stat">
                            <div class="stat-value">${workloadData.tasksCompleted}</div>
                            <div class="stat-label">Completed</div>
                        </div>
                        <div class="workload-stat">
                            <div class="stat-value">${workloadData.tasksPending}</div>
                            <div class="stat-label">Pending</div>
                        </div>
                        <div class="workload-stat">
                            <div class="stat-value">${workloadData.tasksOverdue}</div>
                            <div class="stat-label">Overdue</div>
                        </div>
                    </div>
                    
                    <div class="workload-indicators">
                        <div class="indicator-item">
                            <span class="indicator-label">Current Workload:</span>
                            <span class="indicator-value workload-${workloadData.currentWorkload}">${workloadData.currentWorkload}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Productivity Score:</span>
                            <span class="indicator-value">${workloadData.productivityScore}%</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Weekly Trend:</span>
                            <span class="indicator-value trend-${workloadData.weeklyTrend}">${workloadData.weeklyTrend}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Help & Support -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-hands-helping"></i> Request Help</h3>
                </div>
                <div class="card-body">
                    <div class="help-options">
                        <div class="help-option">
                            <i class="fas fa-user-tie"></i>
                            <div class="help-content">
                                <h4>Manager Assistance</h4>
                                <p>Request help from your manager for task prioritization or delegation</p>
                                <button class="btn btn-primary btn-sm" onclick="requestManagerHelp()">
                                    Request Help
                                </button>
                            </div>
                        </div>
                        
                        <div class="help-option">
                            <i class="fas fa-users"></i>
                            <div class="help-content">
                                <h4>Team Collaboration</h4>
                                <p>Ask team members for assistance with specific tasks</p>
                                <button class="btn btn-outline btn-sm" onclick="requestTeamHelp()">
                                    Collaborate
                                </button>
                            </div>
                        </div>
                        
                        <div class="help-option">
                            <i class="fas fa-clock"></i>
                            <div class="help-content">
                                <h4>Deadline Extension</h4>
                                <p>Request additional time for tasks if needed</p>
                                <button class="btn btn-outline btn-sm" onclick="requestExtension()">
                                    Request Extension
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recommendations -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-lightbulb"></i> Recommendations</h3>
                </div>
                <div class="card-body">
                    <ul class="recommendations-list">
                        ${workloadData.recommendations.map(rec => `
                            <li class="recommendation-item">
                                <i class="fas fa-check-circle"></i>
                                <span>${rec}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
}

function loadLeaveData(filter = null) {
    // Guard: if server-rendered leave view is present, do nothing
    if (document.querySelector('.leave-management')) return;
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    
    const leaveData = {
        balance: {
            annual: 15,
            sick: 10,
            personal: 5
        },
        requests: [
            { id: 1, type: 'Annual', startDate: '2024-02-01', endDate: '2024-02-05', days: 5, status: 'approved', reason: 'Family vacation' },
            { id: 2, type: 'Sick', startDate: '2024-01-15', endDate: '2024-01-16', days: 2, status: 'approved', reason: 'Medical appointment' },
            { id: 3, type: 'Personal', startDate: '2024-02-20', endDate: '2024-02-20', days: 1, status: 'pending', reason: 'Personal work' }
        ]
    };
    
    let filteredRequests = leaveData.requests;
    if (filter === 'pending') {
        filteredRequests = leaveData.requests.filter(req => req.status === 'pending');
    } else if (filter === 'approved') {
        filteredRequests = leaveData.requests.filter(req => req.status === 'approved');
    }
    
    const html = `
        <div class="leave-content">
            <!-- Leave Balance -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-wallet"></i> Leave Balance</h3>
                </div>
                <div class="card-body">
                    <div class="leave-balance">
                        <div class="balance-item">
                            <div class="balance-type">Annual Leave</div>
                            <div class="balance-days">${leaveData.balance.annual} days</div>
                        </div>
                        <div class="balance-item">
                            <div class="balance-type">Sick Leave</div>
                            <div class="balance-days">${leaveData.balance.sick} days</div>
                        </div>
                        <div class="balance-item">
                            <div class="balance-type">Personal Leave</div>
                            <div class="balance-days">${leaveData.balance.personal} days</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Leave Requests -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-list"></i> Leave Requests</h3>
                    <button class="btn btn-primary" onclick="applyForLeave()">
                        <i class="fas fa-plus"></i> Apply for Leave
                    </button>
                </div>
                <div class="card-body">
                    ${filteredRequests.length > 0 ? `
                        <div class="leave-requests">
                            ${filteredRequests.map(request => `
                                <div class="leave-request">
                                    <div class="request-info">
                                        <div class="request-type">${request.type} Leave</div>
                                        <div class="request-dates">${formatDate(request.startDate)} - ${formatDate(request.endDate)} (${request.days} days)</div>
                                        <div class="request-reason">${request.reason}</div>
                                    </div>
                                    <div class="request-status">
                                        <span class="status-badge status-${request.status}">${request.status}</span>
                                        ${request.status === 'pending' ? `
                                            <button class="btn btn-sm btn-outline" onclick="cancelLeaveRequest(${request.id})">
                                                Cancel
                                            </button>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="empty-state">
                            <i class="fas fa-calendar"></i>
                            <h3>No leave requests found</h3>
                            <p class="empty-subtext">${filter ? `No ${filter} leave requests` : 'No leave requests submitted yet'}</p>
                            <button class="btn btn-primary mt-3" onclick="applyForLeave()">
                                <i class="fas fa-plus"></i>
                                Apply for Leave
                            </button>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
}

function loadReportsData() {
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    
    const reportsData = {
        performance: {
            tasksCompleted: 45,
            onTimeRate: 85,
            productivity: 78,
            qualityScore: 92
        },
        monthlyStats: [
            { month: 'Jan', tasks: 12, completed: 10 },
            { month: 'Feb', tasks: 15, completed: 12 },
            { month: 'Mar', tasks: 18, completed: 16 },
            { month: 'Apr', tasks: 14, completed: 12 }
        ]
    };
    
    const html = `
        <div class="reports-content">
            <!-- Performance Overview -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-chart-line"></i> Performance Overview</h3>
                </div>
                <div class="card-body">
                    <div class="performance-stats">
                        <div class="performance-stat">
                            <div class="stat-value">${reportsData.performance.tasksCompleted}</div>
                            <div class="stat-label">Tasks Completed</div>
                        </div>
                        <div class="performance-stat">
                            <div class="stat-value">${reportsData.performance.onTimeRate}%</div>
                            <div class="stat-label">On Time Rate</div>
                        </div>
                        <div class="performance-stat">
                            <div class="stat-value">${reportsData.performance.productivity}%</div>
                            <div class="stat-label">Productivity</div>
                        </div>
                        <div class="performance-stat">
                            <div class="stat-value">${reportsData.performance.qualityScore}%</div>
                            <div class="stat-label">Quality Score</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Report Actions -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-download"></i> Generate Reports</h3>
                </div>
                <div class="card-body">
                    <div class="report-actions">
                        <button class="btn btn-outline" onclick="generatePerformanceReport()">
                            <i class="fas fa-chart-bar"></i>
                            Performance Report
                        </button>
                        <button class="btn btn-outline" onclick="generateTaskReport()">
                            <i class="fas fa-tasks"></i>
                            Task Report
                        </button>
                        <button class="btn btn-outline" onclick="generateTimeReport()">
                            <i class="fas fa-clock"></i>
                            Time Report
                        </button>
                    </div>
                </div>
            </div>

            <!-- Monthly Statistics -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-calendar-alt"></i> Monthly Statistics</h3>
                </div>
                <div class="card-body">
                    <div class="monthly-stats">
                        ${reportsData.monthlyStats.map(stat => `
                            <div class="month-stat">
                                <div class="month-name">${stat.month}</div>
                                <div class="month-tasks">
                                    <span class="task-count">${stat.completed}/${stat.tasks}</span>
                                    <span class="task-label">tasks completed</span>
                                </div>
                                <div class="completion-rate">
                                    ${Math.round((stat.completed / stat.tasks) * 100)}%
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
}

function loadNotificationsData() {
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;

    fetch('/api/employee/notifications', { cache: 'no-store' })
        .then((response) => {
            if (!response.ok) throw new Error('Failed to load notifications');
            return response.json();
        })
        .then((notificationsData) => {
            const html = `
                <div class="notifications-content">
                    <div class="content-card">
                        <div class="card-header">
                            <h3><i class="fas fa-bell"></i> Notifications</h3>
                            <button class="btn btn-outline" onclick="markAllAsRead()">
                                <i class="fas fa-check-double"></i> Mark All as Read
                            </button>
                        </div>
                        <div class="card-body">
                            <div class="notifications-list">
                                ${notificationsData.length > 0 ? notificationsData.map(notification => `
                                    <div class="notification-item ${notification.is_read ? 'read' : 'unread'}" onclick="viewNotification('${notification.id}')">
                                        <div class="notification-icon">
                                            <i class="fas fa-${notification.type === 'task' ? 'tasks' : notification.type === 'project' ? 'target' : notification.type === 'leave' ? 'calendar-check' : 'cog'}"></i>
                                        </div>
                                        <div class="notification-content">
                                            <div class="notification-title">${notification.title}</div>
                                            <div class="notification-message">${notification.message}</div>
                                            <div class="notification-time">${notification.created_at || 'Just now'}</div>
                                        </div>
                                        ${!notification.is_read ? `<div class="notification-badge"></div>` : ''}
                                    </div>
                                `).join('') : `
                                    <div class="empty-state">
                                        <i class="fas fa-bell-slash"></i>
                                        <h3>No notifications</h3>
                                        <p class="empty-subtext">You're all caught up!</p>
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            contentArea.innerHTML = html;
        })
        .catch((error) => {
            console.error(error);
            contentArea.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-triangle-exclamation"></i>
                    <h3>Unable to load notifications</h3>
                    <p class="empty-subtext">Please try again in a moment.</p>
                </div>
            `;
        });
}

function loadProfileData() {
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    
    // Sample profile data - in real app, this would come from the backend
    const profileData = {
        name: 'John Doe',
        email: 'john.doe@company.com',
        position: 'Senior Developer',
        department: 'Engineering',
        joinDate: '2022-03-15',
        phone: '+1 (555) 123-4567',
        location: 'New York, USA',
        skills: ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
        bio: 'Passionate developer with 5+ years of experience in web development.'
    };
    
    const html = `
        <div class="profile-content">
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-user"></i> Personal Information</h3>
                    <button class="btn btn-outline" onclick="editProfile()">
                        <i class="fas fa-edit"></i> Edit Profile
                    </button>
                </div>
                <div class="card-body">
                    <div class="profile-info">
                        <div class="info-row">
                            <div class="info-label">Full Name</div>
                            <div class="info-value">${profileData.name}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Email</div>
                            <div class="info-value">${profileData.email}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Position</div>
                            <div class="info-value">${profileData.position}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Department</div>
                            <div class="info-value">${profileData.department}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Join Date</div>
                            <div class="info-value">${formatDate(profileData.joinDate)}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Phone</div>
                            <div class="info-value">${profileData.phone}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Location</div>
                            <div class="info-value">${profileData.location}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-star"></i> Skills & Expertise</h3>
                </div>
                <div class="card-body">
                    <div class="skills-list">
                        ${profileData.skills.map(skill => `
                            <span class="skill-tag">${skill}</span>
                        `).join('')}
                    </div>
                </div>
            </div>

            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-file-alt"></i> Bio</h3>
                </div>
                <div class="card-body">
                    <p class="bio-text">${profileData.bio}</p>
                </div>
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
}

function loadSettingsData() {
    const contentArea = document.getElementById('dashboard-view');
    if (!contentArea) return;
    
    const settingsData = {
        emailNotifications: true,
        pushNotifications: false,
        taskReminders: true,
        deadlineAlerts: true,
        theme: 'system',
        language: 'en',
        timezone: 'America/New_York'
    };
    
    const html = `
        <div class="settings-content">
            <!-- Notification Settings -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-bell"></i> Notification Settings</h3>
                </div>
                <div class="card-body">
                    <div class="settings-list">
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">Email Notifications</div>
                                <div class="setting-description">Receive notifications via email</div>
                            </div>
                            <label class="switch">
                                <input type="checkbox" ${settingsData.emailNotifications ? 'checked' : ''} onchange="updateSetting('emailNotifications', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">Push Notifications</div>
                                <div class="setting-description">Receive browser push notifications</div>
                            </div>
                            <label class="switch">
                                <input type="checkbox" ${settingsData.pushNotifications ? 'checked' : ''} onchange="updateSetting('pushNotifications', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">Task Reminders</div>
                                <div class="setting-description">Get reminders for upcoming tasks</div>
                            </div>
                            <label class="switch">
                                <input type="checkbox" ${settingsData.taskReminders ? 'checked' : ''} onchange="updateSetting('taskReminders', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">Deadline Alerts</div>
                                <div class="setting-description">Alert for approaching deadlines</div>
                            </div>
                            <label class="switch">
                                <input type="checkbox" ${settingsData.deadlineAlerts ? 'checked' : ''} onchange="updateSetting('deadlineAlerts', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Appearance Settings -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-palette"></i> Appearance</h3>
                </div>
                <div class="card-body">
                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">Theme</div>
                            <div class="setting-description">Choose your preferred theme</div>
                        </div>
                        <select class="form-select" onchange="updateSetting('theme', this.value)">
                            <option value="light" ${settingsData.theme === 'light' ? 'selected' : ''}>Light</option>
                            <option value="dark" ${settingsData.theme === 'dark' ? 'selected' : ''}>Dark</option>
                            <option value="system" ${settingsData.theme === 'system' ? 'selected' : ''}>System</option>
                        </select>
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">Language</div>
                            <div class="setting-description">Choose your preferred language</div>
                        </div>
                        <select class="form-select" onchange="updateSetting('language', this.value)">
                            <option value="en" ${settingsData.language === 'en' ? 'selected' : ''}>English</option>
                            <option value="es" ${settingsData.language === 'es' ? 'selected' : ''}>Spanish</option>
                            <option value="fr" ${settingsData.language === 'fr' ? 'selected' : ''}>French</option>
                        </select>
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">Timezone</div>
                            <div class="setting-description">Set your local timezone</div>
                        </div>
                        <select class="form-select" onchange="updateSetting('timezone', this.value)">
                            <option value="America/New_York" ${settingsData.timezone === 'America/New_York' ? 'selected' : ''}>Eastern Time</option>
                            <option value="America/Chicago" ${settingsData.timezone === 'America/Chicago' ? 'selected' : ''}>Central Time</option>
                            <option value="America/Denver" ${settingsData.timezone === 'America/Denver' ? 'selected' : ''}>Mountain Time</option>
                            <option value="America/Los_Angeles" ${settingsData.timezone === 'America/Los_Angeles' ? 'selected' : ''}>Pacific Time</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Account Actions -->
            <div class="content-card">
                <div class="card-header">
                    <h3><i class="fas fa-shield-alt"></i> Account Security</h3>
                </div>
                <div class="card-body">
                    <div class="security-actions">
                        <button class="btn btn-outline" onclick="changePassword()">
                            <i class="fas fa-key"></i> Change Password
                        </button>
                        <button class="btn btn-outline" onclick="exportData()">
                            <i class="fas fa-download"></i> Export Data
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    contentArea.innerHTML = html;
}

function updateNotificationBadges() {
    const badge = document.getElementById('notification-badge');
    if (!badge) return;

    fetch('/api/employee/notifications', { cache: 'no-store' })
        .then((response) => (response.ok ? response.json() : []))
        .then((rows) => {
            const list = Array.isArray(rows) ? rows : [];
            const unread = list.filter((item) => !Boolean(item.is_read)).length;
            badge.textContent = String(unread);
        })
        .catch(() => {
            badge.textContent = '0';
        });
}

function updateWorkloadIndicator() {
    const workloadStatus = document.getElementById('workload-status');
    const workloadMessage = document.getElementById('workload-message');
    
    if (workloadStatus && workloadMessage) {
        // Sample workload data
        const workload = 'balanced';
        
        workloadStatus.textContent = workload;
        workloadStatus.className = `workload-status workload-${workload}`;
        
        switch(workload) {
            case 'light':
                workloadMessage.textContent = 'Light workload';
                break;
            case 'balanced':
                workloadMessage.textContent = 'Manageable workload';
                break;
            case 'heavy':
                workloadMessage.textContent = 'Consider requesting help';
                break;
        }
    }
}

function showToast(message, type = 'success') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <strong>${type === 'success' ? 'Success' : 'Error'}</strong>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// FIXED BUTTON FUNCTIONS - Now they open modal forms

function editProfile() {
    try {
        if (window.openEditProfileDialog) {
            window.openEditProfileDialog(window.__employeeProfile || {});
            return;
        }
    } catch (e) {}
    // Fallback to legacy modal
    showProfileModal();
}

function changePassword() {
    if (typeof apiChangePassword === 'function') {
        apiChangePassword();
        return;
    }
    // Fallback modal
    showPasswordModal();
}

function exportData() {
    console.log('Exporting data...');
    showExportModal();
}

function applyForLeave() {
    console.log('Opening leave application form...');
    showLeaveModal();
}

function createNewTask() {
    console.log('Opening task creation form...');
    showTaskModal();
}

// Modal Functions
function showProfileModal() {
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Edit Profile</h3>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="profileForm">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" class="form-input" value="John Doe">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" class="form-input" value="john.doe@company.com">
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" class="form-input" value="+1 (555) 123-4567">
                        </div>
                        <div class="form-group">
                            <label>Location</label>
                            <input type="text" class="form-input" value="New York, USA">
                        </div>
                        <div class="form-group">
                            <label>Bio</label>
                            <textarea class="form-input" rows="4">Passionate developer with 5+ years of experience in web development.</textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeModal(event)">Cancel</button>
                    <button class="btn btn-primary" onclick="saveProfile()">Save Changes</button>
                </div>
            </div>
        </div>
    `;
    showModal(modalHtml);
}

function showPasswordModal() {
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Change Password</h3>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="passwordForm">
                        <div class="form-group">
                            <label>Current Password</label>
                            <input type="password" class="form-input" placeholder="Enter current password">
                        </div>
                        <div class="form-group">
                            <label>New Password</label>
                            <input type="password" class="form-input" placeholder="Enter new password">
                        </div>
                        <div class="form-group">
                            <label>Confirm New Password</label>
                            <input type="password" class="form-input" placeholder="Confirm new password">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeModal(event)">Cancel</button>
                    <button class="btn btn-primary" onclick="updatePassword()">Update Password</button>
                </div>
            </div>
        </div>
    `;
    showModal(modalHtml);
}

function showExportModal() {
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Export Data</h3>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Choose the data you want to export:</p>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" checked> Profile Information
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" checked> Task History
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" checked> Project Data
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox"> Performance Reports
                        </label>
                    </div>
                    <div class="form-group">
                        <label>Format</label>
                        <select class="form-select">
                            <option value="json">JSON</option>
                            <option value="csv">CSV</option>
                            <option value="pdf">PDF</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeModal(event)">Cancel</button>
                    <button class="btn btn-primary" onclick="startExport()">Export Data</button>
                </div>
            </div>
        </div>
    `;
    showModal(modalHtml);
}

function showLeaveModal() {
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Apply for Leave</h3>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="leaveForm">
                        <div class="form-group">
                            <label>Leave Type</label>
                            <select class="form-select">
                                <option value="annual">Annual Leave</option>
                                <option value="sick">Sick Leave</option>
                                <option value="personal">Personal Leave</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Start Date</label>
                            <input type="date" class="form-input">
                        </div>
                        <div class="form-group">
                            <label>End Date</label>
                            <input type="date" class="form-input">
                        </div>
                        <div class="form-group">
                            <label>Reason</label>
                            <textarea class="form-input" rows="4" placeholder="Enter reason for leave"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeModal(event)">Cancel</button>
                    <button class="btn btn-primary" onclick="submitLeaveRequest()">Submit Request</button>
                </div>
            </div>
        </div>
    `;
    showModal(modalHtml);
}

function showTaskModal() {
    const modalHtml = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>Create New Task</h3>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="taskForm">
                        <div class="form-group">
                            <label>Task Title</label>
                            <input type="text" class="form-input" placeholder="Enter task title">
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="form-input" rows="4" placeholder="Enter task description"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Priority</label>
                            <select class="form-select">
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Due Date</label>
                            <input type="date" class="form-input">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeModal(event)">Cancel</button>
                    <button class="btn btn-primary" onclick="createTask()">Create Task</button>
                </div>
            </div>
        </div>
    `;
    showModal(modalHtml);
}

// Modal Utility Functions
function showModal(html) {
    // Remove any existing modals
    const existingModals = document.querySelectorAll('.modal-overlay');
    existingModals.forEach(modal => modal.remove());
    
    // Add new modal to modal container or body
    const modalContainer = document.getElementById('modal-container') || document.body;
    modalContainer.insertAdjacentHTML('beforeend', html);
}

function closeModal(event) {
    event.preventDefault();
    event.stopPropagation();
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => modal.remove());
}

// Modal Action Functions
function saveProfile() {
    showToast('Profile updated successfully!', 'success');
    closeModal(event);
}

function updatePassword() {
    showToast('Password updated successfully!', 'success');
    closeModal(event);
}

function startExport() {
    showToast('Export started. You will receive an email when ready.', 'success');
    closeModal(event);
}

function submitLeaveRequest() {
    showToast('Leave request submitted successfully!', 'success');
    closeModal(event);
}

function createTask() {
    showToast('Task created successfully!', 'success');
    closeModal(event);
}

function escapeMarkup(value) {
    return String(value == null ? '' : value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

async function getEmployeeProjectContext() {
    let projects = Array.isArray(window.__employeeProjects) ? window.__employeeProjects : [];
    let tasks = Array.isArray(window.__employeeTasks) ? window.__employeeTasks : [];

    if (!projects.length) {
        projects = await fetch('/api/employee/projects').then(r => r.json()).catch(() => []);
        window.__employeeProjects = projects;
    }

    if (!tasks.length) {
        tasks = await fetch('/api/employee/tasks').then(r => r.json()).catch(() => []);
        window.__employeeTasks = tasks;
    }

    return { projects, tasks };
}

function getProjectProgress(project, tasksForProject) {
    const explicitProgress = Number.parseInt(project?.progress, 10);
    if (Number.isFinite(explicitProgress)) return explicitProgress;
    if (!tasksForProject.length) return 0;
    const completed = tasksForProject.filter(t => (t.status || '').toLowerCase() === 'completed').length;
    return Math.round((completed / tasksForProject.length) * 100);
}

// Additional functions for the new sections
async function viewProjectTasks(projectId) {
    const pid = String(projectId);
    const { projects, tasks } = await getEmployeeProjectContext();
    const project = projects.find(p => String(p.id) === pid);
    const projectTasks = tasks.filter(t => String(t.project_id) === pid);

    const title = project?.name || `Project ${pid}`;
    const taskHtml = projectTasks.length ? projectTasks.map(task => `
        <div class="task-item">
            <span class="task-name">${escapeMarkup(task.title || 'Untitled Task')}</span>
            <span class="task-assignee">${escapeMarkup(task.assignee_name || task.assignee_id || 'Unassigned')}</span>
            <span class="task-status-badge ${(task.status || 'pending').toLowerCase()}">${escapeMarkup(task.status || 'pending')}</span>
        </div>
    `).join('') : `
        <div class="empty-state">
            <i class="fas fa-list"></i>
            <h3>No tasks linked</h3>
            <p class="empty-subtext">This project does not have assigned tasks yet.</p>
        </div>
    `;

    showModal(`
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal modal-lg" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>${escapeMarkup(title)} Tasks</h3>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="project-tasks">
                        ${taskHtml}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeModal(event)">Close</button>
                </div>
            </div>
        </div>
    `);
}

function getEmployeeTaskRecord(taskId) {
    return (window.__employeeTasks || []).find((task) => String(task.id || '') === String(taskId || '')) || null;
}

async function submitEmployeeHelpRequest(payload, successMessage) {
    try {
        const response = await fetch('/api/employee/help-request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload || {})
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(result.error || 'Unable to submit help request');
        }
        showToast(result.message || successMessage || 'Help request sent', 'success');
        return result;
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Unable to submit help request', 'error');
        throw error;
    }
}

function requestManagerHelp(taskId = '') {
    const task = getEmployeeTaskRecord(taskId);
    return submitEmployeeHelpRequest({
        task_id: task ? task.id : '',
        message: task
            ? `I need help with "${task.title || 'this task'}". Please review priorities or suggest support.`
            : 'I need help with my current workload and priorities.',
        urgency: 'medium',
        recipient_type: 'manager',
        request_type: 'help'
    }, 'Help request sent to manager');
}

function requestTeamHelp(taskId = '') {
    const task = getEmployeeTaskRecord(taskId);
    return submitEmployeeHelpRequest({
        task_id: task ? task.id : '',
        message: task
            ? `I need collaboration support on "${task.title || 'this task'}".`
            : 'I need collaboration support on my current workload.',
        urgency: 'medium',
        recipient_type: 'teammate',
        request_type: 'collaboration'
    }, 'Team collaboration request sent');
}

function requestExtension(taskId = '') {
    const task = getEmployeeTaskRecord(taskId);
    return submitEmployeeHelpRequest({
        task_id: task ? task.id : '',
        message: task
            ? `I need additional time to complete "${task.title || 'this task'}".`
            : 'I need a deadline extension for my current workload.',
        urgency: 'medium',
        recipient_type: 'manager',
        request_type: 'extension'
    }, 'Extension request submitted');
}

function cancelLeaveRequest(requestId) {
    showToast(`Leave request ${requestId} cancelled`, 'success');
}

function generatePerformanceReport() {
    showToast('Generating performance report...', 'success');
}

function generateTaskReport() {
    showToast('Generating task report...', 'success');
}

function generateTimeReport() {
    showToast('Generating time report...', 'success');
}

function markAllAsRead() {
    fetch('/api/employee/notifications/read-all', { method: 'POST' })
        .then((response) => {
            if (!response.ok) throw new Error('Failed to update notifications');
            showToast('All notifications marked as read', 'success');
            loadNotificationsData();
            updateNotificationBadge();
        })
        .catch((error) => {
            console.error(error);
            showToast('Unable to update notifications', 'error');
        });
}

function viewNotification(notificationId) {
    fetch(`/api/employee/notifications/${encodeURIComponent(notificationId)}/read`, { method: 'POST' })
        .then((response) => {
            if (!response.ok) throw new Error('Failed to update notification');
            loadNotificationsData();
            updateNotificationBadge();
        })
        .catch((error) => {
            console.error(error);
            showToast('Unable to open notification', 'error');
        });
}

function updateSetting(setting, value) {
    console.log(`Updating setting ${setting} to ${value}`);
    showToast(`Setting updated: ${setting}`, 'success');
}

async function startEmployeeTaskTimer(taskId) {
    try {
        const response = await fetch('/api/employee/tasks/start-timer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId })
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(result.error || 'Failed to start task timer');
        }
        showToast(result.already_running ? 'Task timer is already running' : 'Task timer started', 'success');

        const path = window.location.pathname;
        if (path.includes('/employee/tasks')) {
            const urlParams = new URLSearchParams(window.location.search);
            loadTasksData(urlParams.get('filter'));
        } else {
            loadOverviewData();
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Failed to start task timer', 'error');
    }
}

async function viewTask(taskId) {
    const tid = String(taskId || '').trim();
    let tasks = Array.isArray(window.__employeeTasks) ? window.__employeeTasks : [];
    let projects = Array.isArray(window.__employeeProjects) ? window.__employeeProjects : [];

    if (!tasks.length) {
        tasks = await fetch('/api/employee/tasks', { cache: 'no-store' }).then(r => (r.ok ? r.json() : [])).catch(() => []);
        window.__employeeTasks = tasks;
    }
    if (!projects.length) {
        projects = await fetch('/api/employee/projects', { cache: 'no-store' }).then(r => (r.ok ? r.json() : [])).catch(() => []);
        window.__employeeProjects = projects;
    }

    const task = (tasks || []).find((item) => String(item.id || '') === tid);
    if (!task) {
        showToast('Task details are unavailable.', 'error');
        return;
    }
    if (typeof window.openTaskDetailsDialog === 'function') {
        window.openTaskDetailsDialog(tid, tasks, [], projects);
        return;
    }
    showToast('Task details dialog is unavailable.', 'error');
}

async function viewProject(projectId) {
    const pid = String(projectId);
    const { projects, tasks } = await getEmployeeProjectContext();
    const project = projects.find(p => String(p.id) === pid);

    if (!project) {
        showToast('Project details are unavailable.', 'error');
        return;
    }

    const projectTasks = tasks.filter(t => String(t.project_id) === pid);
    const progress = getProjectProgress(project, projectTasks);
    const completed = projectTasks.filter(t => (t.status || '').toLowerCase() === 'completed').length;
    const dueDate = project.endDate || project.end_date || '';
    const startDate = project.startDate || project.start_date || '';

    showModal(`
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal modal-lg" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <div>
                        <h3>${escapeMarkup(project.name || 'Untitled Project')}</h3>
                        <p class="modal-subtitle">${escapeMarkup(project.description || 'No description provided.')}</p>
                    </div>
                    <button class="modal-close" onclick="closeModal(event)">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="project-stats">
                        <div class="stat-box">
                            <div class="stat-label">Status</div>
                            <div class="stat-value">${escapeMarkup(project.status || 'planning')}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Tasks</div>
                            <div class="stat-value">${completed}/${projectTasks.length}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Progress</div>
                            <div class="stat-value">${progress}%</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Deadline</div>
                            <div class="stat-value">${dueDate ? formatDate(dueDate) : 'N/A'}</div>
                        </div>
                    </div>
                    <div class="project-dates">
                        <div class="date-item">
                            <i class="fas fa-play-circle"></i>
                            <span>Start: ${startDate ? formatDate(startDate) : 'N/A'}</span>
                        </div>
                        <div class="date-item">
                            <i class="fas fa-flag-checkered"></i>
                            <span>End: ${dueDate ? formatDate(dueDate) : 'N/A'}</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="viewProjectTasks('${escapeMarkup(pid)}')">
                        <i class="fas fa-list"></i> View Tasks
                    </button>
                    <button class="btn btn-primary" onclick="closeModal(event)">Close</button>
                </div>
            </div>
        </div>
    `);
}

async function updateTaskStatus(taskId, status) {
    try {
        const resp = await fetch('/api/employee/tasks/update-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId, status })
        });
        if (!resp.ok) throw new Error('Update failed');
        showToast('Task updated', 'success');

        const path = window.location.pathname;
        if (path.includes('/employee/tasks')) {
            const urlParams = new URLSearchParams(window.location.search);
            const filter = urlParams.get('filter');
            loadTasksData(filter);
        } else if (document.querySelector('.projects-grid')) {
            loadProjectsData();
        } else {
            loadOverviewData();
        }
    } catch (e) {
        showToast('Failed to update task', 'error');
    }
}

function requestTaskHelp(taskId) {
    return requestManagerHelp(taskId);
}

function applyTaskFilters() {
    const search = (document.getElementById('taskSearch')?.value || '').toLowerCase();
    const status = document.getElementById('statusFilter')?.value || '';
    const priority = document.getElementById('priorityFilter')?.value || '';
    const tasks = (window.__employeeTasks || []).slice();
    const filtered = tasks.filter(t => {
        const matchesSearch = !search || (t.title || '').toLowerCase().includes(search) || (t.description || '').toLowerCase().includes(search);
        const matchesStatus = !status || (t.status || '') === status;
        const matchesPriority = !priority || (t.priority || '') === priority;
        return matchesSearch && matchesStatus && matchesPriority;
    });

    const list = document.querySelector('.task-list');
    if (!list) return;
    list.innerHTML = filtered.length ? filtered.map(task => `
        <div class="task-card" onclick="viewTask('${task.id}')">
            <div class="task-card-header">
                <h3 class="task-title">${task.title || 'Untitled Task'}</h3>
                <div class="task-badges">
                    <span class="badge badge-${(task.priority||'medium') === 'high' ? 'danger' : (task.priority||'medium') === 'medium' ? 'warning' : 'success'}">
                        ${(task.priority||'medium')} priority
                    </span>
                    <span class="badge badge-outline">
                        ${(task.status||'pending')}
                    </span>
                </div>
            </div>
            <div class="task-description">${task.description || ''}</div>
            <div class="task-meta">
                <span><i class="fas fa-project-diagram"></i> ${task.project_id || ''}</span>
                <span><i class="far fa-calendar"></i> ${task.due_date ? 'Due: ' + formatDate(task.due_date) : ''}</span>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); startEmployeeTaskTimer('${task.id}')">
                    <i class="fas fa-play"></i> Start
                </button>
                <button class="btn btn-sm btn-success" onclick="event.stopPropagation(); updateTaskStatus('${task.id}', 'completed')">
                    <i class="fas fa-check"></i> Complete
                </button>
                <button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); requestTaskHelp('${task.id}')">
                    <i class="fas fa-question-circle"></i> Need Help
                </button>
            </div>
        </div>
    `).join('') : `
        <div class="empty-state">
            <i class="fas fa-tasks"></i>
            <h3>No tasks found</h3>
            <p class="empty-subtext">No tasks match your filters</p>
        </div>
    `;
}
