import requests
import math
from random import randint

# Configuration des URLs
PLAYER_API_URL = "http://localhost:5001"
AUTH_API_URL = "http://localhost:5000"

def register_user(username, password):
    """
    Enregistre un utilisateur et retourne le token en cas de succès.
    """
    register_endpoint = f"{AUTH_API_URL}/register"
    response = requests.post(register_endpoint, json={"identifiant": username, "password": password})
    if response.status_code == 201:
        print("Utilisateur enregistré avec succès.")
        return response.json()["token"]
    elif response.status_code == 400 and "déjà utilisé" in response.text.lower():
        print("Utilisateur déjà enregistré.")
        return None
    else:
        print("Erreur lors de l'enregistrement :", response.text)
        return None

def adjust_inventory_for_summons(token, summon_count):
    """
    Augmente l'expérience pour obtenir un inventaire suffisant pour le nombre de summons souhaité.
    """
    experience_endpoint = f"{PLAYER_API_URL}/player/experience"
    headers = {"Authorization": token, "Content-Type": "application/json"}

    while True:
        # Ajout d'expérience pour augmenter l'inventaire
        response = requests.put(experience_endpoint, headers=headers, json={"experience": 5000})
        if response.status_code != 200:
            print("Erreur lors de l'ajout d'expérience :", response.text)
            return False

        player_data = response.json()["player"]
        max_monsters = player_data["max_monsters"]

        if max_monsters >= summon_count:
            print(f"L'inventaire est suffisant : {max_monsters} slots disponibles.")
            return True

        print(f"Ajout d'expérience. Inventaire actuel : {max_monsters} slots. Objectif : {summon_count} slots.")

def summon_monsters(token, summon_count):
    """
    Invoque des monstres pour l'utilisateur connecté via SummonAPI.
    """
    summon_endpoint = "http://localhost:5003/summon"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    
    for i in range(summon_count):
        response = requests.post(summon_endpoint, headers=headers)
        if response.status_code == 201:
            print(f"Invocation {i + 1} réussie :", response.json())
        else:
            print(f"Erreur lors de l'invocation {i + 1} :", response.text)

def main():
    """
    Script principal pour gérer l'augmentation d'inventaire et les summons.
    """
    # Paramètres utilisateur
    username = f"test_user_{randint(1000, 9999)}"
    password = "test_password"

    # Enregistrement de l'utilisateur
    print("Tentative d'enregistrement...")
    token = register_user(username, password)
    if not token:
        print("Échec de l'enregistrement ou utilisateur déjà enregistré.")
        return

    # Demander le nombre de summons à l'utilisateur
    summon_count = int(input("Entrez le nombre de summons souhaités : "))

    # Vérifier et ajuster l'inventaire
    print("Vérification de l'inventaire...")
    if not adjust_inventory_for_summons(token, summon_count):
        print("Échec de la mise à niveau de l'inventaire.")
        return

    # Invoquer les monstres
    print(f"Invoquant {summon_count} monstres...")
    summon_monsters(token, summon_count)

if __name__ == "__main__":
    main()
