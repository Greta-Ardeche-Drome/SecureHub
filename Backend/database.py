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

def init_db():
    # Créer la table 'users' si elle n'existe pas
    with db.connect() as conn:
        conn.execute(text(strSQLCreate))
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