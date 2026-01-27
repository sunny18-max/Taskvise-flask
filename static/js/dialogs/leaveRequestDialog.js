class LeaveRequestDialog {
    open() {
        const html = `
        <div class="modal-overlay" id="leave-request-modal">
            <div class="modal">
                <div class="modal-header">
                    <h3>Request Leave</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="leave-request-form">
                        <div class="form-group">
                            <label for="leave-start">Start Date *</label>
                            <input type="date" id="leave-start" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label for="leave-end">End Date *</label>
                            <input type="date" id="leave-end" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label for="leave-reason">Reason</label>
                            <textarea id="leave-reason" class="form-input" placeholder="Optional"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn-outline" id="leave-cancel">Cancel</button>
                    <button class="btn-primary" id="leave-submit">Submit Request</button>
                </div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', html);
        this.bind();
    }
    bind() {
        const modal = document.getElementById('leave-request-modal');
        modal.querySelector('.modal-close').addEventListener('click', () => this.close());
        modal.addEventListener('click', (e) => { if (e.target === modal) this.close(); });
        modal.querySelector('#leave-cancel').addEventListener('click', (e)=>{ e.preventDefault(); this.close(); });
        modal.querySelector('#leave-submit').addEventListener('click', (e)=>{ e.preventDefault(); this.submit(); });
    }
    async submit() {
        const start = document.getElementById('leave-start').value;
        const end = document.getElementById('leave-end').value;
        const reason = document.getElementById('leave-reason').value;
        if (!start || !end) { this.toast('Please select start and end dates','error'); return; }
        try {
            const res = await fetch('/api/employee/leave/apply', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_date: start, end_date: end, reason })
            });
            if (!res.ok) throw new Error('Failed');
            this.toast('Leave request submitted','success');
            this.close();
            // Reload leave view if present
            if (window.location.pathname.includes('/employee/leave')) {
                const urlParams = new URLSearchParams(window.location.search);
                const filter = urlParams.get('filter');
                if (window.loadLeaveData) window.loadLeaveData(filter);
            }
        } catch (e) {
            this.toast('Failed to submit leave','error');
        }
    }
    toast(msg, type) {
        if (window.showToast) return window.showToast(msg, type==='success'?'success':'error');
        alert(msg);
    }
    close() { const m = document.getElementById('leave-request-modal'); if (m) m.remove(); }
}

window.openLeaveRequestDialog = function() {
    const dlg = new LeaveRequestDialog();
    dlg.open();
};
