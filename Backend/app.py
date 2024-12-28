from flask import Flask, render_template, redirect, url_for, request, session, flash
from database import init_db, get_user_by_name, add_user_test
from werkzeug.security import check_password_hash

app = Flask(__name__, template_folder='../Frontend/templates')
app.secret_key = 'your_secret_key'
# Initialisation de la base de données
init_db()
add_user_test()

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
            return redirect(url_for('user_dashboard'))  # Redirige vers le tableau de bord utilisateur
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'error')
        return redirect(url_for('login'))

    return f"Bienvenue {session['username']} ! Ceci est votre tableau de bord."

if __name__ == '__main__':
    app.run(debug=True)