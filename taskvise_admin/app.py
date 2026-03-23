import os
import sys
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from taskvise_admin import admin_manager

app = Flask(
    __name__,
    template_folder=os.path.join(APP_DIR, 'templates'),
    static_folder=os.path.join(APP_DIR, 'static'),
)
app.secret_key = os.environ.get('TASKVISE_ADMIN_SECRET', 'taskvise-admin-secret')


def founder_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'platform_admin':
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped


@app.route('/')
def index():
    if session.get('role') == 'platform_admin':
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('role') == 'platform_admin':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        matched_user = admin_manager.authenticate_founder(username, password)
        if matched_user:
            session['user_id'] = matched_user.get('id', 'TVA001')
            session['username'] = matched_user.get('username', admin_manager.FOUNDER_EMAIL)
            session['full_name'] = matched_user.get('full_name', 'TaskVise Founder')
            session['role'] = 'platform_admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid founder credentials')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@founder_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/overview')
@founder_required
def api_overview():
    return jsonify(admin_manager.get_platform_snapshot())


@app.route('/api/companies', methods=['GET', 'POST'])
@founder_required
def api_companies():
    if request.method == 'GET':
        return jsonify({'success': True, 'companies': admin_manager.get_all_companies()})

    data = request.get_json(force=True) or {}
    company = admin_manager.add_company(data)
    return jsonify({'success': True, 'company': company})


@app.route('/api/companies/<company_id>', methods=['PUT', 'DELETE'])
@founder_required
def api_company_detail(company_id):
    if request.method == 'DELETE':
        admin_manager.delete_company(company_id)
        return jsonify({'success': True})

    data = request.get_json(force=True) or {}
    admin_manager.update_company(company_id, data)
    return jsonify({'success': True})


@app.route('/api/settings', methods=['GET', 'POST'])
@founder_required
def api_settings():
    if request.method == 'GET':
        return jsonify({'success': True, 'settings': admin_manager.load_platform_settings()})

    data = request.get_json(force=True) or {}
    saved = admin_manager.save_platform_settings(data)
    return jsonify({'success': True, 'settings': saved})


if __name__ == '__main__':
    port = int(os.environ.get('TASKVISE_ADMIN_PORT', '5051'))
    debug_enabled = os.environ.get('TASKVISE_ADMIN_DEBUG', 'true').strip().lower() in {'1', 'true', 'yes', 'on'}
    use_reloader = os.environ.get('TASKVISE_ADMIN_USE_RELOADER', 'false').strip().lower() in {'1', 'true', 'yes', 'on'}
    app.run(debug=debug_enabled, port=port, use_reloader=use_reloader)
