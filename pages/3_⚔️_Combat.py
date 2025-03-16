import streamlit as st

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="Combat - IMTasy Warriors",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
from constants import *
from utils import display_monster_details, setup_navigation
import time
import random

print("[DEBUG COMBAT] Démarrage de la page de combat")

# Vérification de l'authentification
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("dashboard.py")

# Configuration de la navigation
setup_navigation()

# Styles CSS personnalisés
st.markdown("""
    <style>
        .main {
            background-color: #1E1E1E;
        }
        .monster-card {
            background-color: #2E2E2E;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 2px solid #4CAF50;
        }
        .monster-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2);
        }
        .battle-container {
            text-align: center;
            padding: 20px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #4CAF50;
        }
        .vs-text {
            font-size: 48px;
            color: #4CAF50;
            margin: 20px 0;
            text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        .title-container {
            text-align: center;
            padding: 20px;
            background: linear-gradient(90deg, #1E1E1E, #2E2E2E, #1E1E1E);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .battle-button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.3s ease;
            width: 100%;
            margin: 10px 0;
        }
        .battle-button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        }
        .victory-animation {
            animation: victory-pulse 2s infinite;
        }
        @keyframes victory-pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
""", unsafe_allow_html=True)

print(f"[DEBUG COMBAT] État de session : {dict(st.session_state)}")
print(f"[DEBUG COMBAT] Token : {st.session_state.get('token')}")

st.markdown("""
    <div class="title-container">
        <h1 style='color: #4CAF50;'>Combat</h1>
    </div>
""", unsafe_allow_html=True)

# Récupération des monstres du joueur
try:
    print(f"[DEBUG COMBAT] Tentative de récupération des monstres depuis {PLAYER_API_URL}/player")
    # D'abord, récupérer la liste des IDs des monstres du joueur
    player_response = requests.get(
        f"{PLAYER_API_URL}/player",
        headers={"Authorization": st.session_state["token"]}
    )
    print(f"[DEBUG COMBAT] Code de réponse Player API : {player_response.status_code}")
    print(f"[DEBUG COMBAT] Contenu de la réponse Player : {player_response.text}")
    
    if player_response.status_code == 200:
        player_data = player_response.json()
        monster_ids = player_data.get("monsters", [])
        print(f"[DEBUG COMBAT] IDs des monstres récupérés : {monster_ids}")
        
        # Ensuite, récupérer les détails de chaque monstre
        player_monsters = []
        for monster_id in monster_ids:
            print(f"[DEBUG COMBAT] Récupération des détails du monstre {monster_id}")
            monster_response = requests.get(
                f"{MONSTERS_API_URL}/monsters/{monster_id}",
                headers={"Authorization": st.session_state["token"]}
            )
            print(f"[DEBUG COMBAT] Réponse pour le monstre {monster_id} : {monster_response.status_code}")
            
            if monster_response.status_code == 200:
                monster = monster_response.json()
                player_monsters.append(monster)
            else:
                print(f"[DEBUG COMBAT] Erreur lors de la récupération du monstre {monster_id} : {monster_response.text}")
        
        print(f"[DEBUG COMBAT] Tous les monstres récupérés : {player_monsters}")
        
        if not player_monsters:
            st.warning("Vous n'avez pas encore de monstres. Allez en invoquer !")
            st.stop()
            
    else:
        print(f"[DEBUG COMBAT] Erreur lors de la récupération du profil joueur : {player_response.text}")
        st.error(f"Erreur lors de la récupération de vos monstres. Code : {player_response.status_code}, Message : {player_response.text}")
        st.stop()
except Exception as e:
    print(f"[DEBUG COMBAT] Exception lors de la récupération des monstres : {str(e)}")
    st.error(f"Erreur : {str(e)}")
    st.stop()

# Sélection des monstres pour le combat
col1, col2 = st.columns(2)

with col1:
    st.subheader("Votre monstre")
    print("[DEBUG COMBAT] Options pour le selectbox :", [m["_id"] for m in player_monsters])
    selected_monster = st.selectbox(
        "Choisissez votre monstre",
        options=[m["_id"] for m in player_monsters],
        format_func=lambda x: next((m["name"] for m in player_monsters if m["_id"] == x), x)
    )
    print(f"[DEBUG COMBAT] Monstre sélectionné : {selected_monster}")
    
    if selected_monster:
        monster = next((m for m in player_monsters if m["_id"] == selected_monster), None)
        print(f"[DEBUG COMBAT] Détails du monstre sélectionné : {monster}")
        if monster:
            st.markdown(f"""
                <div class="monster-card">
                    <h3 style='color: #4CAF50;'>{monster['name']}</h3>
                    <p style='color: #888;'>Niveau {monster['level']} - {monster['monster_type']}</p>
                    <div style='margin: 10px 0;'>
                        <p><span style='color: #888;'>HP:</span> <span style='color: #4CAF50;'>{monster['hp']}</span></p>
                        <p><span style='color: #888;'>ATK:</span> <span style='color: #4CAF50;'>{monster['atk']}</span></p>
                        <p><span style='color: #888;'>DEF:</span> <span style='color: #4CAF50;'>{monster['def']}</span></p>
                        <p><span style='color: #888;'>VIT:</span> <span style='color: #4CAF50;'>{monster['vit']}</span></p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.subheader("Adversaire")
    opponent_monster = st.selectbox(
        "Choisissez votre adversaire",
        options=[m["_id"] for m in player_monsters if m["_id"] != selected_monster],
        format_func=lambda x: next((m["name"] for m in player_monsters if m["_id"] == x), x)
    )
    print(f"[DEBUG COMBAT] Adversaire sélectionné : {opponent_monster}")
    
    if opponent_monster:
        monster = next((m for m in player_monsters if m["_id"] == opponent_monster), None)
        print(f"[DEBUG COMBAT] Détails de l'adversaire : {monster}")
        if monster:
            st.markdown(f"""
                <div class="monster-card">
                    <h3 style='color: #4CAF50;'>{monster['name']}</h3>
                    <p style='color: #888;'>Niveau {monster['level']} - {monster['monster_type']}</p>
                    <div style='margin: 10px 0;'>
                        <p><span style='color: #888;'>HP:</span> <span style='color: #4CAF50;'>{monster['hp']}</span></p>
                        <p><span style='color: #888;'>ATK:</span> <span style='color: #4CAF50;'>{monster['atk']}</span></p>
                        <p><span style='color: #888;'>DEF:</span> <span style='color: #4CAF50;'>{monster['def']}</span></p>
                        <p><span style='color: #888;'>VIT:</span> <span style='color: #4CAF50;'>{monster['vit']}</span></p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Conteneur pour l'animation de combat
battle_container = st.empty()

if selected_monster and opponent_monster:
    if st.button("COMBATTRE !", use_container_width=True):
        try:
            print(f"[DEBUG COMBAT] Début du combat entre {selected_monster} et {opponent_monster}")
            # Animation de combat
            with battle_container:
                st.markdown("""
                    <div class="battle-container">
                        <h2 style='color: #4CAF50;'>Combat en cours...</h2>
                        <div class="vs-text">⚔️</div>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(1)

            # Appel à l'API de combat
            print(f"[DEBUG COMBAT] Appel à l'API de combat : {BATTLE_API_URL}/battle")
            response = requests.post(
                f"{BATTLE_API_URL}/battle",
                headers={"Authorization": st.session_state["token"]},
                json={
                    "monster1_id": selected_monster,
                    "monster2_id": opponent_monster
                }
            )
            print(f"[DEBUG COMBAT] Réponse du combat : {response.status_code} - {response.text}")

            if response.status_code == 200:
                result = response.json()
                winner_name = result.get("winner_name", "Inconnu")
                monster_xp = result.get("monster_xp_gain", 0)
                player_xp = result.get("player_xp_gain", 0)
                print(f"[DEBUG COMBAT] Résultat du combat - Vainqueur : {winner_name}, XP monstre : {monster_xp}, XP joueur : {player_xp}")

                with battle_container:
                    st.markdown(f"""
                        <div class="battle-container victory-animation">
                            <h2 style='color: #4CAF50;'>🏆 Victoire de {winner_name} ! 🏆</h2>
                            <p style='color: #888;'>XP gagné par le monstre : {monster_xp}</p>
                            <p style='color: #888;'>XP gagné par le joueur : {player_xp}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                print(f"[DEBUG COMBAT] Erreur lors du combat : {response.text}")
                st.error(f"Erreur lors du combat. Code : {response.status_code}, Message : {response.text}")
        except Exception as e:
            print(f"[DEBUG COMBAT] Exception lors du combat : {str(e)}")
            st.error(f"Erreur : {str(e)}")
else:
    st.info("Sélectionnez deux monstres différents pour commencer le combat.") 