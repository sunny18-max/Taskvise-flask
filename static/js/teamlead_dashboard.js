const TEAMLEAD_TRANSLATIONS = {
  en: {
    'Overview': 'Overview',
    'Team Members': 'Team Members',
    'Projects': 'Projects',
    'Tasks': 'Tasks',
    'Reports': 'Reports',
    'Workload': 'Workload',
    'Skill Development': 'Skill Development',
    'Notifications': 'Notifications',
    'Profile': 'Profile',
    'Settings': 'Settings',
    'Quick Actions': 'Quick Actions',
    'Assign Task': 'Assign Task',
    'New Project': 'New Project',
    'Team Lead Overview': 'Team Lead Overview',
    'Quick snapshot of your team and work.': 'Quick snapshot of your team and work.',
    'View and manage your team members.': 'View and manage your team members.',
    'Track projects you lead.': 'Track projects you lead.',
    'Assign and monitor tasks.': 'Assign and monitor tasks.',
    'View team performance.': 'View team performance.',
    'Workload Balancer': 'Workload Balancer',
    'Balance workload using live task and capacity data.': 'Balance workload using live task and capacity data.',
    'Track live skill gaps and development needs.': 'Track live skill gaps and development needs.',
    'Stay on top of team progress and updates.': 'Stay on top of team progress and updates.',
    'Review and update your account profile inside the team lead dashboard.': 'Review and update your account profile inside the team lead dashboard.',
    'Manage your account preferences without leaving the dashboard shell.': 'Manage your account preferences without leaving the dashboard shell.',
  },
  es: {
    'Overview': 'Resumen',
    'Team Members': 'Miembros del equipo',
    'Projects': 'Proyectos',
    'Tasks': 'Tareas',
    'Reports': 'Informes',
    'Workload': 'Carga de trabajo',
    'Skill Development': 'Desarrollo de habilidades',
    'Notifications': 'Notificaciones',
    'Profile': 'Perfil',
    'Settings': 'Configuracion',
    'Quick Actions': 'Acciones rapidas',
    'Assign Task': 'Asignar tarea',
    'New Project': 'Nuevo proyecto',
    'Team Lead Overview': 'Resumen del lider de equipo',
    'Quick snapshot of your team and work.': 'Resumen rapido de tu equipo y trabajo.',
    'View and manage your team members.': 'Ver y gestionar a los miembros de tu equipo.',
    'Track projects you lead.': 'Supervisa los proyectos que diriges.',
    'Assign and monitor tasks.': 'Asignar y supervisar tareas.',
    'View team performance.': 'Ver el rendimiento del equipo.',
    'Workload Balancer': 'Balanceador de carga',
    'Balance workload using live task and capacity data.': 'Equilibra la carga usando datos en vivo de tareas y capacidad.',
    'Track live skill gaps and development needs.': 'Supervisa brechas de habilidades y necesidades de desarrollo.',
    'Stay on top of team progress and updates.': 'Mantente al dia con el progreso y las actualizaciones del equipo.',
    'Review and update your account profile inside the team lead dashboard.': 'Revisa y actualiza tu perfil dentro del panel del lider de equipo.',
    'Manage your account preferences without leaving the dashboard shell.': 'Gestiona tus preferencias sin salir del panel.',
  },
  fr: {
    'Overview': 'Vue d ensemble',
    'Team Members': 'Membres de l equipe',
    'Projects': 'Projets',
    'Tasks': 'Taches',
    'Reports': 'Rapports',
    'Workload': 'Charge de travail',
    'Skill Development': 'Developpement des competences',
    'Notifications': 'Notifications',
    'Profile': 'Profil',
    'Settings': 'Parametres',
    'Quick Actions': 'Actions rapides',
    'Assign Task': 'Attribuer une tache',
    'New Project': 'Nouveau projet',
    'Team Lead Overview': 'Vue du chef d equipe',
    'Quick snapshot of your team and work.': 'Apercu rapide de votre equipe et du travail.',
    'View and manage your team members.': 'Afficher et gerer les membres de votre equipe.',
    'Track projects you lead.': 'Suivez les projets que vous dirigez.',
    'Assign and monitor tasks.': 'Attribuer et suivre les taches.',
    'View team performance.': 'Voir la performance de l equipe.',
    'Workload Balancer': 'Equilibreur de charge',
    'Balance workload using live task and capacity data.': 'Equilibrez la charge avec des donnees en direct.',
    'Track live skill gaps and development needs.': 'Suivez les ecarts de competences et les besoins de developpement.',
    'Stay on top of team progress and updates.': 'Restez informe de la progression et des mises a jour.',
    'Review and update your account profile inside the team lead dashboard.': 'Consultez et mettez a jour votre profil depuis le tableau de bord.',
    'Manage your account preferences without leaving the dashboard shell.': 'Gerez vos preferences sans quitter le tableau de bord.',
  },
  de: {
    'Overview': 'Ubersicht',
    'Team Members': 'Teammitglieder',
    'Projects': 'Projekte',
    'Tasks': 'Aufgaben',
    'Reports': 'Berichte',
    'Workload': 'Auslastung',
    'Skill Development': 'Kompetenzentwicklung',
    'Notifications': 'Benachrichtigungen',
    'Profile': 'Profil',
    'Settings': 'Einstellungen',
    'Quick Actions': 'Schnellaktionen',
    'Assign Task': 'Aufgabe zuweisen',
    'New Project': 'Neues Projekt',
    'Team Lead Overview': 'Teamleiter Ubersicht',
    'Quick snapshot of your team and work.': 'Kurzer Uberblick uber Team und Arbeit.',
    'View and manage your team members.': 'Teammitglieder ansehen und verwalten.',
    'Track projects you lead.': 'Projekte verfolgen, die du leitest.',
    'Assign and monitor tasks.': 'Aufgaben zuweisen und verfolgen.',
    'View team performance.': 'Teamleistung ansehen.',
    'Workload Balancer': 'Auslastungsplaner',
    'Balance workload using live task and capacity data.': 'Auslastung mit Live-Daten zu Aufgaben und Kapazitat steuern.',
    'Track live skill gaps and development needs.': 'Kompetenzlucken und Entwicklungsbedarf verfolgen.',
    'Stay on top of team progress and updates.': 'Uber Teamfortschritt und Updates informiert bleiben.',
    'Review and update your account profile inside the team lead dashboard.': 'Profil direkt im Teamleiter-Dashboard prufen und aktualisieren.',
    'Manage your account preferences without leaving the dashboard shell.': 'Kontoeinstellungen verwalten, ohne das Dashboard zu verlassen.',
  },
};

let activeTeamLeadLanguage = localStorage.getItem('taskvise_teamlead_language') || 'en';

function tTeamLead(text) {
  const bundle = TEAMLEAD_TRANSLATIONS[activeTeamLeadLanguage] || TEAMLEAD_TRANSLATIONS.en;
  return bundle[text] || text;
}

function resolveThemeMode(theme) {
  const raw = String(theme || 'system').toLowerCase();
  if (raw === 'dark' || raw === 'light') return raw;
  return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
}

function setElementText(selector, value) {
  const element = document.querySelector(selector);
  if (element) {
    element.textContent = value;
  }
}

function setButtonLabel(selector, label) {
  const button = document.querySelector(selector);
  if (!button) return;
  const icon = button.querySelector('i');
  button.innerHTML = icon ? `${icon.outerHTML} ${label}` : label;
}

function applyTeamLeadTheme(theme = 'system') {
  const mode = String(theme || 'system').toLowerCase();
  const resolved = resolveThemeMode(mode);
  document.documentElement.setAttribute('data-theme', resolved);
  document.documentElement.setAttribute('data-theme-mode', mode);
  localStorage.setItem('taskvise_teamlead_theme', mode);
}

function applyTeamLeadLanguage(language = 'en') {
  const lang = TEAMLEAD_TRANSLATIONS[language] ? language : 'en';
  activeTeamLeadLanguage = lang;
  document.documentElement.setAttribute('lang', lang);
  localStorage.setItem('taskvise_teamlead_language', lang);

  [
    ['a[href="/teamlead/overview"] span', 'Overview'],
    ['a[href="/teamlead/team-members"] span', 'Team Members'],
    ['a[href="/teamlead/projects"] span', 'Projects'],
    ['a[href="/teamlead/tasks"] span', 'Tasks'],
    ['a[href="/teamlead/reports"] span', 'Reports'],
    ['a[href="/teamlead/workload-balancer"] span', 'Workload'],
    ['a[href="/teamlead/skill-recommendations"] span', 'Skill Development'],
    ['a[href="/teamlead/notifications"] span', 'Notifications'],
    ['a[href="/teamlead/profile"] span', 'Profile'],
    ['a[href="/teamlead/settings"] span', 'Settings'],
    ['.dropdown-item[data-view="profile"] span', 'Profile'],
    ['.dropdown-item[data-view="settings"] span', 'Settings'],
    ['.workload-header span', 'Quick Actions'],
  ].forEach(([selector, key]) => {
    setElementText(selector, tTeamLead(key));
  });

  setButtonLabel('button[onclick="openTLAssignTaskDialog()"]', tTeamLead('Assign Task'));
  setButtonLabel('button[onclick="openTLCreateProjectDialog()"]', tTeamLead('New Project'));

  const titleElement = document.getElementById('page-title');
  const subtitleElement = document.getElementById('page-subtitle');
  if (titleElement) {
    const base = titleElement.getAttribute('data-base-value') || titleElement.textContent.trim();
    titleElement.setAttribute('data-base-value', base);
    titleElement.textContent = tTeamLead(base);
  }
  if (subtitleElement) {
    const base = subtitleElement.getAttribute('data-base-value') || subtitleElement.textContent.trim();
    subtitleElement.setAttribute('data-base-value', base);
    subtitleElement.textContent = tTeamLead(base);
  }
}

async function loadTeamLeadPreferences() {
  const storedTheme = localStorage.getItem('taskvise_teamlead_theme') || 'system';
  const storedLanguage = localStorage.getItem('taskvise_teamlead_language') || 'en';
  applyTeamLeadTheme(storedTheme);
  applyTeamLeadLanguage(storedLanguage);

  try {
    const response = await fetch('/api/employee/settings', {
      cache: 'no-store',
      credentials: 'same-origin',
    });
    if (!response.ok) return;
    const result = await response.json();
    if (!(result.ok || result.success)) return;
    const settings = result.settings || {};
    applyTeamLeadTheme(settings.theme || storedTheme);
    applyTeamLeadLanguage(settings.language || storedLanguage);
  } catch (_error) {
    // Keep local preferences if server settings are unavailable.
  }
}

window.applyEmployeeTheme = applyTeamLeadTheme;
window.applyEmployeeLanguage = applyTeamLeadLanguage;
window.applyTeamLeadTheme = applyTeamLeadTheme;
window.applyTeamLeadLanguage = applyTeamLeadLanguage;

if (!window.__teamLeadThemeMediaWatcherBound && window.matchMedia) {
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const listener = () => {
    const mode = localStorage.getItem('taskvise_teamlead_theme') || 'system';
    if (mode === 'system') applyTeamLeadTheme('system');
  };
  if (typeof mq.addEventListener === 'function') {
    mq.addEventListener('change', listener);
  } else if (typeof mq.addListener === 'function') {
    mq.addListener(listener);
  }
  window.__teamLeadThemeMediaWatcherBound = true;
}

class TeamLeadDashboard {
  constructor() {
    this.currentView = 'overview';
    this.employees = [];
    this.tasks = [];
    this.projects = [];
    this.stats = {};
    this.currentUserId = null;
    this.role = 'teamlead';
    this.apiBase = '/api/teamlead';
    this.init();
  }

  init() {
    this.seedFromScriptTags();
    loadTeamLeadPreferences();
    this.loadInitialData();
    this.setupChrome();
    this.checkDatabaseStatus();
    window.addEventListener('resize', () => this.handleResponsiveSidebar());
    setInterval(() => this.checkDatabaseStatus(), 30000);
  }

  seedFromScriptTags() {
    try {
      const dataTag = document.getElementById('initial-teamlead-data') || document.getElementById('initial-manager-data');
      if (!dataTag) return false;
      const json = JSON.parse(dataTag.textContent || '{}');
      this.employees = Array.isArray(json.employees) ? json.employees : this.employees;
      this.tasks = Array.isArray(json.tasks) ? json.tasks : this.tasks;
      this.projects = Array.isArray(json.projects) ? json.projects : this.projects;
      this.stats = json.stats && typeof json.stats === 'object' ? json.stats : this.stats;
      this.currentUserId = json.current_user_id || this.currentUserId;
      this.role = json.role || this.role;
      return true;
    } catch (error) {
      console.warn('Failed to seed team lead dashboard data:', error);
      return false;
    }
  }

  async loadInitialData() {
    try {
      await Promise.all([
        this.loadEmployees(),
        this.loadTasks(),
        this.loadProjects(),
        this.loadStats(),
      ]);
      this.dispatchRefresh();
    } catch (error) {
      console.error('Error loading team lead dashboard data:', error);
      this.showNotification('Error loading team lead dashboard data', 'error');
    }
  }

  async makeAuthenticatedRequest(endpoint, options = {}) {
    const response = await fetch(endpoint, {
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch (_error) {
      payload = null;
    }

    if (!response.ok) {
      const message =
        (payload && (payload.error || payload.message)) ||
        `Request failed with status ${response.status}`;
      throw new Error(message);
    }

    return payload;
  }

  async loadEmployees() {
    const response = await this.makeAuthenticatedRequest(`${this.apiBase}/employees`);
    this.employees = Array.isArray(response) ? response : [];
    return this.employees;
  }

  async loadTasks() {
    const response = await this.makeAuthenticatedRequest(`${this.apiBase}/tasks`);
    this.tasks = Array.isArray(response) ? response : [];
    return this.tasks;
  }

  async loadProjects() {
    const response = await this.makeAuthenticatedRequest(`${this.apiBase}/projects`);
    this.projects = Array.isArray(response) ? response : [];
    return this.projects;
  }

  async loadStats() {
    const response = await this.makeAuthenticatedRequest(`${this.apiBase}/stats`);
    this.stats = response && typeof response === 'object' ? response : {};
    return this.stats;
  }

  async getEmployees() {
    if (Array.isArray(this.employees) && this.employees.length) return this.employees;
    return this.loadEmployees();
  }

  async getTasks() {
    if (Array.isArray(this.tasks) && this.tasks.length) return this.tasks;
    return this.loadTasks();
  }

  async getProjects() {
    if (Array.isArray(this.projects) && this.projects.length) return this.projects;
    return this.loadProjects();
  }

  async updateProject(projectId, updateData) {
    await this.makeAuthenticatedRequest(`${this.apiBase}/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
    await Promise.all([this.loadProjects(), this.loadTasks(), this.loadStats()]);
    this.dispatchRefresh();
    return true;
  }

  async deleteProject(projectId) {
    await this.makeAuthenticatedRequest(`${this.apiBase}/projects/${projectId}`, {
      method: 'DELETE',
    });
    await Promise.all([this.loadProjects(), this.loadTasks(), this.loadStats()]);
    this.dispatchRefresh();
    return true;
  }

  async updateTask(taskId, updateData) {
    await this.makeAuthenticatedRequest(`${this.apiBase}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
    await Promise.all([this.loadTasks(), this.loadProjects(), this.loadStats(), this.loadEmployees()]);
    this.dispatchRefresh();
    return true;
  }

  async deleteTask(taskId) {
    await this.makeAuthenticatedRequest(`${this.apiBase}/tasks/${taskId}`, {
      method: 'DELETE',
    });
    await Promise.all([this.loadTasks(), this.loadProjects(), this.loadStats(), this.loadEmployees()]);
    this.dispatchRefresh();
    return true;
  }

  async refreshData() {
    this.showNotification('Refreshing data...', 'info');
    await this.loadInitialData();
    this.dispatchRefresh();
    this.showNotification('Data refreshed successfully', 'success');
  }

  dispatchRefresh() {
    this.renderRecentTasks();
    const detail = {
      employees: this.employees,
      tasks: this.tasks,
      projects: this.projects,
      stats: this.stats,
    };
    window.dispatchEvent(new CustomEvent('managerDataRefreshed', { detail }));
    window.dispatchEvent(new CustomEvent('teamleadDataRefreshed', { detail }));
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

    const employeeMap = new Map((this.employees || []).map((employee) => [String(employee.id), employee]));
    list.innerHTML = top.map((task) => {
      const assignee = employeeMap.get(String(task.assignee_id || ''));
      const assigneeName = assignee ? (assignee.name || assignee.fullName || 'Unknown') : 'Unassigned';
      const status = String(task.status || 'pending');
      return `
        <div class="task-item">
          <div class="task-main">
            <div class="task-title">${task.title || 'Untitled Task'}</div>
            <div class="task-meta">
              <i class="fas fa-user"></i>
              ${assigneeName}
            </div>
          </div>
          <div class="task-status">
            <span class="status-badge ${status}">${status.replace('-', ' ')}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  setupChrome() {
    this.setupUserMenu();
    this.setupSidebarToggle();
    this.handleResponsiveSidebar();
  }

  setupUserMenu() {
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');
    if (!userMenuToggle || !userDropdown) return;

    userMenuToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      userDropdown.classList.toggle('show');
    });
    document.addEventListener('click', () => userDropdown.classList.remove('show'));
  }

  setupSidebarToggle() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (!menuToggle || !sidebar) return;

    menuToggle.addEventListener('click', () => {
      const isMobile = window.innerWidth <= 1024;
      if (isMobile) {
        sidebar.classList.toggle('active');
        return;
      }
      sidebar.classList.toggle('collapsed');
    });
  }

  handleResponsiveSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar || window.innerWidth <= 1024) return;
    sidebar.classList.remove('active');
  }

  async checkDatabaseStatus() {
    try {
      const response = await fetch('/api/system/health', { credentials: 'same-origin' });
      const health = await response.json();
      const statusDot = document.getElementById('statusDot');
      const statusText = document.getElementById('statusText');
      if (!statusDot || !statusText) return;

      if (health.mongodb && health.mongodb.connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'MongoDB Connected';
      } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'MongoDB Disconnected';
      }
    } catch (error) {
      console.warn('Could not check database status:', error);
      const statusText = document.getElementById('statusText');
      if (statusText) {
        statusText.textContent = 'Status Unknown';
      }
    }
  }

  showNotification(message, type = 'info') {
    const accent = getComputedStyle(
      document.querySelector('.dashboard-container') || document.documentElement
    ).getPropertyValue('--primary').trim() || '#c2410c';

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-message">${message}</span>
        <button class="notification-close" type="button">&times;</button>
      </div>
    `;

    if (!document.querySelector('#teamlead-notification-styles')) {
      const styles = document.createElement('style');
      styles.id = 'teamlead-notification-styles';
      styles.textContent = `
        .notification {
          position: fixed;
          top: 1rem;
          right: 1rem;
          background: #fff;
          border-radius: 10px;
          box-shadow: 0 12px 28px rgba(15, 23, 42, 0.16);
          border-left: 4px solid ${accent};
          z-index: 10000;
          max-width: 360px;
          animation: slideInRight 0.25s ease-out;
        }
        .notification-success { border-left-color: #10b981; }
        .notification-error { border-left-color: #ef4444; }
        .notification-warning { border-left-color: #f59e0b; }
        .notification-info { border-left-color: ${accent}; }
        .notification-content {
          padding: 1rem;
          display: flex;
          justify-content: space-between;
          gap: 0.8rem;
        }
        .notification-message {
          color: #0f172a;
          flex: 1;
        }
        .notification-close {
          background: none;
          border: none;
          color: #64748b;
          font-size: 1.2rem;
          cursor: pointer;
          padding: 0;
        }
      `;
      document.head.appendChild(styles);
    }

    notification.querySelector('.notification-close').addEventListener('click', () => notification.remove());
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
  }
}

let teamLeadDashboard;

function initTeamLeadDashboard() {
  if (window.teamLeadDashboard) {
    return window.teamLeadDashboard;
  }
  teamLeadDashboard = new TeamLeadDashboard();
  window.teamLeadDashboard = teamLeadDashboard;
  window.managerDashboard = teamLeadDashboard;
  return teamLeadDashboard;
}

initTeamLeadDashboard();
