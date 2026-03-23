let chartInstances = {};
let allCompanies = [];
let platformStats = {};

document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
    setupEventListeners();
    setupMobileSidebar();
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
});

function initializeAdmin() {
    loadCompaniesData();
    updateDashboard();
    loadSettings();
}

function setupEventListeners() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            showSection(section);
            closeMobileSidebar();
        });
    });

    document.getElementById('add-company-btn')?.addEventListener('click', openAddCompanyModal);
    document.getElementById('company-form')?.addEventListener('submit', handleCompanyFormSubmit);

    document.querySelector('.close')?.addEventListener('click', closeModal);

    document.getElementById('search-input')?.addEventListener('input', filterCompanies);
    document.getElementById('filter-status')?.addEventListener('change', filterCompanies);
    document.getElementById('filter-plan')?.addEventListener('change', filterCompanies);
}

function setMobileSidebarState(open) {
    const sidebar = document.querySelector('.admin-sidebar');
    const overlay = document.getElementById('adminSidebarOverlay');
    const toggle = document.getElementById('adminMenuToggle');
    sidebar?.classList.toggle('show', !!open);
    overlay?.classList.toggle('show', !!open);
    toggle?.classList.toggle('active', !!open);
    if (toggle) {
        toggle.setAttribute('aria-expanded', String(!!open));
    }
    document.body.classList.toggle('admin-sidebar-open', !!open);
}

function closeMobileSidebar() {
    setMobileSidebarState(false);
}

function setupMobileSidebar() {
    const toggle = document.getElementById('adminMenuToggle');
    const overlay = document.getElementById('adminSidebarOverlay');
    toggle?.addEventListener('click', function() {
        const sidebar = document.querySelector('.admin-sidebar');
        const isOpen = !!sidebar && sidebar.classList.contains('show');
        setMobileSidebarState(!isOpen);
    });
    overlay?.addEventListener('click', closeMobileSidebar);
    document.querySelector('.logout-btn')?.addEventListener('click', closeMobileSidebar);
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileSidebar();
        }
    });
}

function showSection(sectionName) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');

    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    const sectionTitles = {
        'dashboard': 'Dashboard',
        'companies': 'Companies',
        'analytics': 'Analytics',
        'settings': 'Settings'
    };
    document.getElementById('section-title').textContent = sectionTitles[sectionName];

    if (sectionName === 'analytics') {
        setTimeout(initializeAnalyticsCharts, 100);
    }
}

function loadCompaniesData() {
    fetch('/api/companies')
        .then(response => response.json())
        .then(data => {
            allCompanies = data.companies || [];
            renderCompaniesTable(allCompanies);
            updateDashboardStats();
            renderRecentCompanies();
        })
        .catch(error => {
            console.error('Error loading companies:', error);
            allCompanies = [];
        });
}

function updateDashboard() {
    fetch('/api/overview')
        .then(response => response.json())
        .then(data => {
            platformStats = data || {};
            updateDashboardStats();
            initializeDashboardCharts(data);
            renderRecentCompanies();
            renderTeamLeaderboard();
            renderPayrollTable();
        })
        .catch(error => console.error('Error loading stats:', error));
}

function updateDashboardStats() {
    const stats = platformStats && platformStats.success ? platformStats : calculateStats(allCompanies);
    document.getElementById('stat-total-companies').textContent = stats.total_users || 0;
    document.getElementById('stat-active-companies').textContent = stats.total_teams || 0;
    document.getElementById('stat-total-users').textContent = stats.active_projects || 0;
    document.getElementById('stat-enterprise').textContent = `INR ${(stats.monthly_payroll || 0).toLocaleString()}`;
    document.getElementById('stat-active-users').textContent = stats.active_users || 0;
    document.getElementById('stat-completed-tasks').textContent = stats.completed_tasks || 0;
    document.getElementById('stat-unread-alerts').textContent = stats.unread_notifications || 0;
    document.getElementById('stat-on-leave').textContent = stats.on_leave_today || 0;
}

function calculateStats(companies) {
    return {
        total_companies: companies.length,
        active_companies: companies.filter(c => c.status === 'active').length,
        total_users: companies.reduce((sum, c) => sum + parseInt(c.users_assigned || 0), 0),
        enterprise_plans: companies.filter(c => c.plan_type === 'enterprise').length,
        professional_plans: companies.filter(c => c.plan_type === 'professional').length,
        total_employees: companies.reduce((sum, c) => sum + parseInt(c.employees_count || 0), 0)
    };
}

function initializeDashboardCharts(stats) {
    const planDistChart = document.getElementById('planDistributionChart');
    if (planDistChart && !chartInstances.planDist) {
        const ctx = planDistChart.getContext('2d');
        const roleDistribution = (stats && stats.role_distribution) || {};
        chartInstances.planDist = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(roleDistribution).map(label => label.replace('_', ' ')),
                datasets: [{
                    data: Object.values(roleDistribution),
                    backgroundColor: ['#2563eb', '#0f766e', '#dc2626', '#ea580c', '#7c3aed', '#64748b'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    const usersPerCompanyChart = document.getElementById('usersPerCompanyChart');
    if (usersPerCompanyChart && !chartInstances.usersPerCompany) {
        const taskStatus = (stats && stats.tasks_by_status) || {};
        const ctx = usersPerCompanyChart.getContext('2d');
        chartInstances.usersPerCompany = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(taskStatus).map(label => label.replace('_', ' ')),
                datasets: [{
                    label: 'Tasks',
                    data: Object.values(taskStatus),
                    backgroundColor: '#2563eb'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 5
                        }
                    }
                }
            }
        });
    }
}

function initializeAnalyticsCharts(stats) {
    const industries = {};
    const countries = {};
    
    allCompanies.forEach(company => {
        industries[company.industry] = (industries[company.industry] || 0) + 1;
        countries[company.country] = (countries[company.country] || 0) + 1;
    });

    const industryCtx = document.getElementById('industryChart');
    if (industryCtx && !chartInstances.industry) {
        chartInstances.industry = new Chart(industryCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(industries),
                datasets: [{
                    data: Object.values(industries),
                    backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#a78bfa']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }

    const planCtx = document.getElementById('planTypeChart');
    if (planCtx && !chartInstances.planType) {
        const stats = calculateStats(allCompanies);
        chartInstances.planType = new Chart(planCtx, {
            type: 'doughnut',
            data: {
                labels: ['Enterprise', 'Professional'],
                datasets: [{
                    data: [stats.enterprise_plans, stats.professional_plans],
                    backgroundColor: ['#a78bfa', '#2563eb']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }

    const countryCtx = document.getElementById('countryChart');
    if (countryCtx && !chartInstances.country) {
        chartInstances.country = new Chart(countryCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(countries).slice(0, 8),
                datasets: [{
                    label: 'Companies',
                    data: Object.values(countries).slice(0, 8),
                    backgroundColor: '#2563eb'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }

    const growthCtx = document.getElementById('growthChart');
    if (growthCtx && !chartInstances.growth) {
        const sortedCompanies = allCompanies.sort((a, b) => new Date(a.signup_date) - new Date(b.signup_date));
        const cumulativeData = [];
        let total = 0;
        sortedCompanies.forEach(c => {
            total++;
            cumulativeData.push(total);
        });

        chartInstances.growth = new Chart(growthCtx, {
            type: 'line',
            data: {
                labels: sortedCompanies.map(c => c.signup_date),
                datasets: [{
                    label: 'Cumulative Companies',
                    data: cumulativeData,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }
}

function renderCompaniesTable(companies) {
    const tbody = document.getElementById('companies-tbody');
    if (!tbody) return;

    tbody.innerHTML = companies.map(company => `
        <tr>
            <td>${company.id}</td>
            <td>${company.company_name}</td>
            <td>${company.industry}</td>
            <td>${company.country}</td>
            <td>${company.employees_count}</td>
            <td>${company.users_assigned}</td>
            <td><span class="plan-badge ${company.plan_type}">${company.plan_type}</span></td>
            <td><span class="status-badge ${company.status}">${company.status}</span></td>
            <td>${company.contact_email}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit-btn" onclick="editCompany('${company.id}')">Edit</button>
                    <button class="action-btn delete-btn" onclick="deleteCompany('${company.id}')">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderRecentCompanies() {
    const tbody = document.getElementById('recent-companies-tbody');
    if (!tbody) return;
    const recent = Array.isArray(platformStats.recent_activity) ? platformStats.recent_activity : [];
    tbody.innerHTML = recent.map(item => `
        <tr>
            <td>${item.message || 'No recent activity'}</td>
            <td>${item.time || ''}</td>
            <td>${item.icon || 'system'}</td>
        </tr>
    `).join('');
}

function renderTeamLeaderboard() {
    const tbody = document.getElementById('leaderboard-tbody');
    if (!tbody) return;
    const rows = Array.isArray(platformStats.team_leaderboard) ? platformStats.team_leaderboard : [];
    tbody.innerHTML = rows.length ? rows.map(item => `
        <tr>
            <td>
                <strong>${item.team_name || 'Unknown Team'}</strong>
                <div>${item.focus_area || ''}</div>
            </td>
            <td>${item.completed_tasks || 0}</td>
            <td>${item.active_projects || 0}</td>
            <td>${item.member_count || 0}</td>
        </tr>
    `).join('') : `
        <tr>
            <td colspan="4">No team leaderboard data available.</td>
        </tr>
    `;
}

function renderPayrollTable() {
    const tbody = document.getElementById('payroll-tbody');
    if (!tbody) return;
    const rows = Array.isArray(platformStats.payroll_by_team) ? platformStats.payroll_by_team : [];
    tbody.innerHTML = rows.length ? rows.map(item => `
        <tr>
            <td>${item.team_name || 'Shared Services'}</td>
            <td>${item.manager_name || 'Unassigned'}</td>
            <td>INR ${(item.payroll_total || 0).toLocaleString()}</td>
        </tr>
    `).join('') : `
        <tr>
            <td colspan="3">No payroll rollup data available.</td>
        </tr>
    `;
}

function filterCompanies() {
    const search = document.getElementById('search-input')?.value.toLowerCase() || '';
    const status = document.getElementById('filter-status')?.value || '';
    const plan = document.getElementById('filter-plan')?.value || '';

    const filtered = allCompanies.filter(company => {
        const matchSearch = !search || 
            company.company_name.toLowerCase().includes(search) || 
            company.industry.toLowerCase().includes(search);
        const matchStatus = !status || company.status === status;
        const matchPlan = !plan || company.plan_type === plan;
        
        return matchSearch && matchStatus && matchPlan;
    });

    renderCompaniesTable(filtered);
}

function openAddCompanyModal() {
    document.getElementById('modal-title').textContent = 'Add New Company';
    document.getElementById('company-form').reset();
    document.getElementById('company-modal').classList.add('show');
}

function closeModal() {
    document.getElementById('company-modal').classList.remove('show');
}

function handleCompanyFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        company_name: document.getElementById('form-company-name').value,
        industry: document.getElementById('form-industry').value,
        country: document.getElementById('form-country').value,
        employees_count: document.getElementById('form-employees').value || 0,
        plan_type: document.getElementById('form-plan-type').value,
        contact_email: document.getElementById('form-contact-email').value,
        users_assigned: 0,
        status: 'active'
    };

    fetch('/api/companies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCompaniesData();
            closeModal();
            alert('Company added successfully!');
        } else {
            alert('Error adding company: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding company');
    });
}

function editCompany(companyId) {
    const company = allCompanies.find(c => c.id === companyId);
    if (!company) return;

    document.getElementById('modal-title').textContent = 'Edit Company';
    document.getElementById('form-company-name').value = company.company_name;
    document.getElementById('form-industry').value = company.industry;
    document.getElementById('form-country').value = company.country;
    document.getElementById('form-employees').value = company.employees_count;
    document.getElementById('form-plan-type').value = company.plan_type;
    document.getElementById('form-contact-email').value = company.contact_email;
    
    document.getElementById('company-form').onsubmit = function(e) {
        e.preventDefault();
        
        const updates = {
            company_name: document.getElementById('form-company-name').value,
            industry: document.getElementById('form-industry').value,
            country: document.getElementById('form-country').value,
            employees_count: document.getElementById('form-employees').value,
            plan_type: document.getElementById('form-plan-type').value,
            contact_email: document.getElementById('form-contact-email').value
        };

        fetch(`/api/companies/${companyId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadCompaniesData();
                closeModal();
                alert('Company updated successfully!');
            }
        })
        .catch(error => console.error('Error:', error));
    };

    document.getElementById('company-modal').classList.add('show');
}

function deleteCompany(companyId) {
    if (!confirm('Are you sure you want to delete this company?')) return;

    fetch(`/api/companies/${companyId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCompaniesData();
            alert('Company deleted successfully!');
        }
    })
    .catch(error => console.error('Error:', error));
}

function saveSettings() {
    const settings = {
        enable_signups: document.getElementById('enable-signups').checked,
        maintenance_mode: document.getElementById('maintenance-mode').checked,
        backup_interval: document.getElementById('backup-interval').value
    };

    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        alert('Settings saved successfully!');
    })
    .catch(error => console.error('Error:', error));
}

function loadSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(data => {
            const settings = data.settings || {};
            const signups = document.getElementById('enable-signups');
            const maintenance = document.getElementById('maintenance-mode');
            const backup = document.getElementById('backup-interval');
            if (signups) signups.checked = !!settings.enable_signups;
            if (maintenance) maintenance.checked = !!settings.maintenance_mode;
            if (backup) backup.value = settings.backup_interval || 24;
        })
        .catch(error => console.error('Error loading settings:', error));
}

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: true 
    });
    document.getElementById('current-time').textContent = timeString;
}

window.addEventListener('click', function(event) {
    const modal = document.getElementById('company-modal');
    if (event.target === modal) {
        closeModal();
    }
});
