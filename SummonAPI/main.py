#  $$$$$$\                                                            
# $$  __$$\                                                           
# $$ /  \__|$$\   $$\ $$$$$$\$$$$\  $$$$$$\$$$$\   $$$$$$\  $$$$$$$\  
# \$$$$$$\  $$ |  $$ |$$  _$$  _$$\ $$  _$$  _$$\ $$  __$$\ $$  __$$\ 
#  \____$$\ $$ |  $$ |$$ / $$ / $$ |$$ / $$ / $$ |$$ /  $$ |$$ |  $$ |
# $$\   $$ |$$ |  $$ |$$ | $$ | $$ |$$ | $$ | $$ |$$ |  $$ |$$ |  $$ |
# \$$$$$$  |\$$$$$$  |$$ | $$ | $$ |$$ | $$ | $$ |\$$$$$$  |$$ |  $$ |
#  \______/  \______/ \__| \__| \__|\__| \__| \__| \______/ \__|  \__|

import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import random
import json

# Initialisation de Flask
app = Flask(__name__)

# Configuration via variables d'environnement
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 27017))
API_PORT = int(os.getenv('API_PORT', 5003))
MONSTERS_API_URL = os.getenv('MONSTERS_API_URL', 'http://localhost:5002')
AUTH_API_URL = os.getenv('AUTH_API_URL', 'http://localhost:5000')
PLAYER_API_URL = os.getenv('PLAYER_API_URL', 'http://localhost:5001')  # URL de l'API Player
API_KEY = os.getenv('API_KEY', 'CLE_API_TRES_SAFE')

# Connexion à MongoDB
print(f"Connexion à MongoDB sur {DB_HOST}:{DB_PORT}...")
client = MongoClient(f'mongodb://{DB_HOST}:{DB_PORT}/')
db = client['summon_db']
failed_invocations = db['failed_invocations']  # Base tampon pour les invocations échouées

# Chargement des monstres de base depuis un fichier JSON
monsters_data = []
data_file_path = os.path.join(os.path.dirname(__file__), "data.json")
if os.path.exists(data_file_path):
    with open(data_file_path, "r") as file:
        try:
            monsters_data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Erreur lors du chargement de data.json : {e}")
else:
    print("Erreur : Fichier data.json introuvable.")

# Fonction pour valider un token via AuthAPI
def validate_token(token):
    try:
        response = requests.post(f"{AUTH_API_URL}/validate", json={"token": token})
        if response.status_code == 200:
            return response.json().get("username")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la validation du token : {e}")
        return None

# Middleware pour valider le token
@app.before_request
def verify_token():
    if request.endpoint not in ['health_check']:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token manquant."}), 401
        username = validate_token(token)
        if not username:
            return jsonify({"error": "Token invalide ou expiré."}), 401
        request.username = username

# Endpoint pour vérifier le fonctionnement de l'API
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"message": "L'API fonctionne correctement !"}), 200

# Endpoint pour invoquer un monstre
@app.route('/summon', methods=['POST'])
def summon_monster():
    username = request.username
    print(f"{username} tente d'invoquer un monstre...")

    if not monsters_data:
        return jsonify({"error": "Aucun monstre disponible pour l'invocation."}), 500

    # Algorithme d'invocation basé sur lootRate
    total_loot_rate = sum(monster["lootRate"] for monster in monsters_data)
    random_pick = random.uniform(0, total_loot_rate)
    cumulative_rate = 0

    selected_monster = None
    for monster in monsters_data:
        cumulative_rate += monster["lootRate"]
        if random_pick <= cumulative_rate:
            selected_monster = monster
            break

    if not selected_monster:
        return jsonify({"error": "Erreur lors de la sélection du monstre."}), 500

    # Création du monstre dans MonstersAPI
    try:
        response = requests.post(
            f"{MONSTERS_API_URL}/monsters",
            headers={"X-API-Key": API_KEY},
            json={
                "monster_type": selected_monster["element"],
                "element": selected_monster["element"],
                "hp": selected_monster["hp"],
                "atk": selected_monster["atk"],
                "def": selected_monster["def"],
                "vit": selected_monster["vit"],
                "skills": selected_monster["skills"],
                "owner": username,
            },
        )
        if response.status_code == 201:
            monster_id = response.json()["id"]
            print(f"Monstre invoqué avec succès : {monster_id}")
            
            # Ajout du monstre à PlayerAPI
            try:
                player_response = requests.post(
                    f"{PLAYER_API_URL}/player/monsters",
                    headers={"Authorization": request.headers.get("Authorization")},
                    json={"monster_id": monster_id},
                )
                if player_response.status_code != 201:
                    raise Exception(f"Erreur PlayerAPI : {player_response.text}")
            except Exception as e:
                print(f"Erreur lors de l'ajout du monstre dans PlayerAPI : {e}")
                return jsonify({"error": "Erreur lors de l'ajout dans l'inventaire."}), 500

            return jsonify({"message": "Invocation réussie.", "monster_id": monster_id}), 201
        else:
            raise Exception(f"Erreur MonstersAPI : {response.text}")
    except Exception as e:
        print(f"Invocation échouée : {e}")
        return jsonify({"error": "Erreur lors de l'invocation. Réessayez plus tard."}), 500

# Endpoint pour rejouer les invocations échouées
@app.route('/replay', methods=['POST'])
def replay_invocations():
    invocations = list(failed_invocations.find())
    for invocation in invocations:
        username = invocation["username"]
        monster = invocation["monster"]
        print(f"Rejeu pour {username} : {monster}")

        try:
            response = requests.post(
                f"{MONSTERS_API_URL}/monsters",
                headers={"X-API-Key": API_KEY},
                json={
                    "monster_type": monster["element"],  # Utiliser "element" comme "monster_type"
                    "element": monster["element"],
                    "hp": monster["hp"],
                    "atk": monster["atk"],
                    "def": monster["def"],
                    "vit": monster["vit"],
                    "skills": monster["skills"],
                },
            )
            if response.status_code == 201:
                failed_invocations.delete_one({"_id": invocation["_id"]})
        except Exception as e:
            print(f"Erreur lors du rejeu : {e}")

    return jsonify({"message": "Rejeu terminé."}), 200

# Point d'entrée
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT, debug=True)
