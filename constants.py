# URLs des API
import os

# Récupération des URLs depuis les variables d'environnement (avec fallback aux valeurs locales)
AUTH_API_URL = os.environ.get("AUTH_API_URL", "http://localhost:5000")
PLAYER_API_URL = os.environ.get("PLAYER_API_URL", "http://localhost:5001")
MONSTERS_API_URL = os.environ.get("MONSTERS_API_URL", "http://localhost:5002")
SUMMON_API_URL = os.environ.get("SUMMON_API_URL", "http://localhost:5003")
BATTLE_API_URL = os.environ.get("BATTLE_API_URL", "http://localhost:5004") 