class EditProfileDialog {
  open(profile = {}) {
    const html = `
    <div class="modal-overlay" id="edit-profile-modal">
      <div class="modal">
        <div class="modal-header">
          <h3>Edit Profile</h3>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <form id="edit-profile-form">
            <div class="form-group">
              <label for="prof-name">Full Name</label>
              <input id="prof-name" class="form-input" value="${profile.name||''}">
            </div>
            <div class="form-group">
              <label for="prof-email">Email</label>
              <input type="email" id="prof-email" class="form-input" value="${profile.email||''}">
            </div>
            <div class="form-group">
              <label for="prof-phone">Phone</label>
              <input id="prof-phone" class="form-input" value="${profile.phone||''}">
            </div>
            <div class="form-group">
              <label for="prof-location">Location</label>
              <input id="prof-location" class="form-input" value="${profile.location||''}">
            </div>
            <div class="form-group">
              <label for="prof-dept">Department</label>
              <input id="prof-dept" class="form-input" value="${profile.department||''}">
            </div>
            <div class="form-group">
              <label for="prof-position">Position</label>
              <input id="prof-position" class="form-input" value="${profile.position||''}">
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn-outline" id="ep-cancel">Cancel</button>
          <button class="btn-primary" id="ep-save">Save</button>
        </div>
      </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', html);
    const modal = document.getElementById('edit-profile-modal');
    modal.querySelector('.modal-close').addEventListener('click', ()=> this.close());
    modal.addEventListener('click', (e)=>{ if (e.target===modal) this.close(); });
    modal.querySelector('#ep-cancel').addEventListener('click', (e)=>{ e.preventDefault(); this.close(); });
    modal.querySelector('#ep-save').addEventListener('click', (e)=>{ e.preventDefault(); this.submit(); });
  }
  async submit() {
    const payload = {
      name: document.getElementById('prof-name').value,
      email: document.getElementById('prof-email').value,
      phone: document.getElementById('prof-phone').value,
      location: document.getElementById('prof-location').value,
      department: document.getElementById('prof-dept').value,
      position: document.getElementById('prof-position').value,
    };
    try {
      const res = await fetch('/api/employee/profile/update', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      const ok = res.ok;
      if (!ok) throw new Error('Failed');
      if (window.managerDashboard && window.managerDashboard.showNotification) {
        window.managerDashboard.showNotification('Profile updated successfully','success');
      } else if (window.showToast) {
        showToast('Profile updated','success');
      } else {
        alert('SUCCESS: Profile updated');
      }
      this.close();
      // Refresh data so profile view reflects updates
      if (window.managerDashboard && typeof window.managerDashboard.refreshData === 'function') {
        window.managerDashboard.refreshData();
      }
      // Navigate to /manager/profile to ensure server-rendered values update
      if (window.location.pathname !== '/manager/profile') {
        window.location.href = '/manager/profile';
      } else {
        window.location.reload();
      }
    } catch(e) {
      if (window.managerDashboard && window.managerDashboard.showNotification) {
        window.managerDashboard.showNotification('Failed to update profile','error');
      } else if (window.showToast) {
        showToast('Failed to update profile','error');
      } else {
        alert('ERROR: Failed to update profile');
      }
    }
  }
  close() { const m = document.getElementById('edit-profile-modal'); if (m) m.remove(); }
}

window.openEditProfileDialog = function(profile){ new EditProfileDialog().open(profile||{}); };
