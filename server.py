from flask import Flask, request, redirect, jsonify, render_template_string
from datetime import datetime
import os, platform, socket, getpass, sys, time, requests

app = Flask(__name__)
ps_start = time.time()

# ===== CONFIG =====
CLIENT_ID = "1407754949722509394
CLIENT_SECRET = "MBNletlsEiSlSiuw60egwiniDgAkXH6J
REDIRECT_URI = "santoworkspace.netlify.app"  # cambiar a tu URL cuando publiques
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1461954556165357610/_udtV75K9kr-zkFdP8-UYKiG4mmf2OovuXdu4mQQNstzBEIiI4aCvwpsthLjsJDoSpYK
# ==================

DISCORD_AUTH = (
    "https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    "&response_type=code"
    "&scope=identify"
    f"&redirect_uri={REDIRECT_URI}"
)

@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Panel</title>
</head>
<body>
<h2>🔐 Acceso Seguro</h2>
<p>Continúa con Discord para enviar tu info</p>
<button onclick="location.href='/login'">Continuar con Discord</button>
</body>
</html>
""")

@app.route("/login")
def login():
    return redirect(DISCORD_AUTH)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error OAuth"

    # === Intercambia el code por token ===
    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()

    access_token = token_res.get("access_token")

    # === Obtiene info del usuario ===
    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # === Captura info de PC + navegador ===
    guardar_todo(user)

    return "<h2>✅ Datos enviados correctamente</h2>"

def guardar_todo(user):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_local = "No disponible"  # La IP real desde navegador requiere JS
    hostname = socket.gethostname()
    usuario = getpass.getuser()
    sistema = platform.system() + " " + platform.release()
    sistema_completo = platform.platform()
    arquitectura = platform.architecture()[0]
    maquina = platform.machine()
    procesador = platform.processor()
    cpu_count = os.cpu_count()
    python_version = sys.version.split()[0]
    cwd = os.getcwd()
    pid = os.getpid()
    uptime = int(time.time() - ps_start)
    zona_horaria_sistema = time.tzname

    try:
        ip_publica = requests.get("https://api.ipify.org", timeout=5).text
    except:
        ip_publica = "No disponible"

    texto = (
        f"🕒 Hora: {hora}\n"
        f"🖥️ Hostname: {hostname}\n"
        f"👤 Usuario: {usuario}\n"
        f"💻 Sistema: {sistema}\n"
        f"📦 Sistema completo: {sistema_completo}\n"
        f"🧱 Arquitectura: {arquitectura}\n"
        f"🏗️ Máquina: {maquina}\n"
        f"⚙️ Procesador: {procesador}\n"
        f"🧠 CPUs: {cpu_count}\n"
        f"🐍 Python: {python_version}\n"
        f"📂 Directorio App: {cwd}\n"
        f"🆔 PID: {pid}\n"
        f"🕰️ Zona Horaria Sistema: {zona_horaria_sistema}\n"
        f"⏱️ Uptime (s): {uptime}\n\n"
        f"🌐 IP Local: {ip_local}\n"
        f"🌍 IP Pública: {ip_publica}\n"
        "-----------------------------\n"
        f"🎮 Discord User: {user.get('username')}#{user.get('discriminator')}\n"
        f"🆔 Discord ID: {user.get('id')}\n"
        f"🌍 Locale: {user.get('locale')}\n"
    )

    # Guarda en TXT
    with open("datos.txt", "a", encoding="utf-8") as f:
        f.write(texto)

    # Envía a webhook
    requests.post(WEBHOOK_URL, json={
        "content": "📡 **Nuevo acceso detectado**",
        "embeds": [{"description": f"```{texto}```", "color": 5793266}]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
