from flask import Flask, request, jsonify
import json
import os
from hashlib import sha256
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# File onde salvare gli utenti (in produzione usare database vero)
DATABASE_FILE = "users_database.json"

# Ottiene la porta da variabili d'ambiente (per Render)
PORT = int(os.environ.get('PORT', 5000))

def load_users():
    """Carica gli utenti dal file"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    """Salva gli utenti nel file"""
    with open(DATABASE_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Cripta la password"""
    return sha256(password.encode()).hexdigest()

def validate_password(password):
    """Valida la password secondo i criteri di sicurezza"""
    if len(password) < 8:
        return False, "La password deve avere almeno 8 caratteri"
    
    if not any(c.isupper() for c in password):
        return False, "La password deve contenere almeno una lettera MAIUSCOLA"
    
    if not any(c.islower() for c in password):
        return False, "La password deve contenere almeno una lettera minuscola"
    
    if not any(c.isdigit() for c in password):
        return False, "La password deve contenere almeno un numero"
    
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        return False, "La password deve contenere almeno un carattere speciale"
    
    return True, "Password valida"

@app.route('/register', methods=['POST'])
def register():
    """Endpoint per la registrazione"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip().replace(" ", "")
    
    users = load_users()
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username e password sono obbligatori'}), 400
    
    if username in users:
        return jsonify({'success': False, 'message': 'Questo username è già registrato'}), 400
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'success': False, 'message': message}), 400
    
    users[username] = hash_password(password)
    save_users(users)
    
    return jsonify({'success': True, 'message': f'Utente {username} registrato con successo'}), 201

@app.route('/login', methods=['POST'])
def login():
    """Endpoint per il login"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip().replace(" ", "")
    
    users = load_users()
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username e password sono obbligatori'}), 400
    
    if username not in users:
        return jsonify({'success': False, 'message': 'Username non trovato'}), 401
    
    if users[username] == hash_password(password):
        return jsonify({'success': True, 'message': f'Benvenuto {username}'}), 200
    else:
        return jsonify({'success': False, 'message': 'Password sbagliata'}), 401

@app.route('/health', methods=['GET'])
def health():
    """Endpoint per verificare se il server è online"""
    return jsonify({'status': 'online'}), 200

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=PORT)
