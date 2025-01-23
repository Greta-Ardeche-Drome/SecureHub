from ldap3 import Server, Connection, ALL
from models import db, User
from app import app

# Configuration LDAP
AD_SERVER = 'ldap://ad.entreprise.com'
AD_USER = 'admin@entreprise.com'
AD_PASSWORD = 'password'
BASE_DN = 'OU=Utilisateurs,DC=entreprise,DC=com'

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
        attributes=['sAMAccountName', 'mail', 'displayName']
    )

    with app.app_context():
        for entry in conn.entries:
            username = entry.sAMAccountName.value
            email = entry.mail.value
            display_name = entry.displayName.value

            # Vérifiez si l'utilisateur existe déjà
            if User.query.filter_by(username=username).first():
                continue

            # Ajouter l'utilisateur à la base
            user = User(
                username=username,
                totp_secret='',  # Généré ou attribué plus tard
                recovery_phrase=None,
                is_admin=False  # À personnaliser si nécessaire
            )
            db.session.add(user)
        db.session.commit()
        print("Synchronisation terminée avec succès.")

# Exécutez uniquement si appelé directement
if __name__ == '__main__':
    sync_users_from_ad()
