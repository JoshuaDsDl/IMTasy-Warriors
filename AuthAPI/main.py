#  $$$$$$\              $$\     $$\       
# $$  __$$\             $$ |    $$ |      
# $$ /  $$ |$$\   $$\ $$$$$$\   $$$$$$$\  
# $$$$$$$$ |$$ |  $$ |\_$$  _|  $$  __$$\ 
# $$  __$$ |$$ |  $$ |  $$ |    $$ |  $$ |
# $$ |  $$ |$$ |  $$ |  $$ |$$\ $$ |  $$ |
# $$ |  $$ |\$$$$$$  |  \$$$$  |$$ |  $$ |
# \__|  \__| \______/    \____/ \__|  \__|
                                        
import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
import hashlib
import datetime

# Initialisation de Flask
app = Flask(__name__)

# Chargement des variables d'environnement (config)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 27017))
API_PORT = int(os.getenv('API_PORT', 5000))
PLAYER_API_URL = os.getenv('PLAYER_API_URL', 'http://localhost:5001')  # URL de l'API Player

# Connexion à MongoDB
print(f"Connexion à MongoDB sur {DB_HOST}:{DB_PORT}...")
client = MongoClient(f'mongodb://{DB_HOST}:{DB_PORT}/')
db = client['auth_db']
users_collection = db['users']
tokens_collection = db['tokens']

# Endpoint pour vérifier le fonctionnement de l'API (public)
@app.route('/health', methods=['GET'])
def health_check():
    """
    Vérifie que l'API fonctionne correctement.
    """
    return jsonify({"message": "L'API fonctionne correctement !"}), 200

# Endpoint pour générer un token unique
def generate_token(username):
    """
    Le token est basé sur le nom d'utilisateur, la date et l'heure actuelles.
    """
    now = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    token_str = f"{username}-{now}"
    token = hashlib.sha256(token_str.encode()).hexdigest()
    return token

# Endpoint pour enregistrer un nouvel utilisateur
@app.route('/register', methods=['POST'])
def register():
    """
    Enregistre un nouvel utilisateur.
    Arguments :
      - identifiant : le nom d'utilisateur
      - password : le mot de passe
    """
    print("Requête reçue pour enregistrer un utilisateur.")
    data = request.json
    username = data.get('identifiant')
    password = data.get('password')

    if not username or not password:
        print("Erreur : Identifiant ou mot de passe manquant.")
        return jsonify({"error": "Identifiant et mot de passe requis."}), 400

    try:
        # Utiliser un index unique pour éviter les doublons au niveau de MongoDB
        users_collection.create_index("username", unique=True)
    except Exception as e:
        print(f"Erreur lors de la création de l'index unique : {e}")
        return jsonify({"error": "Erreur interne du système."}), 500

    try:
        # Tenter d'insérer l'utilisateur
        users_collection.insert_one({"username": username, "password": password})
        print(f"Utilisateur {username} enregistré avec succès.")
    except Exception as e:
        # Vérifier si l'erreur provient d'une duplication
        if "duplicate key" in str(e):
            print(f"Erreur : L'utilisateur {username} est déjà enregistré.")
            return jsonify({"error": "Utilisateur déjà enregistré."}), 409
        print(f"Erreur inconnue lors de l'enregistrement : {e}")
        return jsonify({"error": "Erreur interne du système."}), 500

    # Authentifier l'utilisateur pour générer un token
    try:
        token_response = requests.post(
            f"http://localhost:{API_PORT}/login",
            json={"identifiant": username, "password": password}
        )
        if token_response.status_code != 200:
            print(f"Erreur lors de l'authentification de l'utilisateur {username}: {token_response.text}")
            return jsonify({"error": "Utilisateur enregistré, mais échec de l'authentification."}), 500
        token = token_response.json().get("token")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de communication avec AuthAPI pour l'authentification : {e}")
        return jsonify({"error": "Erreur de communication avec AuthAPI."}), 500

    # Création du joueur dans PlayerAPI
    try:
        response = requests.post(
            f"{PLAYER_API_URL}/player",
            json={"username": username},
            headers={"Authorization": token},  # Utiliser le token généré
        )
        if response.status_code != 201:
            print(f"Erreur lors de la création du joueur dans PlayerAPI : {response.text}")
            return jsonify({"error": "Utilisateur enregistré, mais erreur lors de la création du joueur."}), 500
    except requests.exceptions.RequestException as e:
        print(f"Erreur de communication avec PlayerAPI : {e}")
        return jsonify({"error": "Erreur de communication avec PlayerAPI."}), 500

    return jsonify({"message": "Utilisateur enregistré avec succès et joueur créé.", "token": token}), 201

# Endpoint pour générer un token
@app.route('/login', methods=['POST'])
def login():
    """
    Arguments :
      - identifiant : le nom d'utilisateur
      - password : le mot de passe
    """
    print("Requête reçue pour authentifier un utilisateur.")
    data = request.json
    username = data.get('identifiant')
    password = data.get('password')

    if not username or not password:
        print("Erreur : Identifiant ou mot de passe manquant.")
        return jsonify({"error": "Identifiant et mot de passe requis."}), 400

    user = users_collection.find_one({"username": username})
    if not user or user['password'] != password:
        print(f"Erreur : Authentification échouée pour l'utilisateur {username}.")
        return jsonify({"error": "Identifiants incorrects."}), 401

    # Génération du token
    token = generate_token(username)
    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)

    # Stockage du token et de sa date d'expiration
    tokens_collection.insert_one({
        "token": token,
        "username": username,
        "expires_at": expiration_time
    })
    print(f"Token généré pour l'utilisateur {username}.")
    return jsonify({"token": token}), 200

# Endpoint pour valider un token
@app.route('/validate', methods=['POST'])
def validate_token():
    """
    Argument :
      - token : le token à valider
    """
    print("Requête reçue pour valider un token.")
    data = request.json
    token = data.get('token')

    if not token:
        print("Erreur : Aucun token fourni.")
        return jsonify({"error": "Token requis."}), 400

    token_data = tokens_collection.find_one({"token": token})

    if not token_data:
        print("Erreur : Token invalide.")
        return jsonify({"error": "Token invalide."}), 401

    if datetime.datetime.now() > token_data["expires_at"]:
        print("Erreur : Token expiré.")
        return jsonify({"error": "Token expiré."}), 401

    # Mise à jour de la date d'expiration
    new_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
    tokens_collection.update_one({"token": token}, {"$set": {"expires_at": new_expiration}})
    print(f"Token validé pour l'utilisateur {token_data['username']}.")
    return jsonify({"username": token_data["username"]}), 200

# Point d'entrée
if __name__ == '__main__':
    # Lancement de Flask
    print(f"Démarrage de l'API sur le port {API_PORT}...")
    app.run(host='0.0.0.0', port=API_PORT, debug=False)