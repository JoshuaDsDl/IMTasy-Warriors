# URLs des API et constantes
import os

# Récupération des URLs depuis les variables d'environnement (avec fallback aux valeurs locales)
AUTH_API_URL = os.environ.get("AUTH_API_URL", "http://localhost:5000")
PLAYER_API_URL = os.environ.get("PLAYER_API_URL", "http://localhost:5001")
MONSTERS_API_URL = os.environ.get("MONSTERS_API_URL", "http://localhost:5002")
SUMMON_API_URL = os.environ.get("SUMMON_API_URL", "http://localhost:5003")
BATTLE_API_URL = os.environ.get("BATTLE_API_URL", "http://localhost:5004")

import streamlit as st
import requests
import json
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
from constants import *
from utils import display_player_stats

# Configuration initiale de la page
st.set_page_config(
    page_title="IMTasy Warriors",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
        /* Masquer le menu hamburger */
        #MainMenu {visibility: hidden;}
        
        /* Masquer le pied de page */
        footer {visibility: hidden;}
        
        /* Masquer le bouton Deploy */
        .stDeployButton {display: none;}
        
        /* Masquer la barre colorée de Streamlit */
        div[data-testid="stDecoration"] {visibility: hidden;}
        
        /* Style pour la page de connexion */
        .login-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background: rgba(46, 46, 46, 0.95);
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #4CAF50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #888;
            font-size: 1.2em;
        }
        
        .stTextInput > div > div > input {
            background-color: #1E1E1E;
            color: #4CAF50;
            border: 2px solid #4CAF50;
            border-radius: 5px;
            padding: 10px;
        }
        
        .stButton > button {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            margin-top: 10px !important;
        }
        
        .stButton > button:hover {
            background-color: #45a049 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2) !important;
        }
        
        .stTabs > div > div > div {
            background-color: #2E2E2E;
            border-radius: 5px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .stTabs > div > div > div > div > div > button {
            color: #4CAF50 !important;
            background-color: transparent !important;
        }
        
        .stTabs > div > div > div > div > div > button[data-baseweb="tab"][aria-selected="true"] {
            color: white !important;
            border-bottom: 2px solid #4CAF50 !important;
        }
        
        /* Masquer la barre latérale quand non connecté */
        [data-testid="stSidebar"][aria-expanded="true"] {
            display: none;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Fonction pour gérer l'authentification
def handle_auth(auth_type):
    """
    Gère l'authentification (connexion ou inscription)
    """
    print(f"[DEBUG] Début de handle_auth avec auth_type={auth_type}")
    print(f"[DEBUG] État de session actuel : {dict(st.session_state)}")
    
    with st.form(f"{auth_type}_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter" if auth_type == "login" else "S'inscrire")
        
        if submit and username and password:
            print(f"[DEBUG] Tentative de {auth_type} pour l'utilisateur {username}")
            try:
                endpoint = "/login" if auth_type == "login" else "/register"
                print(f"[DEBUG] Appel à l'endpoint {endpoint}")
                print(f"[DEBUG] URL complète : {AUTH_API_URL}{endpoint}")
                print(f"[DEBUG] Données envoyées : {{'identifiant': {username}, 'password': '***'}}")
                
                auth_response = requests.post(
                    f"{AUTH_API_URL}{endpoint}",
                    json={"identifiant": username, "password": password}
                )
                
                print(f"[DEBUG] Réponse de l'authentification : {auth_response.status_code}")
                print(f"[DEBUG] Contenu de la réponse : {auth_response.text}")
                
                if auth_response.status_code not in [200, 201]:
                    st.error(auth_response.json().get("error", "Erreur d'authentification"))
                    print(f"[DEBUG] Erreur d'authentification : {auth_response.text}")
                    return False
                
                token = auth_response.json()["token"]
                print("[DEBUG] Token obtenu avec succès")
                
                if auth_type == "login":
                    print("[DEBUG] Vérification du profil joueur existant")
                    player_response = requests.get(
                        f"{PLAYER_API_URL}/player",
                        headers={"Authorization": token}
                    )
                    if player_response.status_code == 404:
                        print("[DEBUG] Profil non trouvé, création d'un nouveau profil")
                        create_response = requests.post(
                            f"{PLAYER_API_URL}/player",
                            headers={"Authorization": token}
                        )
                        if create_response.status_code != 201:
                            st.error(f"Erreur lors de la création du profil joueur : {create_response.text}")
                            print(f"[DEBUG] Erreur création profil : {create_response.text}")
                            return False
                
                print("[DEBUG] Mise à jour de la session")
                st.session_state["token"] = token
                st.session_state["username"] = username
                st.session_state["authenticated"] = True
                
                print(f"[DEBUG] Nouvel état de session : {dict(st.session_state)}")
                
                # Redirection vers le dashboard
                st.switch_page("pages/1_🎮_Dashboard.py")
                return True
                
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
                print(f"[DEBUG] Exception dans handle_auth : {str(e)}")
                print(f"[DEBUG] Type d'exception : {type(e)}")
                print(f"[DEBUG] Détails de l'exception : {e.__dict__}")
                return False
    
    return False

# Fonction pour afficher les statistiques du joueur
def display_player_stats():
    try:
        response = requests.get(
            f"{PLAYER_API_URL}/player",
            headers={"Authorization": st.session_state["token"]}
        )
        if response.status_code == 200:
            player_data = response.json()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Niveau", player_data["level"])
            with col2:
                st.metric("Expérience", f"{player_data['experience']} XP")
            with col3:
                st.metric("Monstres", f"{len(player_data['monsters'])}/{player_data['max_monsters']}")
                
            # Graphique d'expérience
            fig = go.Figure(go.Indicator(
                mode="gauge",
                value=player_data["experience"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Progression d'expérience", 'font': {'color': '#4CAF50'}},
                number={'visible': False},  # Masquer le nombre
                gauge={
                    'axis': {
                        'range': [0, player_data['xp_next_level']],
                        'tickwidth': 1,
                        'tickcolor': "#4CAF50",
                        'tickfont': {'color': '#4CAF50'},
                        'showticklabels': False  # Masquer les étiquettes de l'axe
                    },
                    'bar': {'color': "#4CAF50"},
                    'bgcolor': "#2E2E2E",
                    'borderwidth': 2,
                    'bordercolor': "#4CAF50",
                    'steps': [
                        {'range': [0, player_data['xp_next_level']], 'color': 'rgba(0,0,0,0)'}
                    ]
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "#4CAF50"},
                margin=dict(t=80, b=0, l=0, r=0),
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            return player_data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données du joueur : {str(e)}")
        return None

# Fonction pour afficher les détails d'un monstre
def display_monster_details(monster_id):
    try:
        response = requests.get(
            f"{MONSTERS_API_URL}/monsters/{monster_id}",
            headers={"Authorization": st.session_state["token"]}
        )
        if response.status_code == 200:
            monster = response.json()
            
            st.markdown(f"""
                <div class="monster-card">
                    <h2 style='color: #4CAF50;'>{monster['name']} - {monster['monster_type']}</h2>
                    <h3 style='color: #888;'>Niveau {monster['level']}</h3>
                    <div class="stat-container">
                        <span class="stat-label">HP:</span>
                        <span class="stat-value">{monster['hp']}</span>
                    </div>
                    <div class="stat-container">
                        <span class="stat-label">ATK:</span>
                        <span class="stat-value">{monster['atk']}</span>
                    </div>
                    <div class="stat-container">
                        <span class="stat-label">DEF:</span>
                        <span class="stat-value">{monster['def']}</span>
                    </div>
                    <div class="stat-container">
                        <span class="stat-label">VIT:</span>
                        <span class="stat-value">{monster['vit']}</span>
                    </div>
                    <div class="stat-container">
                        <span class="stat-label">Expérience:</span>
                        <span class="stat-value">{monster['experience']}</span>
                    </div>
                    <div class="stat-container">
                        <span class="stat-label">Points de compétence:</span>
                        <span class="stat-value">{monster['skill_points']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Affichage des compétences
            if monster['skill_points'] > 0:
                st.info(f"Vous avez {monster['skill_points']} points de compétence à utiliser!")
            
            st.subheader("Compétences")
            for i, skill in enumerate(monster['skills']):
                with st.expander(f"Compétence {i+1} - Niveau {skill.get('level', 1)}/{skill['lvlMax']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div class="monster-card">
                                <div class="stat-container">
                                    <span class="stat-label">Dégâts de base:</span>
                                    <span class="stat-value">{skill['dmg']}</span>
                                </div>
                                <div class="stat-container">
                                    <span class="stat-label">Ratio:</span>
                                    <span class="stat-value">{skill['ratio']['percent']}% {skill['ratio']['stat']}</span>
                                </div>
                                <div class="stat-container">
                                    <span class="stat-label">Cooldown:</span>
                                    <span class="stat-value">{skill['cooldown']} tours</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if monster['skill_points'] > 0 and skill.get('level', 1) < skill['lvlMax']:
                            if st.button(f"Améliorer la compétence (1 point)", key=f"skill_{monster_id}_{i}"):
                                response = requests.put(
                                    f"{MONSTERS_API_URL}/monsters/{monster_id}/skills/{i+1}",
                                    headers={"Authorization": st.session_state["token"]}
                                )
                                if response.status_code == 200:
                                    st.success("Compétence améliorée!")
                                    st.rerun()
                                else:
                                    st.error("Erreur lors de l'amélioration de la compétence")
                        elif skill.get('level', 1) >= skill['lvlMax']:
                            st.warning("Niveau maximum atteint!")
                        elif monster['skill_points'] <= 0:
                            st.warning("Pas de points de compétence disponibles")
            
            return monster
    except Exception as e:
        st.error(f"Erreur lors de la récupération des détails du monstre : {str(e)}")
        return None

def calculate_experience_gain(winner_stats, loser_stats):
    """
    Calcule le gain d'expérience basé sur les statistiques des monstres.
    Plus la différence de niveau est grande, plus le gain est important.
    """
    base_xp = 20
    level_diff = loser_stats['level'] - winner_stats['level']
    level_multiplier = 1 + (0.1 * level_diff) if level_diff > 0 else max(0.1, 1 + (0.05 * level_diff))
    
    # Bonus basé sur les stats totales du perdant
    loser_total_stats = loser_stats['hp'] + loser_stats['atk'] + loser_stats['def'] + loser_stats['vit']
    stats_multiplier = loser_total_stats / 100
    
    return int(base_xp * level_multiplier * stats_multiplier)

def display_combat_result(response_data):
    if "winner_id" in response_data:
        winner_name = response_data.get("winner_name", "Inconnu")
        monster_xp = response_data.get("monster_xp_gain", 0)
        player_xp = response_data.get("player_xp_gain", 0)
        
        victory_message = f"""
        🏆 Victoire de {winner_name} ! 🏆
        XP gagné par le monstre : {monster_xp}
        XP gagné par le joueur : {player_xp}
        """
        
        st.session_state.victory_message = victory_message
        st.session_state.show_victory = True
        time.sleep(0.1)  # Petit délai pour assurer l'affichage
        st.rerun()

# Interface principale
def main():
    print("[DEBUG] Début de main()")
    print(f"[DEBUG] État de session au début de main : {dict(st.session_state)}")
    
    # Initialiser les variables de session si elles n'existent pas
    if "authenticated" not in st.session_state:
        print("[DEBUG] Initialisation de authenticated à False")
        st.session_state["authenticated"] = False
        st.session_state["token"] = None
        st.session_state["username"] = None
    
    print(f"[DEBUG] État de session après initialisation : {dict(st.session_state)}")
    
    # Page d'authentification
    if not st.session_state["authenticated"]:
        st.markdown("""
            <div class="login-container">
                <div class="login-header">
                    <h1>⚔️ IMTasy Warriors</h1>
                    <p>Embarquez dans une aventure épique</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            tab1, tab2 = st.tabs(["Connexion", "Inscription"])
            with tab1:
                if handle_auth("login"):
                    st.success("Connexion réussie!")
            with tab2:
                if handle_auth("register"):
                    st.success("Inscription réussie!")
    else:
        # Redirection vers le dashboard si déjà connecté
        st.switch_page("pages/1_🎮_Dashboard.py")

if __name__ == "__main__":
    main()
