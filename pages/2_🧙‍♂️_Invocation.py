import streamlit as st

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="Invocation - IMTasy Warriors",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
from constants import *
import time
import random
import plotly.graph_objects as go
from utils import setup_navigation

print("[DEBUG INVOCATION] Démarrage de la page d'invocation")

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
        .title-container {
            text-align: center;
            padding: 20px;
            background: linear-gradient(90deg, #1E1E1E, #2E2E2E, #1E1E1E);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .summon-animation {
            text-align: center;
            padding: 40px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #4CAF50;
            animation: glow 2s infinite;
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #4CAF50; }
            50% { box-shadow: 0 0 20px #4CAF50; }
            100% { box-shadow: 0 0 5px #4CAF50; }
        }
        .stat-container {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 10px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 5px;
        }
        .stat-label {
            color: #888;
        }
        .stat-value {
            color: #4CAF50;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Vérification de l'authentification
print(f"[DEBUG INVOCATION] État de session : {dict(st.session_state)}")
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    print("[DEBUG INVOCATION] Utilisateur non authentifié")
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

print(f"[DEBUG INVOCATION] Token : {st.session_state.get('token')}")

# Configuration de la navigation
setup_navigation()

st.markdown("""
    <div class="title-container">
        <h1 style='color: #4CAF50;'>Invocation</h1>
    </div>
""", unsafe_allow_html=True)

# Conteneur pour l'animation d'invocation
summon_container = st.empty()

def display_monster_details(monster):
    print(f"[DEBUG INVOCATION] Affichage des détails du monstre : {monster}")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Description du monstre
        st.markdown(f"## {monster.get('name', 'Inconnu')}")
        st.markdown(f"### {monster.get('monster_type', 'Type inconnu')} - Niveau {monster.get('level', '?')}")
        
        # Statistiques
        st.markdown("#### Statistiques")
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("HP", monster.get('hp', '?'))
            st.metric("ATK", monster.get('atk', '?'))
        with stats_col2:
            st.metric("DEF", monster.get('def', '?'))
            st.metric("VIT", monster.get('vit', '?'))
        
        # Affichage des compétences
        st.markdown("#### Compétences")
        for i, skill in enumerate(monster.get('skills', [])):
            print(f"[DEBUG INVOCATION] Affichage de la compétence {i+1} : {skill}")
            with st.expander(f"Compétence {i+1}"):
                st.metric("Dégâts de base", skill.get('dmg', '?'))
                st.metric("Ratio", f"{skill.get('ratio', {}).get('percent', '?')}% {skill.get('ratio', {}).get('stat', '?')}")
                st.metric("Cooldown", f"{skill.get('cooldown', '?')} tours")
    
    with col2:
        print("[DEBUG INVOCATION] Création du graphique radar")
        # Graphique radar des statistiques
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=[monster.get('atk', 0), monster.get('def', 0), monster.get('vit', 0), monster.get('hp', 0)],
            theta=['ATK', 'DEF', 'VIT', 'HP'],
            fill='toself',
            name=monster.get('name', 'Inconnu'),
            line_color='#4CAF50'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(monster.get('atk', 0), monster.get('def', 0), monster.get('vit', 0), monster.get('hp', 0)) * 1.2]
                )
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)

if st.button("Invoquer un monstre", use_container_width=True):
    try:
        print("[DEBUG INVOCATION] Début de l'invocation")
        # Animation d'invocation
        with summon_container:
            st.markdown("""
                <div class="summon-animation">
                    <h2 style='color: #4CAF50;'>✨ Invocation en cours... ✨</h2>
                    <div style='font-size: 48px; margin: 20px;'>
                        <span style='animation: glow 1s infinite'>🌟</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
        
        print(f"[DEBUG INVOCATION] Appel à l'API d'invocation : {SUMMON_API_URL}/summon")
        response = requests.post(
            f"{SUMMON_API_URL}/summon",
            headers={"Authorization": st.session_state["token"]}
        )
        print(f"[DEBUG INVOCATION] Réponse de l'invocation : {response.status_code} - {response.text}")
        
        if response.status_code == 201:
            monster_id = response.json()["monster_id"]
            print(f"[DEBUG INVOCATION] Monstre créé avec l'ID : {monster_id}")
            
            # Récupérer les détails du monstre
            print(f"[DEBUG INVOCATION] Récupération des détails du monstre : {MONSTERS_API_URL}/monsters/{monster_id}")
            monster_response = requests.get(
                f"{MONSTERS_API_URL}/monsters/{monster_id}",
                headers={"Authorization": st.session_state["token"]}
            )
            print(f"[DEBUG INVOCATION] Réponse des détails : {monster_response.status_code} - {monster_response.text}")
            
            if monster_response.status_code == 200:
                monster = monster_response.json()
                print(f"[DEBUG INVOCATION] Détails du monstre récupérés : {monster}")
                
                # Afficher le résultat de l'invocation
                with summon_container:
                    st.markdown(f"""
                        <div class="summon-animation">
                            <h2 style='color: #4CAF50;'>✨ Invocation réussie ! ✨</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Afficher les détails du monstre
                    display_monster_details(monster)
            else:
                print(f"[DEBUG INVOCATION] Erreur lors de la récupération des détails : {monster_response.text}")
                st.error(f"Erreur lors de la récupération des détails du monstre. Code : {monster_response.status_code}, Message : {monster_response.text}")
        else:
            print(f"[DEBUG INVOCATION] Erreur lors de l'invocation : {response.text}")
            st.error(f"Erreur lors de l'invocation. Code : {response.status_code}, Message : {response.text}")
    except Exception as e:
        print(f"[DEBUG INVOCATION] Exception lors de l'invocation : {str(e)}")
        st.error(f"Erreur lors de l'invocation : {str(e)}") 