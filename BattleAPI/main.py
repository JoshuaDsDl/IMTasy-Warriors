# $$$$$$$\             $$\     $$\     $$\           
# $$  __$$\            $$ |    $$ |    $$ |          
# $$ |  $$ | $$$$$$\ $$$$$$\ $$$$$$\   $$ | $$$$$$\  
# $$$$$$$\ | \____$$\\_$$  _|\_$$  _|  $$ |$$  __$$\ 
# $$  __$$\  $$$$$$$ | $$ |    $$ |    $$ |$$$$$$$$ |
# $$ |  $$ |$$  __$$ | $$ |$$\ $$ |$$\ $$ |$$   ____|
# $$$$$$$  |\$$$$$$$ | \$$$$  |\$$$$  |$$ |\$$$$$$$\ 
# \_______/  \_______|  \____/  \____/ \__| \_______|

import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import datetime

# Initialisation de Flask
app = Flask(__name__)

# Configuration via variables d'environnement
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 27017))
API_PORT = int(os.getenv('API_PORT', 5004))
MONSTERS_API_URL = os.getenv('MONSTERS_API_URL', 'http://localhost:5002')
AUTH_API_URL = os.getenv('AUTH_API_URL', 'http://localhost:5000')
PLAYER_API_URL = os.getenv('PLAYER_API_URL', 'http://localhost:5003')

# Connexion à MongoDB
client = MongoClient(f'mongodb://{DB_HOST}:{DB_PORT}/')
db = client['battle_db']
battles_collection = db['battles']

# Validation du token via AuthAPI
def validate_token(token):
    try:
        response = requests.post(f"{AUTH_API_URL}/validate", json={"token": token})
        if response.status_code == 200:
            return response.json().get("username")
        return None
    except requests.exceptions.RequestException:
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

# Exécution d'une attaque
def execute_attack(attacker, defender, cooldowns, attacker_id, logs):
    for i in reversed(range(len(attacker["skills"]))):
        if cooldowns[i] == 0:
            skill = attacker["skills"][i]
            damage = skill["dmg"] + (skill["ratio"]["percent"] / 100) * attacker[skill["ratio"]["stat"]]
            cooldowns[i] = skill["cooldown"]
            logs.append(
                f"{attacker_id} utilise compétence {i + 1} (qui a {skill['cooldown']} tours de cooldown) et inflige {int(damage)} dégâts."
            )
            return int(damage)
        else:
            cooldowns[i] -= 1
    logs.append(f"{attacker_id} ne peut utiliser aucune compétence.")
    return 0

# Simulation de combat
def simulate_battle(monster1, monster2):
    logs = []
    cooldowns = {1: [0] * len(monster1["skills"]), 2: [0] * len(monster2["skills"])}
    hp1, hp2 = monster1["hp"], monster2["hp"]
    monster1_id, monster2_id = monster1["_id"], monster2["_id"]

    turn = 1
    while hp1 > 0 and hp2 > 0:
        logs.append(f"--- Tour {turn} ---")
        damage = execute_attack(monster1, monster2, cooldowns[1], monster1_id, logs)
        hp2 -= damage
        if hp2 <= 0:
            break
        damage = execute_attack(monster2, monster1, cooldowns[2], monster2_id, logs)
        hp1 -= damage
        turn += 1

    winner_id = monster1_id if hp1 > 0 else monster2_id
    logs.append(f"Le vainqueur est le monstre avec l'ID {winner_id}.")
    return logs, winner_id

def calculate_experience_gain(winner_stats, loser_stats):
    """
    Calcule le gain d'expérience basé sur les statistiques des monstres.
    Plus la différence de niveau est grande, plus le gain est important.
    Le gain est plafonné pour éviter une progression trop rapide.
    """
    base_xp = 5  # Réduit de 10 à 5
    level_diff = loser_stats['level'] - winner_stats['level']
    level_multiplier = 1 + (0.02 * level_diff) if level_diff > 0 else max(0.1, 1 + (0.01 * level_diff))
    
    # Bonus basé sur les stats totales du perdant
    loser_total_stats = loser_stats['hp'] + loser_stats['atk'] + loser_stats['def'] + loser_stats['vit']
    stats_multiplier = loser_total_stats / 400  # Augmenté de 200 à 400
    
    # Calcul de l'XP avant plafonnement
    xp = int(base_xp * level_multiplier * stats_multiplier)
    
    # Plafonnement de l'XP en fonction du niveau du gagnant
    max_xp = 20 + (5 * winner_stats['level'])  # Un monstre niveau 1 peut gagner max 25 XP
    
    return min(xp, max_xp)

# Endpoint pour démarrer un combat
@app.route('/battle', methods=['POST'])
def start_battle():
    data = request.json
    monster1_id = data.get("monster1_id")
    monster2_id = data.get("monster2_id")
    username = request.username

    if not monster1_id or not monster2_id:
        return jsonify({"error": "Les IDs des deux monstres sont requis."}), 400

    try:
        # Récupération des détails des monstres
        response1 = requests.get(
            f"{MONSTERS_API_URL}/monsters/{monster1_id}",
            headers={"Authorization": request.headers.get("Authorization")}
        )
        response2 = requests.get(
            f"{MONSTERS_API_URL}/monsters/{monster2_id}",
            headers={"Authorization": request.headers.get("Authorization")}
        )

        if response1.status_code != 200:
            return jsonify({"error": f"Le monstre {monster1_id} est introuvable ou inaccessible."}), 404
        if response2.status_code != 200:
            return jsonify({"error": f"Le monstre {monster2_id} est introuvable ou inaccessible."}), 404

        monster1 = response1.json()
        monster2 = response2.json()

        if monster1.get("owner") != username or monster2.get("owner") != username:
            return jsonify({"error": "Un ou plusieurs monstres ne vous appartiennent pas."}), 403

        # Simulation du combat
        battle_logs, winner_id = simulate_battle(monster1, monster2)

        # Déterminer le gagnant et le perdant
        winner_stats = monster1 if winner_id == monster1_id else monster2
        loser_stats = monster2 if winner_id == monster1_id else monster1

        # Calculer l'expérience
        monster_xp_gain = calculate_experience_gain(winner_stats, loser_stats)
        player_xp_gain = int(monster_xp_gain * 0.5)  # Le joueur gagne 50% de l'XP du monstre

        # Ajouter l'XP au monstre gagnant
        response = requests.put(
            f"{MONSTERS_API_URL}/monsters/{winner_id}/experience",
            headers={"Authorization": request.headers.get("Authorization")},
            json={"experience": monster_xp_gain}
        )
        if response.status_code != 200:
            print(f"Erreur lors de l'attribution de l'XP au monstre : {response.text}")

        # Ajouter l'XP au joueur
        response = requests.put(
            f"{PLAYER_API_URL}/player/experience",
            headers={"Authorization": request.headers.get("Authorization")},
            json={"experience": player_xp_gain}
        )
        if response.status_code != 200:
            print(f"Erreur lors de l'attribution de l'XP au joueur : {response.text}")

        combat_id = str(ObjectId())
        battles_collection.insert_one({
            "_id": combat_id,
            "monster1": monster1_id,
            "monster2": monster2_id,
            "logs": battle_logs,
            "winner_id": winner_id,
            "winner_name": winner_stats["name"],
            "monster_xp_gain": monster_xp_gain,
            "player_xp_gain": player_xp_gain,
            "timestamp": datetime.datetime.utcnow()
        })

        return jsonify({
            "message": "Combat simulé avec succès.",
            "combat_id": combat_id,
            "winner_id": winner_id,
            "winner_name": winner_stats["name"],
            "monster_xp_gain": monster_xp_gain,
            "player_xp_gain": player_xp_gain,
            "logs": battle_logs
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors du combat : {str(e)}"}), 500

# Endpoint pour rediffuser un combat
@app.route('/battle/<battle_id>', methods=['GET'])
def replay_battle(battle_id):
    battle = battles_collection.find_one({"_id": battle_id})
    if not battle:
        return jsonify({"error": "Combat introuvable."}), 404
    return jsonify(battle), 200

# Endpoint pour lister les combats
@app.route('/battles', methods=['GET'])
def list_battles():
    battles = list(battles_collection.find({}, {"logs": 0}))
    for battle in battles:
        battle["_id"] = str(battle["_id"])
    return jsonify(battles), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT)
