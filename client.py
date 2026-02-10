import requests
import json

# URL del server (modificare quando deployato online)
SERVER_URL = "http://localhost:5000"

def register(username, password):
    """Registra un nuovo utente sul server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            json={"username": username, "password": password},
            timeout=5
        )
        data = response.json()
        print(data['message'])
        return data['success']
    except requests.exceptions.RequestException as e:
        print(f"Errore di connessione al server: {e}")
        return False

def login(username, password):
    """Effettua il login sul server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/login",
            json={"username": username, "password": password},
            timeout=5
        )
        data = response.json()
        print(data['message'])
        return data['success']
    except requests.exceptions.RequestException as e:
        print(f"Errore di connessione al server: {e}")
        return False

def check_server():
    """Verifica se il server è online"""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def main():
    """Menu principale"""
    
    # Controlla se il server è online
    print("Verifica connessione al server...")
    if not check_server():
        print("Errore: Il server non è raggiungibile")
        print("Assicurati che il backend.py sia in esecuzione")
        return
    
    print("Server online\n")
    
    while True:
        print("\n" + "="*40)
        print("SISTEMA DI LOGIN ONLINE")
        print("="*40)
        print("1. Registrazione")
        print("2. Login")
        print("3. Esci")
        print("="*40)
        
        choice = input("Scegli un'opzione (1/2/3): ").strip()
        
        if choice == "1":
            print("\n--- REGISTRAZIONE ---")
            username = input("Username: ").strip()
            password = input("Password: ").strip().replace(" ", "")
            register(username, password)
            
        elif choice == "2":
            print("\n--- LOGIN ---")
            username = input("Username: ").strip()
            password = input("Password: ").strip().replace(" ", "")
            login(username, password)
            
        elif choice == "3":
            print("Arrivederci")
            break
            
        else:
            print("Opzione non valida")

if __name__ == "__main__":
    main()
