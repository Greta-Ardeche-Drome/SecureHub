import pyotp
import qrcode
from io import BytesIO

# Clé secrète pour l'ensemble de l'entreprise
SECRET_KEY = "4OT7FRJ3A2T3GRDU5L2PYMW3T2T6DYJ5"  # Générer une clé avec pyotp.random_base32()

def generate_totp():
    """
    Génère un code TOTP valable 30 secondes.
    """
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.now()

def generate_qr_code():
    """
    Génère un QR code pour configurer TOTP sur une application comme Okta.
    """
    # Création de l'URI TOTP compatible avec Google Authenticator et Okta
    totp = pyotp.TOTP(SECRET_KEY)
    otp_uri = totp.provisioning_uri(name="EntrepriseApp:Utilisateur", issuer_name="EntrepriseApp")

    # Génération du QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(otp_uri)
    qr.make(fit=True)

    # Convertir le QR code en image
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf

def response_totp():
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.now()