from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash

# Créer l'engine pour la base de données SQLite
db = create_engine("sqlite:///app.db", echo=True, future=True)

# Définir la requête SQL pour créer la table
strSQLCreate = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        name VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'user'
    );
"""

strSQLCreateEvents = """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        event TEXT,
        timestamp TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
"""

def init_db():
    # Créer la table 'users' si elle n'existe pas
    with db.connect() as conn:
        conn.execute(text(strSQLCreate))
        conn.execute(text(strSQLCreateEvents))
        conn.commit()

def insert_user(name, password):
    # Ajouter un utilisateur avec un mot de passe haché
    hashed_password = generate_password_hash(password)
    strSQLInsert = """
        INSERT INTO users (name, password) VALUES (:name, :password);
        """
    with db.connect() as conn:
        try:
            conn.execute(text(strSQLInsert), {"name": name, "password": hashed_password})
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'insertion : {e}")

def insert_admin(name, password):
    # Ajouter un utilisateur avec un mot de passe haché
    hashed_password = generate_password_hash(password)
    strSQLInsert = """
        INSERT INTO users (name, password, role) VALUES (:name, :password, :role);
        """
    with db.connect() as conn:
        try:
            conn.execute(text(strSQLInsert), {"name": name, "password": hashed_password, "role": "admin"})
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'insertion : {e}")

def get_user_by_name(name):
    # Récupérer un utilisateur par son nom
    strSQLSelect = "SELECT * FROM users WHERE name = :name;"
    with db.connect() as conn:
        result = conn.execute(text(strSQLSelect), {"name": name}).fetchone()
        return result

def add_test():
    
    insert_user("Nono", "password63")
    insert_user("Jojo", "password64")
    insert_admin("Loick", "coucou")

    print("Utilisateurs ajoutés avec succès !")

def get_all_users():
    with db.connect() as conn:
        result = conn.execute(text("SELECT * FROM users")).fetchall()
        return [dict(row) for row in result]
    

def add_user(name, password, role):
    hashed_password = generate_password_hash(password)
    with db.connect() as conn:
        conn.execute(
            text("INSERT INTO users (name, password, role) VALUES (:name, :password, :role)"),
            {"name": name, "password": hashed_password, "role": role}
        )
        conn.commit()

def update_user(user_id, name, password, role):
    hashed_password = generate_password_hash(password)
    with db.connect() as conn:
        conn.execute(
            text("UPDATE users SET name = :name, password = :password, role = :role WHERE id = :id"),
            {"name": name, "password": hashed_password, "role": role, "id": user_id}
        )
        conn.commit()

def get_user_by_id(user_id):
    """Récupère un utilisateur spécifique par son ID."""
    with db.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id}).fetchone()
        return dict(result) if result else None

def delete_user(user_id):
    with db.connect() as conn:
        conn.execute(
            text("DELETE FROM users WHERE id = :id"),
            {"id": user_id}
        )
        conn.commit()

def get_all_users_count():
    """Retourne le nombre total d'utilisateurs inscrits."""
    with db.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        return result.scalar()  # Renvoie le nombre d'utilisateurs

def check_system_status():
    """Vérifie l'état du système, comme les erreurs de synchronisation."""
    # Exemple simple : vérifier si la base de données est accessible
    try:
        with db.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "Système opérationnel"
    except Exception as e:
        return f"Erreur : {str(e)}"
    
def get_recent_events():
    """Récupère les derniers événements liés à l'authentification."""
    with db.connect() as conn:
        result = conn.execute(text("SELECT events.event, strftime('%d/%m/%Y | %H:%M:%S', events.timestamp) AS formatted_timestamp, users.name AS user_name FROM events LEFT JOIN users ON events.user_id = users.id ORDER BY events.timestamp DESC LIMIT 20;")).fetchall()
        return [dict(row) for row in result]
    
def log_event(user_id, event):
    """Enregistre un événement dans la base de données."""
    with db.connect() as conn:
        conn.execute(text("INSERT INTO events (user_id, event) VALUES (:user_id, :event)"), 
                     {"user_id": user_id, "event": event})
        conn.commit()