// Team Lead Dashboard JS
window.teamLeadDashboard = (function(){
  async function fetchJSON(url){
    const res = await fetch(url);
    if(!res.ok) throw new Error('Request failed');
    return await res.json();
  }
  return {
    getEmployees: () => fetchJSON('/api/teamlead/employees'),
    getProjects: () => fetchJSON('/api/teamlead/projects'),
    getTasks: () => fetchJSON('/api/teamlead/tasks'),
    refreshData: () => window.location.reload(),
    showNotification: (msg, type='info') => {
      const evt = new CustomEvent('toast', { detail: { msg, type } });
      window.dispatchEvent(evt);
    }
  };
})();

function initTeamLeadDashboard(){
  const userMenuToggle = document.getElementById('userMenuToggle');
  const userDropdown = document.getElementById('userDropdown');
  if(userMenuToggle && userDropdown){
    userMenuToggle.addEventListener('click', (e)=>{
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });
    document.addEventListener('click', ()=> userDropdown.classList.remove('show'));
  }
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  if(menuToggle && sidebar){
    menuToggle.addEventListener('click', ()=> sidebar.classList.toggle('collapsed'));
  }
  console.log('Team Lead dashboard initialized');
}

document.addEventListener('DOMContentLoaded', initTeamLeadDashboard);
