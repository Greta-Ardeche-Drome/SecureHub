// Fonction pour actualiser le code TOTP toutes les 30 secondes
async function fetchTOTP() {
    const response = await fetch('/totp-code');
    const data = await response.json();
    document.getElementById('totp-code').innerText = data.totp_code;
}

// Actualisation automatique
document.addEventListener('DOMContentLoaded', () => {
    fetchTOTP();
    setInterval(fetchTOTP, 30000); // Mise à jour toutes les 30 secondes
});