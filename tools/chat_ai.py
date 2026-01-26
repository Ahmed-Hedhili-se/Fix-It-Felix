import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Ajouter le dossier parent au système pour trouver le dossier 'src'
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

# Charger le .env depuis la racine
load_dotenv(os.path.join(root_path, ".env"))

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

# Initialisation de l'historique des messages
messages = [
    {"role": "system", "content": "Tu es un assistant utile et poli."}
]

print("💬 Chat AI démarré (tapez 'exit' ou 'quit' pour quitter)")

while True:
    user_input = input("\n👤 Vous : ")
    
    if user_input.lower() in ["exit", "quit"]:
        print("Fin de la session. Au revoir !")
        break
        
    if not user_input.strip():
        continue

    # Ajouter le message de l'utilisateur à l'historique
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        ai_message = response.choices[0].message.content
        print(f"\n🤖 IA : {ai_message}")

        # Ajouter la réponse de l'IA à l'historique pour maintenir le contexte
        messages.append({"role": "assistant", "content": ai_message})
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
