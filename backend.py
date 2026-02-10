from flask import Flask, request, jsonify
import json
import os
from hashlib import sha256
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# File onde salvare gli utenti (in produzione usare database vero)
DATABASE_FILE = "users_database.json"
RESPONSES_FILE = "risposte_centralizzate.json"
RESPONSES_TXT = "risposte_centralizzate.txt"
SUPERVISOR_PASSWORD = "Supervisore123!"

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

def load_responses():
    """Carica tutte le risposte"""
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_responses(responses):
    """Salva tutte le risposte"""
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=4, ensure_ascii=False)

def salva_response_txt(responses):
    """Salva tutte le risposte in un file txt centralizzato"""
    with open(RESPONSES_TXT, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("RISPOSTE AL QUESTIONARIO - REPORT SUPERVISORE\n")
        f.write("="*70 + "\n\n")
        
        for resp in responses:
            f.write("-"*70 + "\n")
            f.write(f"Username: {resp['username']}\n")
            f.write(f"Nome e Cognome: {resp.get('nome_cognome', 'N/A')}\n")
            f.write("-"*70 + "\n")
            
            for item in resp.get('domande', []):
                f.write(f"Domanda: {item['domanda']}\n")
                f.write(f"Risposta: {item['risposta']}\n\n")
            
            f.write("\n")
        
        f.write("="*70 + "\n")

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

@app.route('/save_responses', methods=['POST'])
def save_responses_endpoint():
    """Endpoint per salvare le risposte del questionario"""
    data = request.get_json()
    username = data.get('username', '').strip()
    risposte = data.get('risposte', {})
    
    if not username or not risposte:
        return jsonify({'success': False, 'message': 'Dati incompleti'}), 400
    
    # Carica risposte esistenti
    all_responses = load_responses()
    
    # Controlla se l'utente ha già inviato
    for resp in all_responses:
        if resp['username'] == username:
            return jsonify({'success': False, 'message': 'Hai già inviato il questionario'}), 400
    
    # Aggiungi la nuova risposta
    nome_cognome = risposte.get('domande', [])[0].get('risposta', 'Sconosciuto') if risposte.get('domande') else 'Sconosciuto'
    new_response = {
        'username': username,
        'nome_cognome': nome_cognome,
        'domande': risposte.get('domande', [])
    }
    
    all_responses.append(new_response)
    
    # Salva in JSON
    save_responses(all_responses)
    
    # Salva in TXT
    salva_response_txt(all_responses)
    
    return jsonify({'success': True, 'message': 'Risposte salvate con successo'}), 201

@app.route('/get_all_responses', methods=['GET'])
def get_all_responses():
    """Endpoint per recuperare tutte le risposte (supervisore)"""
    # In produzione, aggiungere autenticazione per il supervisore
    all_responses = load_responses()
    return jsonify({'success': True, 'responses': all_responses}), 200

@app.route('/check_response/<username>', methods=['GET'])
def check_response(username):
    """Endpoint per controllare se un utente ha già inviato"""
    all_responses = load_responses()
    
    for resp in all_responses:
        if resp['username'] == username:
            return jsonify({'success': True, 'submitted': True}), 200
    
    return jsonify({'success': True, 'submitted': False}), 200

@app.route('/verify_supervisor', methods=['POST'])
def verify_supervisor():
    """Endpoint per verificare la password supervisore"""
    data = request.get_json()
    password = data.get('password', '')
    
    if password == SUPERVISOR_PASSWORD:
        all_responses = load_responses()
        return jsonify({'success': True, 'responses': all_responses}), 200
    else:
        return jsonify({'success': False, 'message': 'Password supervisore errata'}), 401

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=PORT)


