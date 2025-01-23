from flask import Flask, render_template, send_file, redirect, url_for, request, session, flash, jsonify
from database import init_db, get_user_by_name, add_test, get_all_users, add_user, update_user, get_user_by_id, delete_user, get_all_users_count, check_system_status, get_recent_events, log_event
from werkzeug.security import check_password_hash
from totp_utils import generate_totp, generate_qr_code
from datetime import datetime
import os

app = Flask(__name__, template_folder='../Frontend/templates', static_folder='../Frontend/static')
app.secret_key = 'your_secret_key'
# Initialisation de la base de données
if not os.path.exists('app.db'):
    init_db()
    add_test()

@app.route('/')
def index():
    # Redirige la page racine vers /login
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérifiez si l'utilisateur existe dans la base de données
        user = get_user_by_name(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['role'] = user['role']
            log_event(user['id'], "Authentification réussie")

            role = user['role']
            if role == 'admin':
                flash('Connexion réussie en tant qu’administrateur.', 'success')
                return redirect(url_for('admin_page'))
            else:
                flash('Connexion réussie en tant qu’utilisateur.', 'success')
                return redirect(url_for('user_page'))
        else:
            if user:
                log_event(user['id'], "Erreur d'authentification")
            else:
                log_event(None, "Tentative d'authentification échouée : utilisateur inconnu")

            flash('Nom d’utilisateur ou mot de passe incorrect', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('login'))

@app.route('/user')
def user_page():
    if 'user_id' not in session or session.get('role') != 'user':
        flash('Accès interdit.', 'error')
        return redirect(url_for('login'))

    totp_code = generate_totp()
    return render_template('user_page.html', username=session['username'], totp_code=totp_code)

@app.route('/admin')
def admin_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Accès interdit.', 'error')
        return redirect(url_for('login'))

    # Générer le code TOTP
    totp_code = generate_totp()
    return render_template('admin_page.html', username=session['username'], totp_code=totp_code)

@app.route('/admin/users', methods=['GET'])
def admin_users():
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès interdit.", 'error')
        return redirect(url_for('login'))

    # Récupérer tous les utilisateurs
    users = get_all_users()
    return render_template('admin_users_table.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user_page():
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès interdit.", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        add_user(name, password, role)
        flash("Utilisateur ajouté avec succès.", 'success')
        return redirect(url_for('admin_users'))

    return render_template('add_user.html')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user_page(user_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès interdit.", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        update_user(user_id, name, password, role)
        flash("Utilisateur modifié avec succès.", 'success')
        return redirect(url_for('admin_users'))

    return render_template('edit_user.html', user=get_user_by_id(user_id))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user_page(user_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès interdit.", 'error')
        return redirect(url_for('login'))

    delete_user(user_id)
    flash("Utilisateur supprimé avec succès.", 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/dashboard')
def dashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès interdit.", 'error')
        return redirect(url_for('login'))

    # Récupérer le nombre d'utilisateurs inscrits
    users_count = get_all_users_count()
    
    # Vérification du statut global du système
    system_status = check_system_status()
    
    # Récupérer les événements récents
    recent_events = get_recent_events()
    return render_template('admin_dashboard.html', users_count=users_count, system_status=system_status, recent_events=recent_events)

@app.route('/totp-code')
def get_totp_code():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    totp_code = generate_totp()
    return jsonify({"totp_code": totp_code})

@app.route('/qr-code')
def qr_code():
    image_qr = generate_qr_code()
    return send_file(image_qr, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
