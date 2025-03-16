# $$\      $$\                                 $$\                                   
# $$$\    $$$ |                                $$ |                                  
# $$$$\  $$$$ | $$$$$$\  $$$$$$$\   $$$$$$$\ $$$$$$\    $$$$$$\   $$$$$$\   $$$$$$$\ 
# $$\$$\$$ $$ |$$  __$$\ $$  __$$\ $$  _____|\_$$  _|  $$  __$$\ $$  __$$\ $$  _____|
# $$ \$$$  $$ |$$ /  $$ |$$ |  $$ |\$$$$$$\    $$ |    $$$$$$$$ |$$ |  \__|\$$$$$$\  
# $$ |\$  /$$ |$$ |  $$ |$$ |  $$ | \____$$\   $$ |$$\ $$   ____|$$ |       \____$$\ 
# $$ | \_/ $$ |\$$$$$$  |$$ |  $$ |$$$$$$$  |  \$$$$  |\$$$$$$$\ $$ |      $$$$$$$  |
# \__|     \__| \______/ \__|  \__|\_______/    \____/  \_______|\__|      \_______/ 
                                                                                   
import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import math
import json
import random

# Initialisation de Flask
app = Flask(__name__)

# Configuration via variables d'environnement
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 27017))
API_PORT = int(os.getenv('API_PORT', 5002))
PLAYER_API_URL = os.getenv('PLAYER_API_URL', 'http://localhost:5001')  # URL de l'API Player
AUTH_API_URL = os.getenv('AUTH_API_URL', 'http://localhost:5000')
SUMMON_API_KEY = os.getenv('SUMMON_API_KEY', 'CLE_API_TRES_SAFE')

# Connexion à la base de données MongoDB
print(f"Connexion à MongoDB sur {DB_HOST}:{DB_PORT}...")
client = MongoClient(f'mongodb://{DB_HOST}:{DB_PORT}/')
db = client['monsters_db']
monsters_collection = db['monsters']

# Chargement des monstres de base depuis un fichier JSON
data_file_path = os.path.join(os.path.dirname(__file__), "data.json")
if os.path.exists(data_file_path):
    with open(data_file_path, "r") as file:
        try:
            data = json.load(file)
            for monster in data:
                monster["_id"] = str(monster["_id"])
                if not monsters_collection.find_one({"_id": monster["_id"]}):
                    monsters_collection.insert_one(monster)
            print("Les données de base des monstres ont été chargées.")
        except json.JSONDecodeError as e:
            print(f"Erreur lors du chargement de data.json : {e}")
else:
    print("Erreur : Fichier data.json introuvable.")

# Liste de préfixes et suffixes pour générer des noms de monstres
MONSTER_NAME_PREFIXES = [
    "Shadow", "Blaze", "Frost", "Storm", "Thunder", "Crystal", "Dark", "Light",
    "Ancient", "Mystic", "Chaos", "Cosmic", "Dragon", "Phoenix", "Titan", "Void",
    "Celestial", "Infernal", "Divine", "Eternal", "Savage", "Wild", "Feral", "Primal"
]

MONSTER_NAME_SUFFIXES = [
    "heart", "blade", "claw", "fang", "wing", "scale", "tail", "horn",
    "soul", "spirit", "mind", "eye", "breath", "fury", "rage", "might",
    "force", "power", "strike", "guard", "shield", "armor", "walker", "stalker"
]

def generate_monster_name():
    """
    Génère un nom aléatoire pour un monstre en combinant un préfixe et un suffixe.
    """
    prefix = random.choice(MONSTER_NAME_PREFIXES)
    suffix = random.choice(MONSTER_NAME_SUFFIXES)
    return f"{prefix}{suffix}"

# Fonction pour valider un token via AuthAPI
def validate_token(token):
    """
    Valide le token auprès de l'API Auth.
    """
    try:
        response = requests.post(f"{AUTH_API_URL}/validate", json={"token": token})
        if response.status_code == 200:
            return response.json().get("username")
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la validation du token : {e}")
        return None

# Middleware pour valider le token
@app.before_request
def verify_token():
    """
    Vérifie le token pour chaque requête (sauf health_check).
    """
    if request.endpoint not in ['health_check', 'create_monster']:
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
    """
    Vérifie que l'API fonctionne correctement.
    """
    return jsonify({"message": "L'API fonctionne correctement !"}), 200

# Endpoint pour créer une instance de monstre
@app.route('/monsters', methods=['POST'])
def create_monster():
    """
    Endpoint protégé pour créer un monstre.
    Seules les requêtes authentifiées provenant de SummonAPI peuvent l'utiliser.
    """
    api_key = request.headers.get('X-API-Key')
    if api_key != SUMMON_API_KEY:
        return jsonify({"error": "Accès non autorisé."}), 403

    data = request.json
    required_fields = ["monster_type", "element", "hp", "atk", "def", "vit", "skills", "owner"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Données incomplètes pour la création du monstre."}), 400

    new_monster = {
        "_id": str(ObjectId()),
        "name": generate_monster_name(),  # Ajout du nom généré
        "monster_type": data["monster_type"],
        "element": data["element"],
        "hp": data["hp"],
        "atk": data["atk"],
        "def": data["def"],
        "vit": data["vit"],
        "skills": data["skills"],
        "owner": data["owner"],
        "level": 1,
        "experience": 0,
        "skill_points": 0,
    }

    monsters_collection.insert_one(new_monster)
    return jsonify({"id": new_monster["_id"], "message": "Monstre créé avec succès."}), 201

# Endpoint pour supprimer un monstre
@app.route('/monsters/<monster_id>', methods=['DELETE'])
def delete_monster(monster_id):
    """
    Supprime un monstre de la base de données et de l'inventaire du joueur.
    """
    print(f"Requête reçue pour supprimer le monstre {monster_id}.")

    # Récupérer le monstre dans la base de données
    monster = monsters_collection.find_one({"_id": monster_id})
    if not monster:
        print(f"Erreur : Monstre {monster_id} introuvable.")
        return jsonify({"error": "Monstre introuvable."}), 404

    # Si le monstre appartient à un joueur, le retirer de son inventaire via PlayerAPI
    owner = monster.get("owner")
    if owner:
        print(f"Monstre {monster_id} appartient à {owner}. Tentative de suppression de l'inventaire.")
        try:
            response = requests.delete(
                f"{PLAYER_API_URL}/player/monsters/{monster_id}",
                headers={"Authorization": request.headers.get("Authorization")},
            )
            if response.status_code != 200:
                print(f"Erreur lors de la suppression du monstre dans PlayerAPI : {response.text}")
                return jsonify({"error": "Impossible de supprimer le monstre de l'inventaire du joueur."}), 500
        except requests.exceptions.RequestException as e:
            print(f"Erreur de communication avec PlayerAPI : {e}")
            return jsonify({"error": "Erreur de communication avec PlayerAPI."}), 500

    # Supprimer le monstre de la base de données MonstersAPI
    result = monsters_collection.delete_one({"_id": monster_id})
    if result.deleted_count == 0:
        print(f"Erreur : Monstre {monster_id} introuvable ou déjà supprimé.")
        return jsonify({"error": "Monstre introuvable ou déjà supprimé."}), 404

    print(f"Monstre {monster_id} supprimé avec succès.")
    return jsonify({"message": "Monstre supprimé avec succès."}), 200


# Endpoint pour obtenir les informations d'un monstre
@app.route('/monsters/<monster_id>', methods=['GET'])
def get_monster(monster_id):
    """
    Récupère les informations d'un monstre spécifique.
    """
    username = request.username
    monster = monsters_collection.find_one({"_id": monster_id, "owner": username})
    if not monster:
        return jsonify({"error": "Monstre introuvable ou non associé à l'utilisateur."}), 404

    monster["_id"] = str(monster["_id"])
    return jsonify(monster), 200

# Endpoint pour ajouter de l'expérience à un monstre
@app.route('/monsters/<monster_id>/experience', methods=['PUT'])
def add_experience(monster_id):
    """
    Ajoute de l'expérience à un monstre et gère son leveling.
    """
    username = request.username
    data = request.json
    experience_gain = data.get('experience', 0)

    if experience_gain <= 0:
        return jsonify({"error": "Un gain d'expérience positif est requis."}), 400

    monster = monsters_collection.find_one({"_id": monster_id, "owner": username})
    if not monster:
        return jsonify({"error": "Monstre introuvable ou non associé à l'utilisateur."}), 404

    monster["experience"] += experience_gain
    level_up_threshold = 50 * math.pow(1.1, monster["level"])

    while monster["experience"] >= level_up_threshold:
        monster["level"] += 1
        monster["experience"] -= level_up_threshold
        monster["skill_points"] += 1
        monster["hp"] += 10
        monster["atk"] += 5
        monster["def"] += 3
        monster["vit"] += 2
        level_up_threshold = 50 * math.pow(1.1, monster["level"])

    monsters_collection.update_one({"_id": monster_id}, {"$set": monster})
    return jsonify({"message": "Expérience ajoutée.", "monster": monster}), 200

# Endpoint pour utiliser un point de compétence
@app.route('/monsters/<monster_id>/skills/<int:skill_num>', methods=['PUT'])
def use_skill_point(monster_id, skill_num):
    """
    Utilise un point de compétence pour améliorer une compétence spécifique.
    """
    username = request.username
    print(f"Requête reçue pour améliorer la compétence {skill_num} du monstre {monster_id} par {username}.")

    # Vérifier si le monstre appartient à l'utilisateur
    monster = monsters_collection.find_one({"_id": monster_id, "owner": username})
    if not monster:
        print(f"Erreur : Monstre {monster_id} introuvable ou n'appartient pas à l'utilisateur.")
        return jsonify({"error": "Monstre introuvable ou n'appartient pas à l'utilisateur."}), 404

    if monster["skill_points"] <= 0:
        print("Erreur : Pas de points de compétence disponibles.")
        return jsonify({"error": "Pas de points de compétence disponibles."}), 400

    # Vérifier que le numéro de compétence est valide
    skills = monster.get("skills", [])
    if skill_num < 1 or skill_num > len(skills):
        print(f"Erreur : Compétence {skill_num} invalide.")
        return jsonify({"error": "Numéro de compétence invalide."}), 400

    skill = skills[skill_num - 1]
    if skill["lvlMax"] <= skill.get("level", 1):
        print(f"Erreur : Compétence {skill_num} a atteint son niveau maximum.")
        return jsonify({"error": "Niveau maximum atteint pour cette compétence."}), 400

    # Améliorer la compétence
    skill["level"] = skill.get("level", 1) + 1
    skill["dmg"] += 10  # Exemple d'augmentation des dégâts de base
    skill["ratio"]["percent"] += 2  # Exemple d'augmentation du ratio
    monster["skill_points"] -= 1

    # Mise à jour dans la base de données
    monsters_collection.update_one({"_id": monster_id}, {"$set": {"skills": skills, "skill_points": monster["skill_points"]}})
    print(f"Compétence {skill_num} du monstre {monster_id} améliorée avec succès.")
    return jsonify({"message": "Compétence améliorée avec succès.", "monster": monster}), 200

# Point d'entrée de l'application
if __name__ == '__main__':
    print(f"Démarrage de MonstersAPI sur le port {API_PORT}...")
    app.run(host='0.0.0.0', port=API_PORT, debug=True)
