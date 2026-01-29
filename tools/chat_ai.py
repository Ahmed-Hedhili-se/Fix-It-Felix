import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

load_dotenv(os.path.join(root_path, ".env"))

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

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

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        ai_message = response.choices[0].message.content
        print(f"\n🤖 IA : {ai_message}")

        messages.append({"role": "assistant", "content": ai_message})

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
