// Team Member Details Dialog (Team Lead)
let tlMemberDialog = null;

function openTLMemberDetailsDialog(member){
  if(!tlMemberDialog){
    tlMemberDialog = document.createElement('div');
    tlMemberDialog.className = 'dialog-overlay';
    tlMemberDialog.addEventListener('click', (e)=>{ if(e.target===tlMemberDialog) closeTLMemberDetailsDialog(); });
  }
  tlMemberDialog.innerHTML = `
  <div class="dialog">
    <div class="dialog-header">
      <h2 class="dialog-title">${member?.name || 'Team Member'}</h2>
      <p class="dialog-description">${member?.email || ''}</p>
      <button class="dialog-close" onclick="closeTLMemberDetailsDialog()">×</button>
    </div>
    <div class="dialog-content">
      <div class="form-group">
        <label class="form-label">Position</label>
        <div class="form-input" style="border:none; padding:0">${member?.position || '-'}</div>
      </div>
      <div class="form-group">
        <label class="form-label">Department</label>
        <div class="form-input" style="border:none; padding:0">${member?.department || '-'}</div>
      </div>
    </div>
    <div class="dialog-actions">
      <button class="btn btn-outline" onclick="closeTLMemberDetailsDialog()">Close</button>
    </div>
  </div>`;
  document.body.appendChild(tlMemberDialog);
  tlMemberDialog.style.display = 'flex';
}

function closeTLMemberDetailsDialog(){ if(tlMemberDialog){ tlMemberDialog.style.display='none'; } }

window.openTLMemberDetailsDialog = openTLMemberDetailsDialog;
window.closeTLMemberDetailsDialog = closeTLMemberDetailsDialog;
