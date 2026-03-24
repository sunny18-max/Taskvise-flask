const chartInstances = {};
let allCompanies = [];
let platformStats = {};
let editingCompanyId = null;

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupMobileSidebar();
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    showSection((window.location.hash || '#dashboard').slice(1), false);
    refreshAllData(true);
});

function setupEventListeners() {
    document.querySelectorAll('.nav-link').forEach((link) => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            showSection(link.dataset.section || 'dashboard');
            closeMobileSidebar();
        });
    });

    document.querySelectorAll('[data-open-section]').forEach((button) => {
        button.addEventListener('click', () => {
            showSection(button.dataset.openSection || 'dashboard');
            closeMobileSidebar();
        });
    });

    document.getElementById('refresh-dashboard-btn')?.addEventListener('click', refreshAllData);
    document.getElementById('add-company-btn')?.addEventListener('click', openAddCompanyModal);
    document.getElementById('company-form')?.addEventListener('submit', handleCompanyFormSubmit);
    document.querySelector('.close')?.addEventListener('click', closeModal);
    document.getElementById('cancel-company-modal')?.addEventListener('click', closeModal);
    document.getElementById('save-settings-btn')?.addEventListener('click', saveSettings);

    document.getElementById('search-input')?.addEventListener('input', filterCompanies);
    document.getElementById('filter-status')?.addEventListener('change', filterCompanies);
    document.getElementById('filter-plan')?.addEventListener('change', filterCompanies);

    window.addEventListener('click', (event) => {
        const modal = document.getElementById('company-modal');
        if (event.target === modal) {
            closeModal();
        }
    });
}

async function refreshAllData(silent = false) {
    try {
        await Promise.all([loadCompaniesData(), updateDashboard(), loadSettings()]);
        if (!silent) {
            showToast('Founder console refreshed.', 'success');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Unable to refresh founder console.', 'error');
    }
}

function showSection(sectionName, updateHash = true) {
    const sections = {
        dashboard: {
            title: 'Platform Command Center',
            subtitle: 'Global monitoring, company controls, and operational analytics.',
        },
        companies: {
            title: 'Company Registry',
            subtitle: 'Manage onboarding, plan mix, contacts, and company status.',
        },
        analytics: {
            title: 'Founder Analytics',
            subtitle: 'Understand growth, adoption, and platform distribution trends.',
        },
        settings: {
            title: 'Founder Settings',
            subtitle: 'Tune policies and platform controls for the founder workspace.',
        },
    };

    const selectedKey = sections[sectionName] ? sectionName : 'dashboard';

    document.querySelectorAll('.content-section').forEach((section) => {
        section.classList.toggle('active', section.id === selectedKey);
    });

    document.querySelectorAll('.nav-link').forEach((link) => {
        link.classList.toggle('active', link.dataset.section === selectedKey);
    });

    document.getElementById('section-title').textContent = sections[selectedKey].title;
    document.getElementById('section-subtitle').textContent = sections[selectedKey].subtitle;

    if (selectedKey === 'analytics') {
        renderAnalyticsCharts();
    }

    if (updateHash) {
        window.location.hash = selectedKey;
    }
}

function setupMobileSidebar() {
    const toggle = document.getElementById('adminMenuToggle');
    const overlay = document.getElementById('adminSidebarOverlay');
    toggle?.addEventListener('click', () => {
        const sidebar = document.getElementById('adminSidebar');
        setMobileSidebarState(!sidebar?.classList.contains('show'));
    });
    overlay?.addEventListener('click', closeMobileSidebar);
    window.addEventListener('resize', () => {
        if (window.innerWidth > 920) {
            closeMobileSidebar();
        }
    });
}

function setMobileSidebarState(open) {
    document.getElementById('adminSidebar')?.classList.toggle('show', !!open);
    document.getElementById('adminSidebarOverlay')?.classList.toggle('show', !!open);
    document.body.style.overflow = open ? 'hidden' : '';
    document.getElementById('adminMenuToggle')?.setAttribute('aria-expanded', String(!!open));
}

function closeMobileSidebar() {
    setMobileSidebarState(false);
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
        throw new Error(data.error || data.message || `Request failed for ${url}`);
    }
    return data;
}

async function loadCompaniesData() {
    const data = await fetchJson('/api/companies');
    allCompanies = Array.isArray(data.companies) ? data.companies : [];
    renderCompaniesTable(allCompanies);
    updateCompanySummary();
    renderAnalyticsCharts();
}

async function updateDashboard() {
    platformStats = await fetchJson('/api/overview');
    updateDashboardStats();
    updateHeroSummary();
    updateAnalyticsSummary();
    renderDashboardCharts();
    renderRecentCompanies();
    renderTeamLeaderboard();
    renderPayrollTable();
}

function updateDashboardStats() {
    setText('stat-total-companies', formatNumber(platformStats.total_users));
    setText('stat-active-companies', formatNumber(platformStats.total_teams));
    setText('stat-total-users', formatNumber(platformStats.active_projects));
    setText('stat-enterprise', formatCurrency(platformStats.monthly_payroll));
    setText('stat-active-users', formatNumber(platformStats.active_users));
    setText('stat-completed-tasks', formatNumber(platformStats.completed_tasks));
    setText('stat-unread-alerts', formatNumber(platformStats.unread_notifications));
    setText('stat-on-leave', formatNumber(platformStats.on_leave_today));
}

function updateHeroSummary() {
    const settings = platformStats.settings || {};
    setText('hero-signup-status', settings.enable_signups ? 'Enabled' : 'Paused');
    setText('hero-maintenance-status', settings.maintenance_mode ? 'On' : 'Off');
    setText('hero-backup-interval', `${settings.backup_interval || 24} hours`);
    const enterprise = formatNumber(platformStats.enterprise_plans);
    const professional = formatNumber(platformStats.professional_plans);
    setText('hero-plan-mix', `${enterprise} Enterprise / ${professional} Professional`);
}

function updateCompanySummary() {
    const enterprise = allCompanies.filter((company) => normalize(company.plan_type) === 'enterprise').length;
    const professional = allCompanies.filter((company) => normalize(company.plan_type) === 'professional').length;
    const active = allCompanies.filter((company) => normalize(company.status) === 'active').length;
    setText('companies-total', formatNumber(allCompanies.length));
    setText('companies-active', formatNumber(active));
    setText('companies-enterprise', formatNumber(enterprise));
    setText('companies-professional', formatNumber(professional));
}

function updateAnalyticsSummary() {
    setText('analytics-total-projects', formatNumber(platformStats.total_projects));
    setText('analytics-total-teams', formatNumber(platformStats.total_teams));
    setText('analytics-total-employees', formatNumber(platformStats.total_employees));
    setText('analytics-total-tasks', formatNumber(platformStats.total_tasks));
}

function renderDashboardCharts() {
    upsertChart('planDistributionChart', 'doughnut', {
        labels: Object.keys(platformStats.role_distribution || {}).map(labelize),
        datasets: [{
            data: Object.values(platformStats.role_distribution || {}),
            backgroundColor: ['#2563eb', '#0f766e', '#f97316', '#14b8a6', '#8b5cf6', '#64748b'],
            borderWidth: 0,
        }],
    });

    upsertChart('usersPerCompanyChart', 'bar', {
        labels: Object.keys(platformStats.tasks_by_status || {}).map(labelize),
        datasets: [{
            label: 'Tasks',
            data: Object.values(platformStats.tasks_by_status || {}),
            backgroundColor: ['#2563eb', '#0f766e', '#f97316', '#dc2626', '#8b5cf6'],
            borderRadius: 12,
        }],
    }, {
        scales: { y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.14)' } }, x: { grid: { display: false } } },
    });
}

function renderAnalyticsCharts() {
    const industries = countBy(allCompanies, 'industry', 'General');
    const countries = countBy(allCompanies, 'country', 'Unknown');
    const planCounts = {
        Enterprise: allCompanies.filter((company) => normalize(company.plan_type) === 'enterprise').length,
        Professional: allCompanies.filter((company) => normalize(company.plan_type) === 'professional').length,
    };
    const sortedCompanies = [...allCompanies].sort((a, b) => new Date(a.signup_date || 0) - new Date(b.signup_date || 0));
    let total = 0;
    const growthData = sortedCompanies.map(() => ++total);

    upsertChart('industryChart', 'doughnut', {
        labels: Object.keys(industries),
        datasets: [{ data: Object.values(industries), backgroundColor: ['#2563eb', '#0f766e', '#f97316', '#8b5cf6', '#14b8a6', '#dc2626'], borderWidth: 0 }],
    });

    upsertChart('planTypeChart', 'doughnut', {
        labels: Object.keys(planCounts),
        datasets: [{ data: Object.values(planCounts), backgroundColor: ['#2563eb', '#0f766e'], borderWidth: 0 }],
    });

    upsertChart('countryChart', 'bar', {
        labels: Object.keys(countries).slice(0, 8),
        datasets: [{ label: 'Companies', data: Object.values(countries).slice(0, 8), backgroundColor: '#2563eb', borderRadius: 12 }],
    }, {
        scales: { y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.14)' } }, x: { grid: { display: false } } },
    });

    upsertChart('growthChart', 'line', {
        labels: sortedCompanies.map((company) => company.signup_date || ''),
        datasets: [{
            label: 'Cumulative Companies',
            data: growthData,
            borderColor: '#0f766e',
            backgroundColor: 'rgba(15, 118, 110, 0.12)',
            fill: true,
            tension: 0.35,
        }],
    });
}

function upsertChart(canvasId, type, data, extraOptions = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    chartInstances[canvasId]?.destroy();
    chartInstances[canvasId] = new Chart(canvas, {
        type,
        data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 10 } },
                tooltip: { enabled: true },
            },
            ...extraOptions,
        },
    });
}

function renderCompaniesTable(companies) {
    const tbody = document.getElementById('companies-tbody');
    if (!tbody) return;
    if (!companies.length) {
        tbody.innerHTML = `<tr><td colspan="10">No companies available.</td></tr>`;
        return;
    }
    tbody.innerHTML = companies.map((company) => `
        <tr>
            <td>${escapeHtml(company.id)}</td>
            <td>${escapeHtml(company.company_name)}</td>
            <td>${escapeHtml(company.industry)}</td>
            <td>${escapeHtml(company.country)}</td>
            <td>${formatNumber(company.employees_count)}</td>
            <td>${formatNumber(company.users_assigned)}</td>
            <td><span class="plan-badge ${normalize(company.plan_type)}">${escapeHtml(company.plan_type || 'professional')}</span></td>
            <td><span class="status-badge ${normalize(company.status)}">${escapeHtml(company.status || 'active')}</span></td>
            <td>${escapeHtml(company.contact_email)}</td>
            <td><div class="action-buttons"><button class="action-btn edit-btn" onclick="editCompany('${escapeHtml(company.id)}')">Edit</button><button class="action-btn delete-btn" onclick="deleteCompany('${escapeHtml(company.id)}')">Delete</button></div></td>
        </tr>
    `).join('');
}

function renderRecentCompanies() {
    renderRows('recent-companies-tbody', platformStats.recent_activity, 3, (item) => `
        <tr><td>${escapeHtml(item.message || 'No recent activity')}</td><td>${escapeHtml(item.time || '')}</td><td>${labelize(item.icon || 'system')}</td></tr>
    `, 'No recent platform activity.');
}

function renderTeamLeaderboard() {
    renderRows('leaderboard-tbody', platformStats.team_leaderboard, 4, (item) => `
        <tr><td><strong>${escapeHtml(item.team_name || 'Unknown Team')}</strong><br><span>${escapeHtml(item.focus_area || '')}</span></td><td>${formatNumber(item.completed_tasks)}</td><td>${formatNumber(item.active_projects)}</td><td>${formatNumber(item.member_count)}</td></tr>
    `, 'No leaderboard data available.');
}

function renderPayrollTable() {
    renderRows('payroll-tbody', platformStats.payroll_by_team, 3, (item) => `
        <tr><td>${escapeHtml(item.team_name || 'Shared Services')}</td><td>${escapeHtml(item.manager_name || 'Unassigned')}</td><td>${formatCurrency(item.payroll_total)}</td></tr>
    `, 'No payroll rollup data available.');
}

function renderRows(targetId, rows, colspan, renderer, emptyMessage) {
    const tbody = document.getElementById(targetId);
    if (!tbody) return;
    const safeRows = Array.isArray(rows) ? rows : [];
    tbody.innerHTML = safeRows.length ? safeRows.map(renderer).join('') : `<tr><td colspan="${colspan}">${emptyMessage}</td></tr>`;
}

function filterCompanies() {
    const search = (document.getElementById('search-input')?.value || '').toLowerCase();
    const status = normalize(document.getElementById('filter-status')?.value);
    const plan = normalize(document.getElementById('filter-plan')?.value);
    const filtered = allCompanies.filter((company) => {
        const companyName = String(company.company_name || '').toLowerCase();
        const industry = String(company.industry || '').toLowerCase();
        return (!search || companyName.includes(search) || industry.includes(search))
            && (!status || normalize(company.status) === status)
            && (!plan || normalize(company.plan_type) === plan);
    });
    renderCompaniesTable(filtered);
}

function openAddCompanyModal() {
    editingCompanyId = null;
    document.getElementById('modal-title').textContent = 'Add New Company';
    document.getElementById('company-form')?.reset();
    document.getElementById('company-modal')?.classList.add('show');
}

function closeModal() {
    document.getElementById('company-modal')?.classList.remove('show');
}

async function handleCompanyFormSubmit(event) {
    event.preventDefault();
    const payload = {
        company_name: document.getElementById('form-company-name').value.trim(),
        industry: document.getElementById('form-industry').value.trim(),
        country: document.getElementById('form-country').value.trim(),
        employees_count: document.getElementById('form-employees').value || 0,
        plan_type: document.getElementById('form-plan-type').value,
        contact_email: document.getElementById('form-contact-email').value.trim(),
        users_assigned: 0,
        status: 'active',
    };

    try {
        if (editingCompanyId) {
            await fetchJson(`/api/companies/${editingCompanyId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast('Company updated successfully.', 'success');
        } else {
            await fetchJson('/api/companies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast('Company added successfully.', 'success');
        }
        closeModal();
        await Promise.all([loadCompaniesData(), updateDashboard()]);
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Unable to save company.', 'error');
    }
}

window.editCompany = function editCompany(companyId) {
    const company = allCompanies.find((row) => String(row.id) === String(companyId));
    if (!company) return;
    editingCompanyId = companyId;
    document.getElementById('modal-title').textContent = 'Edit Company';
    document.getElementById('form-company-name').value = company.company_name || '';
    document.getElementById('form-industry').value = company.industry || '';
    document.getElementById('form-country').value = company.country || '';
    document.getElementById('form-employees').value = company.employees_count || 0;
    document.getElementById('form-plan-type').value = company.plan_type || 'professional';
    document.getElementById('form-contact-email').value = company.contact_email || '';
    document.getElementById('company-modal')?.classList.add('show');
};

window.deleteCompany = async function deleteCompany(companyId) {
    if (!window.confirm('Delete this company from the founder registry?')) return;
    try {
        await fetchJson(`/api/companies/${companyId}`, { method: 'DELETE' });
        await Promise.all([loadCompaniesData(), updateDashboard()]);
        showToast('Company deleted successfully.', 'success');
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Unable to delete company.', 'error');
    }
};

async function saveSettings() {
    const settings = {
        enable_signups: !!document.getElementById('enable-signups')?.checked,
        maintenance_mode: !!document.getElementById('maintenance-mode')?.checked,
        backup_interval: document.getElementById('backup-interval')?.value || 24,
    };
    try {
        await fetchJson('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings),
        });
        platformStats.settings = settings;
        updateHeroSummary();
        showToast('Founder settings saved.', 'success');
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Unable to save settings.', 'error');
    }
}

async function loadSettings() {
    const data = await fetchJson('/api/settings');
    const settings = data.settings || {};
    document.getElementById('enable-signups').checked = !!settings.enable_signups;
    document.getElementById('maintenance-mode').checked = !!settings.maintenance_mode;
    document.getElementById('backup-interval').value = settings.backup_interval || 24;
}

function updateCurrentTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        month: 'short',
        day: 'numeric',
    });
}

function showToast(message, kind = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${kind}`;
    toast.textContent = message;
    container.appendChild(toast);
    window.setTimeout(() => toast.remove(), 2800);
}

function countBy(rows, key, fallback) {
    return (rows || []).reduce((accumulator, row) => {
        const label = String(row?.[key] || fallback).trim() || fallback;
        accumulator[label] = (accumulator[label] || 0) + 1;
        return accumulator;
    }, {});
}

function normalize(value) {
    return String(value || '').trim().toLowerCase();
}

function labelize(value) {
    return String(value || '').replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatNumber(value) {
    const number = Number.parseInt(value, 10);
    return Number.isFinite(number) ? number.toLocaleString('en-IN') : '0';
}

function formatCurrency(value) {
    const number = Number.parseInt(value, 10);
    return `INR ${Number.isFinite(number) ? number.toLocaleString('en-IN') : '0'}`;
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
