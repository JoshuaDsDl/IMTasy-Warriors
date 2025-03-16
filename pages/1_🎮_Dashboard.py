import streamlit as st

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="Dashboard - IMTasy Warriors",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"  # Afficher la barre latérale par défaut
)

# Masquer la page de connexion dans le menu de navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul li:first-child {
            display: none;
        }
        .summon-link:hover {
            background-color: #45a049 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

import plotly.graph_objects as go
import requests
from constants import *
from utils import display_player_stats, setup_navigation
import time

# Vérification de l'authentification avant tout
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("dashboard.py")

# Configuration de la navigation
setup_navigation()

# Réactiver la barre latérale une fois connecté
st.markdown("""
    <style>
        [data-testid="stSidebar"][aria-expanded="true"] {
            display: flex !important;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            display: flex !important;
        }
        .main {
            background-color: #1E1E1E;
        }
        .monster-card {
            background-color: #2E2E2E;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stat-container {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }
        .stat-label {
            color: #888;
        }
        .stat-value {
            color: #4CAF50;
            font-weight: bold;
        }
        .title-container {
            text-align: center;
            padding: 20px;
            background: linear-gradient(90deg, #1E1E1E, #2E2E2E, #1E1E1E);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        div[data-testid="stExpander"] {
            background-color: #2E2E2E;
            border-radius: 10px;
            border: 1px solid #4CAF50;
        }
        .monster-button {
            background-color: #2E2E2E;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 2px solid #4CAF50;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .monster-button:hover {
            background-color: #3E3E3E;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
        }
        /* Style pour les boutons de monstre */
        div.main div[data-testid="stButton"] > button {
            background-color: #2E2E2E !important;
            color: #4CAF50 !important;
            border: 2px solid #4CAF50 !important;
            border-radius: 10px !important;
            padding: 20px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            line-height: 1.5 !important;
            transition: all 0.3s ease !important;
            height: auto !important;
            white-space: pre-line !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        div.main div[data-testid="stButton"] > button:hover {
            background-color: #3E3E3E !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2) !important;
            border-color: #45a049 !important;
        }
        /* Style pour les boutons d'action (comme Améliorer la compétence) */
        div.main button.action-button {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 5px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            margin: 5px 0 !important;
            width: 100% !important;
        }
        div.main button.action-button:hover {
            background-color: #45a049 !important;
            transform: translateY(-2px) !important;
        }
        /* Style pour le bouton de suppression */
        div.main button.delete-button {
            background-color: #ff4444 !important;
            border: none !important;
            color: white !important;
        }
        div.main button.delete-button:hover {
            background-color: #ff3333 !important;
            box-shadow: 0 4px 8px rgba(255, 68, 68, 0.2) !important;
        }
        /* Style pour les boutons de monstre dans la zone principale */
        div.main div[data-testid="stButton"] button[kind="secondary"] {
            white-space: pre-wrap !important;
            min-height: 120px !important;
            padding: 20px !important;
            background: linear-gradient(145deg, #2E2E2E, #252525) !important;
            border: 2px solid #4CAF50 !important;
            border-radius: 15px !important;
            color: #4CAF50 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin: 8px 0 !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            text-align: center !important;
            line-height: 1.8 !important;
            width: 100% !important;
            font-size: 1.1em !important;
            font-weight: 500 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 8px !important;
        }
        div.main div[data-testid="stButton"] button[kind="secondary"]:hover {
            background: linear-gradient(145deg, #323232, #282828) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 12px rgba(76, 175, 80, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            border-color: #5CDB5C !important;
        }
        div.main div[data-testid="stButton"] button[kind="secondary"]:active {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        }
        /* Style pour les emojis dans les boutons */
        div.main div[data-testid="stButton"] button[kind="secondary"] span {
            font-size: 1.4em !important;
            margin-bottom: 4px !important;
        }
        /* Style spécifique pour les boutons de monstre */
        div[data-testid="stButton"] > button[data-testid*="monster_btn"] {
            height: auto !important;
            white-space: pre-line !important;
            padding: 1.5rem !important;
            background-color: #2E2E2E !important;
            border: 2px solid #4CAF50 !important;
            color: #4CAF50 !important;
            font-size: 16px !important;
            line-height: 1.6 !important;
            width: 100% !important;
            margin: 5px 0 !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stButton"] > button[data-testid*="monster_btn"]:hover {
            background-color: #3E3E3E !important;
            border-color: #5CDB5C !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="title-container">
        <h1 style='color: #4CAF50;'>Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

player_data = display_player_stats()

def display_monster_details(monster_id):
    try:
        response = requests.get(
            f"{MONSTERS_API_URL}/monsters/{monster_id}",
            headers={"Authorization": st.session_state["token"]}
        )
        if response.status_code == 200:
            monster = response.json()
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
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
                
                # Affichage du message pour les points de compétence disponibles
                if monster['skill_points'] > 0:
                    st.info(f"Vous avez {monster['skill_points']} points de compétence à utiliser!")
            
            with col2:
                # Graphique radar des statistiques
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=[monster['atk'], monster['def'], monster['vit'], monster['hp']],
                    theta=['ATK', 'DEF', 'VIT', 'HP'],
                    fill='toself',
                    name=monster['name'],
                    line_color='#4CAF50'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(monster['atk'], monster['def'], monster['vit'], monster['hp']) * 1.2]
                        )
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
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
                            if st.button(f"Améliorer la compétence (1 point)", key=f"skill_{monster_id}_{i}", type="primary"):
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

            # Ajout du bouton de suppression du monstre
            st.markdown("---")
            delete_container = st.container()
            
            # Initialiser les variables de session pour la suppression
            if "delete_confirmation" not in st.session_state:
                st.session_state.delete_confirmation = False
                st.session_state.monster_to_delete = None
            
            with delete_container:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col2:
                    if st.button("🗑️ Supprimer", key=f"delete_{monster_id}", type="secondary", help="Supprimer ce monstre de votre inventaire"):
                        print(f"[DEBUG] Bouton supprimer cliqué pour le monstre {monster_id}")
                        st.session_state.delete_confirmation = True
                        st.session_state.monster_to_delete = monster_id
                        st.rerun()
                
                if st.session_state.delete_confirmation and st.session_state.monster_to_delete == monster_id:
                    st.warning("Êtes-vous sûr de vouloir supprimer ce monstre ? Cette action est irréversible.")
                    confirm_col1, confirm_col2 = st.columns(2)
                    with confirm_col1:
                        if st.button("✔️ Confirmer", key=f"confirm_delete_{monster_id}", type="primary"):
                            print(f"[DEBUG] Confirmation de suppression pour le monstre {monster_id}")
                            try:
                                print(f"[DEBUG] Envoi de la requête DELETE à {MONSTERS_API_URL}/monsters/{monster_id}")
                                print(f"[DEBUG] Token utilisé : {st.session_state['token']}")
                                print(f"[DEBUG] Headers de la requête : {{'Authorization': {st.session_state['token']}}}")
                                
                                response = requests.delete(
                                    f"{MONSTERS_API_URL}/monsters/{monster_id}",
                                    headers={"Authorization": st.session_state["token"]}
                                )
                                
                                print(f"[DEBUG] Réponse de l'API : Status {response.status_code}")
                                print(f"[DEBUG] Contenu de la réponse : {response.text}")
                                print(f"[DEBUG] Headers de la réponse : {dict(response.headers)}")
                                
                                if response.status_code == 200:
                                    print("[DEBUG] Suppression réussie, mise à jour de l'interface")
                                    st.success("Monstre supprimé avec succès!")
                                    # Réinitialiser les variables de session
                                    st.session_state.delete_confirmation = False
                                    st.session_state.monster_to_delete = None
                                    if "selected_monster" in st.session_state:
                                        del st.session_state["selected_monster"]
                                    time.sleep(1)  # Petit délai pour assurer que le message est vu
                                    st.rerun()
                                else:
                                    print(f"[DEBUG] Échec de la suppression : {response.status_code} - {response.text}")
                                    st.error(f"Erreur lors de la suppression du monstre : {response.text}")
                            except Exception as e:
                                print(f"[DEBUG] Exception lors de la suppression : {str(e)}")
                                print(f"[DEBUG] Type d'exception : {type(e)}")
                                st.error(f"Une erreur est survenue : {str(e)}")
                    with confirm_col2:
                        if st.button("❌ Annuler", key=f"cancel_delete_{monster_id}", type="secondary"):
                            print(f"[DEBUG] Annulation de la suppression pour le monstre {monster_id}")
                            st.session_state.delete_confirmation = False
                            st.session_state.monster_to_delete = None
                            st.rerun()
        else:
            st.error("Erreur lors de la récupération des détails du monstre")
    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

if player_data:
    if not player_data["monsters"]:
        st.markdown("""
            <div style="text-align: center; padding: 40px; background: rgba(76, 175, 80, 0.1); border-radius: 10px; margin: 20px 0; border: 2px solid #4CAF50;">
                <h2 style="color: #4CAF50; margin-bottom: 20px;">✨ Votre collection de monstres est vide ! ✨</h2>
                <p style="color: #888; font-size: 1.2em; margin-bottom: 30px;">Commencez votre aventure en invoquant votre premier monstre !</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Centrer le bouton
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎲 Invoquer un monstre", use_container_width=True, type="primary"):
                st.switch_page("pages/2_🧙‍♂️_Invocation.py")
        st.stop()
    
    st.subheader("Vos Monstres")
    
    # Récupérer les détails de tous les monstres
    monsters_details = {}
    for monster_id in player_data["monsters"]:
        try:
            response = requests.get(
                f"{MONSTERS_API_URL}/monsters/{monster_id}",
                headers={"Authorization": st.session_state["token"]}
            )
            if response.status_code == 200:
                monster = response.json()
                monsters_details[monster_id] = monster
        except Exception as e:
            st.error(f"Erreur lors de la récupération des détails du monstre {monster_id}: {str(e)}")
    
    monster_cols = st.columns(3)
    for i, monster_id in enumerate(player_data["monsters"]):
        with monster_cols[i % 3]:
            monster = monsters_details.get(monster_id, {})
            if monster:
                container = st.container()
                with container:
                    # Utiliser des retours à la ligne explicites
                    button_text = f"""🎯 {monster['name']}

★ Niveau {monster['level']}

✨ {monster['monster_type']}"""
                    
                    if st.button(
                        button_text,
                        key=f"monster_btn_{monster_id}",
                        use_container_width=True
                    ):
                        st.session_state["selected_monster"] = monster_id
                        st.rerun()
            else:
                st.markdown(f"""
                    <div class="monster-button">
                        <h3 style='color: #888;'>Monstre {i+1}</h3>
                        <p style='color: #666;'>Non disponible</p>
                    </div>
                """, unsafe_allow_html=True)
                
    if "selected_monster" in st.session_state:
        st.markdown("---")
        display_monster_details(st.session_state["selected_monster"]) 