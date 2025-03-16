import streamlit as st
import requests
import plotly.graph_objects as go
from constants import *
import math  # Ajout de l'import math
import time  # Ajout de l'import time

def setup_navigation():
    """Configure la barre de navigation et le style commun pour toutes les pages."""
    # Masquer les éléments par défaut de Streamlit
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display: none;}
            .stToolbar {display: none;}
            [data-testid="stToolbar"] {display: none;}
            .stApp [data-testid="stToolbar"] {display: none;}
            div[data-testid="stDecoration"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    # Masquer la page de connexion dans le menu de navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] ul li:first-child {
                display: none;
            }
            .main {
                background-color: #1E1E1E;
            }
            /* Style spécifique pour le bouton de déconnexion */
            div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
                width: 100% !important;
                background-color: #2E2E2E !important;
                color: #ff4444 !important;
                border: 2px solid #ff4444 !important;
                padding: 10px !important;
                margin-top: 10px !important;
                height: 42px !important;
                font-size: 14px !important;
                line-height: 1 !important;
            }
            div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
                background-color: #3E3E3E !important;
                box-shadow: 0 4px 8px rgba(255, 68, 68, 0.2) !important;
                transform: translateY(-2px) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Ajouter le bouton de déconnexion en bas de la barre latérale
    with st.sidebar:
        if st.button("📤 Se déconnecter"):
            st.session_state.clear()
            st.switch_page("dashboard.py")

def display_player_stats():
    try:
        # Ajout d'une clé de session pour gérer le refresh
        if 'dashboard_loaded' not in st.session_state:
            st.session_state.dashboard_loaded = False
            time.sleep(1)  # Attendre 1 seconde
            st.rerun()  # Forcer le refresh de la page
        
        st.session_state.dashboard_loaded = True
        
        # Réappliquer le style du bouton de déconnexion après le refresh
        st.markdown("""
            <style>
                div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
                    width: 100% !important;
                    background-color: #2E2E2E !important;
                    color: #ff4444 !important;
                    border: 2px solid #ff4444 !important;
                    padding: 10px !important;
                    margin-top: 10px !important;
                    height: 42px !important;
                    font-size: 14px !important;
                    line-height: 1 !important;
                }
                div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
                    background-color: #3E3E3E !important;
                    box-shadow: 0 4px 8px rgba(255, 68, 68, 0.2) !important;
                    transform: translateY(-2px) !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        response = requests.get(
            f"{PLAYER_API_URL}/player",
            headers={"Authorization": st.session_state["token"]}
        )
        if response.status_code == 200:
            player_data = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Niveau", player_data["level"])
            with col2:
                st.metric("Monstres", f"{len(player_data['monsters'])}/{player_data['max_monsters']}")
                
            # Graphique d'expérience
            # Calcul de l'expérience nécessaire pour le niveau suivant
            exp_to_next_level = int(50 * math.pow(1.1, player_data["level"]))
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=player_data["experience"],
                domain={'x': [0.1, 0.9], 'y': [0.1, 0.9]},
                title={
                    'text': f"Progression d'expérience",
                    'font': {'color': '#4CAF50', 'size': 24},
                    'align': 'center'
                },
                number={
                    'font': {'color': '#4CAF50', 'size': 30},
                    'valueformat': ',d'
                },
                delta={'reference': exp_to_next_level, 'position': 'bottom'},
                gauge={
                    'axis': {'range': [0, exp_to_next_level], 'tickfont': {'color': '#4CAF50'}},
                    'bar': {'color': "#4CAF50"},
                    'bgcolor': "#2E2E2E",
                    'borderwidth': 2,
                    'bordercolor': "#4CAF50",
                    'threshold': {
                        'line': {'color': "#4CAF50", 'width': 2},
                        'thickness': 0.75,
                        'value': exp_to_next_level
                    }
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "#4CAF50"},
                height=400,
                margin=dict(t=120, b=80, l=40, r=40),
                autosize=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            return player_data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données du joueur : {str(e)}")
        return None

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
            
            return monster
    except Exception as e:
        st.error(f"Erreur lors de la récupération des détails du monstre : {str(e)}")
        return None 