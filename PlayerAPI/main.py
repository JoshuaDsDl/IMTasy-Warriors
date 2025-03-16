# $$$$$$$\  $$\                                         
# $$  __$$\ $$ |                                        
# $$ |  $$ |$$ | $$$$$$\  $$\   $$\  $$$$$$\   $$$$$$\  
# $$$$$$$  |$$ | \____$$\ $$ |  $$ |$$  __$$\ $$  __$$\ 
# $$  ____/ $$ | $$$$$$$ |$$ |  $$ |$$$$$$$$ |$$ |  \__|
# $$ |      $$ |$$  __$$ |$$ |  $$ |$$   ____|$$ |      
# $$ |      $$ |\$$$$$$$ |\$$$$$$$ |\$$$$$$$\ $$ |      
# \__|      \__| \_______| \____$$ | \_______|\__|      
#                         $$\   $$ |                    
#                         \$$$$$$  |                    
#                          \______/                     

import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
import math

# Initialisation de l'application Flask
app = Flask(__name__)

# Chargement des variables d'environnement pour la configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 27017))
API_PORT = int(os.getenv('API_PORT', 5001))
AUTH_API_URL = os.getenv('AUTH_API_URL', 'http://localhost:5000')  # URL de l'API Auth
MONSTERS_API_URL = os.getenv('MONSTERS_API_URL', 'http://localhost:5002')  # URL de l'API Monsters

# Connexion à la base de données MongoDB
print(f"Connexion à MongoDB sur {DB_HOST}:{DB_PORT}...")
client = MongoClient(f'mongodb://{DB_HOST}:{DB_PORT}/')
db = client['player_db']
players_collection = db['players']

# Fonction pour valider le token en appelant l'API Auth
def validate_token(token):
    """
    Valide le token en appelant l'API Auth.
    Retourne le nom d'utilisateur si le token est valide, sinon une erreur.
    """
    print("Validation du token auprès de l'API Auth...")
    try:
        response = requests.post(f"{AUTH_API_URL}/validate", json={"token": token})
        if response.status_code == 200:
            return response.json().get("username")
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la validation du token : {e}")
        return None

# Middleware pour vérifier le token
@app.before_request
def check_authentication():
    """
    Vérifie le token avant chaque requête.
    """
    if request.endpoint != 'health_check':  # Exclure les endpoints publics
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token manquant dans les headers."}), 401

        username = validate_token(token)
        if not username:
            return jsonify({"error": "Token invalide ou expiré."}), 401

        # Ajouter le nom d'utilisateur à la requête pour l'utiliser dans les endpoints
        request.username = username

# Endpoint pour vérifier le fonctionnement de l'API (public)
@app.route('/health', methods=['GET'])
def health_check():
    """
    Vérifie que l'API fonctionne correctement.
    """
    return jsonify({"message": "L'API fonctionne correctement !"}), 200

# Endpoint pour créer le joueur
@app.route('/player', methods=['POST'])
def create_player():
    """
    Crée un nouveau joueur.
    """
    username = request.username  # Récupération du nom d'utilisateur depuis le middleware
    print(f"Requête reçue pour créer un joueur pour {username}.")

    # Vérifie si le joueur existe déjà
    if players_collection.find_one({"username": username}):
        print(f"Erreur : Le joueur {username} existe déjà.")
        return jsonify({"error": "Joueur déjà existant."}), 409

    # Crée le joueur avec les données initiales
    player = {
        "username": username,
        "level": 1,  # Niveau initial à 1 au lieu de 0
        "experience": 0,  # Expérience initiale à 0
        "monsters": [],  # Liste vide de monstres
        "max_monsters": 11  # Capacité initiale des monstres (10 + niveau 1)
    }
    result = players_collection.insert_one(player)

    # Ajoute l'ID du joueur sous forme de chaîne pour éviter les problèmes de sérialisation
    player["_id"] = str(result.inserted_id)
    
    print(f"Joueur {username} créé avec succès.")
    return jsonify({"message": "Joueur créé avec succès.", "player": player}), 201

# Endpoint pour récupérer les informations complètes du joueur
@app.route('/player', methods=['GET'])
def get_player():
    """
    Récupère les informations complètes du joueur connecté.
    """
    username = request.username
    print(f"Requête reçue pour récupérer les informations du joueur {username}.")
    player = players_collection.find_one({"username": username})
    if not player:
        print(f"Erreur : Joueur {username} introuvable.")
        return jsonify({"error": "Joueur introuvable."}), 404

    player["_id"] = str(player["_id"])  # Convertir ObjectId en string pour JSON
    return jsonify(player), 200

# Endpoint pour ajouter de l'expérience au joueur
@app.route('/player/experience', methods=['PUT'])
def add_experience():
    """
    Ajoute de l'expérience au joueur connecté.
    """
    username = request.username
    print(f"Requête reçue pour ajouter de l'expérience au joueur {username}.")
    data = request.json
    experience_gain = data.get('experience')

    if not experience_gain or experience_gain < 0:
        print("Erreur : Gain d'expérience invalide.")
        return jsonify({"error": "Un gain d'expérience positif est requis."}), 400

    player = players_collection.find_one({"username": username})
    if not player:
        print(f"Erreur : Joueur {username} introuvable.")
        return jsonify({"error": "Joueur introuvable."}), 404

    player["experience"] += experience_gain

    # Vérifier si le joueur peut monter de niveau
    level_up_threshold = 50 * math.pow(1.1, player["level"])
    if player["experience"] >= level_up_threshold:
        player["level"] += 1
        player["experience"] = 0  # Réinitialiser l'expérience
        player["max_monsters"] = 10 + player["level"]  # Mise à jour de la limite des monstres

    players_collection.update_one({"username": username}, {"$set": player})

    # Convertir l'ObjectId en string pour éviter l'erreur de sérialisation
    player["_id"] = str(player["_id"])
    print(f"Expérience mise à jour pour le joueur {username}. Nouvelle expérience : {player['experience']}. Niveau : {player['level']}")
    return jsonify({"message": "Expérience mise à jour.", "player": player}), 200

# Endpoint pour gérer l'acquisition d'un monstre
@app.route('/player/monsters', methods=['POST'])
def add_monster():
    """
    Ajoute un monstre à la liste du joueur connecté après vérification.
    """
    username = request.username
    print(f"Requête reçue pour ajouter un monstre au joueur {username}.")
    data = request.json
    monster_id = data.get('monster_id')

    if not monster_id:
        print("Erreur : ID du monstre requis.")
        return jsonify({"error": "Un ID de monstre est requis."}), 400

    # Vérification auprès de MonstersAPI
    try:
        response = requests.get(
            f"{MONSTERS_API_URL}/monsters/{monster_id}",
            headers={"Authorization": request.headers.get("Authorization")}
        )
        if response.status_code != 200:
            print(f"Erreur : Monstre {monster_id} introuvable ou problème lors de la requête : {response.text}")
            return jsonify({"error": "Monstre introuvable ou problème de vérification."}), 400

        monster_data = response.json()
        if "owner" in monster_data and monster_data["owner"] != username:
            print(f"Erreur : Monstre {monster_id} appartient déjà à un autre joueur.")
            return jsonify({"error": "Ce monstre appartient déjà à un autre joueur."}), 400
    except requests.exceptions.RequestException as e:
        print(f"Erreur de communication avec MonstersAPI : {e}")
        return jsonify({"error": "Erreur de communication avec MonstersAPI."}), 500

    # Récupération du joueur
    player = players_collection.find_one({"username": username})
    if not player:
        print(f"Erreur : Joueur {username} introuvable.")
        return jsonify({"error": "Joueur introuvable."}), 404

    if len(player["monsters"]) >= player["max_monsters"]:
        print("Erreur : Capacité maximale de monstres atteinte.")
        return jsonify({"error": "Capacité maximale de monstres atteinte."}), 400

    if monster_id in player["monsters"]:
        print(f"Erreur : Monstre {monster_id} déjà présent dans la liste du joueur.")
        return jsonify({"error": "Monstre déjà présent dans la liste."}), 400

    # Ajout du monstre à l'inventaire
    player["monsters"].append(monster_id)
    players_collection.update_one({"username": username}, {"$set": player})
    print(f"Monstre {monster_id} ajouté pour le joueur {username}.")
    return jsonify({"message": "Monstre ajouté avec succès.", "monsters": player["monsters"]}), 201

# Endpoint pour supprimer un monstre de l'inventaire
@app.route('/player/monsters/<monster_id>', methods=['DELETE'])
def remove_monster(monster_id):
    """
    Supprime un monstre de la liste du joueur connecté.
    """
    username = request.username
    print(f"Requête reçue pour supprimer le monstre {monster_id} du joueur {username}.")

    player = players_collection.find_one({"username": username})
    if not player:
        print(f"Erreur : Joueur {username} introuvable.")
        return jsonify({"error": "Joueur introuvable."}), 404

    if monster_id not in player["monsters"]:
        print(f"Erreur : Monstre {monster_id} introuvable dans la liste du joueur.")
        return jsonify({"error": "Monstre introuvable dans la liste du joueur."}), 404

    player["monsters"].remove(monster_id)
    players_collection.update_one({"username": username}, {"$set": player})
    print(f"Monstre {monster_id} supprimé pour le joueur {username}.")
    return jsonify({"message": "Monstre supprimé avec succès.", "monsters": player["monsters"]}), 200

# Point d'entrée de l'application
if __name__ == '__main__':
    # Lancement de l'application Flask
    print(f"Démarrage de l'application PlayerAPI sur le port {API_PORT}...")
    app.run(host='0.0.0.0', port=API_PORT, debug=True)
