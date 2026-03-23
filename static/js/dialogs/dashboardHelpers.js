(function () {
  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function uniqueStrings(values) {
    const seen = new Set();
    const ordered = [];
    (values || []).forEach((value) => {
      const item = String(value || '').trim();
      if (!item || seen.has(item)) {
        return;
      }
      seen.add(item);
      ordered.push(item);
    });
    return ordered;
  }

  function getDashboardContext() {
    if (window.adminDashboard) {
      return { scope: 'admin', apiBase: '/api/admin', dashboard: window.adminDashboard };
    }
    if (window.teamLeadDashboard) {
      return { scope: 'teamlead', apiBase: '/api/teamlead', dashboard: window.teamLeadDashboard };
    }
    if (window.managerDashboard) {
      return { scope: 'manager', apiBase: '/api/manager', dashboard: window.managerDashboard };
    }
    return { scope: 'employee', apiBase: '/api/employee', dashboard: null };
  }

  function notify(message, type = 'info') {
    const context = getDashboardContext();
    if (context.dashboard && typeof context.dashboard.showNotification === 'function') {
      context.dashboard.showNotification(message, type);
      return;
    }
    if (typeof window.showNotification === 'function' && window.showNotification !== notify) {
      window.showNotification(message, type);
      return;
    }
    window.alert(message);
  }

  async function refreshView() {
    window.location.reload();
  }

  async function requestJson(url, options = {}) {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
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

  function getDashboardCollection(name) {
    const context = getDashboardContext();
    const items = context.dashboard && Array.isArray(context.dashboard[name]) ? context.dashboard[name] : [];
    return items;
  }

  function buildEmployeeMap(employees) {
    const map = new Map();
    (employees || []).forEach((employee) => {
      map.set(String(employee.id || '').trim(), employee);
    });
    return map;
  }

  function parseTeamMembers(project) {
    if (!project) {
      return [];
    }
    if (Array.isArray(project.team_members)) {
      return uniqueStrings(project.team_members);
    }
    if (Array.isArray(project.teamMembers)) {
      return uniqueStrings(project.teamMembers);
    }
    return uniqueStrings(String(project.team_members || '').split(','));
  }

  function getEmployeeName(employeeId, employees) {
    const employee = buildEmployeeMap(employees).get(String(employeeId || '').trim());
    return employee ? employee.name || employee.fullName || employee.email || employeeId : '';
  }

  function getDefaultCompanyName() {
    const context = getDashboardContext();
    if (context.dashboard && context.dashboard.systemSettings && context.dashboard.systemSettings.company_name) {
      return String(context.dashboard.systemSettings.company_name);
    }
    const employees = getDashboardCollection('employees');
    const projects = getDashboardCollection('projects');
    const company =
      employees.find((employee) => employee.company)?.company ||
      projects.find((project) => project.company)?.company ||
      'TaskVise HyperScale Operations Consortium';
    return String(company || 'TaskVise HyperScale Operations Consortium');
  }

  window.TaskViseDashboardHelpers = {
    escapeHtml,
    uniqueStrings,
    getDashboardContext,
    getDashboardCollection,
    notify,
    refreshView,
    requestJson,
    buildEmployeeMap,
    parseTeamMembers,
    getEmployeeName,
    getDefaultCompanyName,
  };
})();
