# IMTasy Warriors 🎮⚔️

Un jeu de combat de monstres inspiré des classiques du genre, développé pendant le cours Web API.

## De quoi s'agit-il? 

IMTasy Warriors est un jeu où tu peux invoquer, collectionner et faire combattre des monstres dans des batailles épiques. Chaque monstre possède des stats et des capacités uniques qui déterminent sa puissance en combat.

## Comment lancer le jeu?

### Option 1: Docker (recommandée)

La façon la plus simple de jouer:

```bash
# Clone le repo
git clone https://github.com/JoshuaDsDl/IMTasy-Warriors.git
cd IMTasy-Warriors

# Lance tout le projet avec Docker Compose
docker-compose up -d
```

Puis ouvre simplement [http://localhost:8501](http://localhost:8501) dans ton navigateur!

### Option 2: Lancement manuel

Si tu préfères la méthode manuelle:

1. Assure-toi d'avoir Python 3.8+ installé
2. Installe les dépendances:
   ```bash
   pip install -r requirements.txt
   ```
3. Lance les API (il faut un MongoDB sur chaque):
   ```bash
   cd AuthAPI && python main.py
   cd PlayerAPI && python main.py
   cd MonstersAPI && python main.py
   cd SummonAPI && python main.py
   cd BattleAPI && python main.py
   ```
4. Lance l'interface web:
   ```bash
   streamlit run dashboard.py
   ```

## Fonctionnalités principales

🔐 **Authentification** - Crée un compte et connecte-toi au jeu  
📊 **Dashboard** - Visualise tes stats et celles de tes monstres  
🧙 **Invocation** - Obtiens de nouveaux monstres aléatoirement  
⚔️ **Combat** - Fais s'affronter tes monstres dans l'arène  

## Quelques astuces

- Les monstres rares (3+ étoiles) sont beaucoup plus puissants
- L'expérience gagnée dépend de la différence de niveau entre les monstres
- Plus tu joues, plus tu débloques de contenu

## Architecture du projet

Le jeu est construit autour d'une architecture microservices:

- **AuthAPI** (port 5000): Gestion des utilisateurs
- **PlayerAPI** (port 5001): Profils et stats des joueurs  
- **MonstersAPI** (port 5002): Données et stats des monstres
- **SummonAPI** (port 5003): Système d'invocation
- **BattleAPI** (port 5004): Système de combat
- **WebServer** (port 8501): Interface utilisateur Streamlit

## Développé par

Joshua DESCHIETERE, étudiant à l'IMT pour le cours Web API, promo 2024-2025. 