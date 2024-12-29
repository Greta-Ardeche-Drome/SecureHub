import pyotp

# Clé secrète pour l'ensemble de l'entreprise
SECRET_KEY = "4OT7FRJ3A2T3GRDU5L2PYMW3T2T6DYJ5"  # Générer une clé avec pyotp.random_base32()

def generate_totp():
    """
    Génère un code TOTP valable 30 secondes.
    """
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.now()
