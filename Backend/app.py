from flask import Flask, render_template, send_file, redirect, url_for, request, session, flash, jsonify
from database import init_db, get_user_by_name, add_default_admin, get_all_users, add_user, update_user, get_user_by_id, delete_user, get_all_users_count, check_system_status, get_recent_events, log_event, db
from sync_user_ad import initialize_users_from_ad, update_users_from_ad
from werkzeug.security import generate_password_hash, check_password_hash
from totp_utils import generate_totp, generate_qr_code
from datetime import datetime
from sqlalchemy import text
import os
import threading
import time

app = Flask(__name__, template_folder='../Frontend/templates', static_folder='../Frontend/static')
app.secret_key = 'your_secret_key'
# Initialisation de la base de données
if not os.path.exists('app.db'):
    init_db()
    add_default_admin()
    initialize_users_from_ad()

def sync_ad_users_periodically():
    """Fonction qui interroge l'AD toutes les 3 minutes pour synchroniser les utilisateurs."""
    while True:
        time.sleep(180) # Attend 3 minutes (180 secondes)
        update_users_from_ad()  # Appelle la fonction pour mettre à jour les utilisateurs
                

#Démarre le thread de synchronisation des utilisateurs AD
threading.Thread(target=sync_ad_users_periodically, daemon=True).start()

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
            session['fullname'] = user['fullname']
            session['role'] = user['role']
            log_event(user['id'], "Authentification réussie")

            if user["is_password_changed"] == 0:
                return redirect(url_for('change_password'))
            else:
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

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:  # Vérifie si l'utilisateur est connecté
        flash("Vous devez être connecté pour changer votre mot de passe.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']  # Récupération de l'ID de l'utilisateur connecté

    if request.method == 'POST':
        new_password = request.form['new_password']
        
        # Hacher le nouveau mot de passe
        hashed_password = generate_password_hash(new_password)

        with db.connect() as conn:
            # Mise à jour du mot de passe pour CE SEUL utilisateur
            conn.execute(
                text("""
                    UPDATE users 
                    SET password = :password, is_password_changed = 1 
                    WHERE id = :user_id
                """),
                {"password": hashed_password, "user_id": user_id}
            )
            conn.commit()

        flash("Votre mot de passe a été mis à jour avec succès !")
        if session['role'] == 'admin':
            return redirect(url_for('admin_page'))  # Rediriger vers la page utilisateur après le changement
        else:
            return redirect(url_for('user_page'))

    return render_template('change_password.html')

@app.route('/user')
def user_page():
    if 'user_id' not in session or session.get('role') != 'user':
        flash('Accès interdit.', 'error')
        return redirect(url_for('login'))

    totp_code = generate_totp()
    return render_template('user_page.html', username=session['fullname'], totp_code=totp_code)

@app.route('/admin')
def admin_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Accès interdit.', 'error')
        return redirect(url_for('login'))

    # Générer le code TOTP
    totp_code = generate_totp()
    return render_template('admin_page.html', username=session['fullname'], totp_code=totp_code)

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
