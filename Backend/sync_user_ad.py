from ldap3 import Server, Connection, ALL
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Configuration LDAP
AD_SERVER = '192.168.252.37'
AD_USER = 'ldap@securehub.local'
AD_PASSWORD = 'IutVal2607'
BASE_DN = 'OU=Sites,DC=securehub,DC=local'

def sync_users_from_ad():
    """
    Synchronise les utilisateurs depuis l'Active Directory dans la base de données.
    """
    server = Server(AD_SERVER, get_info=ALL)
    conn = Connection(server, AD_USER, AD_PASSWORD, auto_bind=True)

    # Requête LDAP pour récupérer les utilisateurs
    conn.search(
        search_base=BASE_DN,
        search_filter='(objectClass=user)',
        attributes=['sAMAccountName', 'displayName']
    )

    with db.connect() as conn_db:
        for entry in conn.entries:
            username = entry.sAMAccountName.value
            fullname = entry.displayName.value if entry.displayName else username
            # Vérification si l'utilisateur existe déjà
            existing_user = conn_db.execute(text("SELECT * FROM users WHERE name = :username"), {"username": username}).fetchone()

            if existing_user:
                continue  # Passer l'utilisateur s'il est déjà dans la base

            # Générer le mot de passe par défaut
            hashed_password = generate_password_hash("SecHub")

            # Insérer l'utilisateur dans la base
            conn_db.execute(
                text("""
                    INSERT INTO users (name, fullname, password, is_password_changed) 
                    VALUES (:username, :fullname, :password, 0)  -- Le mot de passe n'a pas été changé
                """),
                {"username": username, "fullname": fullname, "password": hashed_password}
            )
        conn_db.commit()
    
    print("Synchronisation terminée avec succès.")