from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from database import init_db, get_user_by_name, add_test
from werkzeug.security import check_password_hash
from totp_utils import generate_totp
import os

app = Flask(__name__, template_folder='../Frontend/templates')
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
            role = user['role']
            if role == 'admin':
                flash('Connexion réussie en tant qu’administrateur.', 'success')
                return redirect(url_for('admin_page'))
            else:
                flash('Connexion réussie en tant qu’utilisateur.', 'success')
                return redirect(url_for('user_page'))
        else:
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


@app.route('/totp-code')
def get_totp_code():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    totp_code = generate_totp()
    return jsonify({"totp_code": totp_code})

if __name__ == '__main__':
    app.run(debug=True)