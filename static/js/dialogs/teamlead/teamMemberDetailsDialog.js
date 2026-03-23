let tlMemberDialog = null;
let tlMemberEscHandlerBound = false;

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function openTLMemberDetailsDialog(member) {
  if (!tlMemberDialog) {
    tlMemberDialog = document.createElement('div');
    tlMemberDialog.className = 'modal-overlay';
    tlMemberDialog.style.display = 'none';
    tlMemberDialog.addEventListener('click', (e) => {
      if (e.target === tlMemberDialog) closeTLMemberDetailsDialog();
    });
  }

  tlMemberDialog.innerHTML = `
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="tl-member-title">
    <div class="modal-header">
      <div>
        <h3 id="tl-member-title">${escapeHtml(member?.name || 'Team Member')}</h3>
        <p class="modal-subtitle">${escapeHtml(member?.email || '')}</p>
      </div>
      <button class="modal-close" type="button" aria-label="Close" onclick="closeTLMemberDetailsDialog()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label class="form-label">Position</label>
        <div class="form-static-value">${escapeHtml(member?.position || '-')}</div>
      </div>
      <div class="form-group" style="margin-bottom:0;">
        <label class="form-label">Department</label>
        <div class="form-static-value">${escapeHtml(member?.department || '-')}</div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" type="button" onclick="closeTLMemberDetailsDialog()">Close</button>
    </div>
  </div>`;

  if (!document.body.contains(tlMemberDialog)) {
    document.body.appendChild(tlMemberDialog);
  }
  tlMemberDialog.style.display = 'flex';

  if (!tlMemberEscHandlerBound) {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && tlMemberDialog && tlMemberDialog.style.display === 'flex') {
        closeTLMemberDetailsDialog();
      }
    });
    tlMemberEscHandlerBound = true;
  }
}

function closeTLMemberDetailsDialog() {
  if (tlMemberDialog) {
    tlMemberDialog.style.display = 'none';
  }
}

window.openTLMemberDetailsDialog = openTLMemberDetailsDialog;
window.closeTLMemberDetailsDialog = closeTLMemberDetailsDialog;
