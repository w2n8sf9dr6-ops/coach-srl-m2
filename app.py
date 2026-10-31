import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Coach SRL - Master 2", page_icon="🧠", layout="centered")

# Connexion Groq 100% gratuite
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Connexion rapide
if not st.session_state.logged_in:
    st.title("🧠 Connexion Coach SRL")
    with st.form("login"):
        email = st.text_input("E-mail")
        code = st.text_input("Code", type="password")
        if st.form_submit_button("Entrer") and code == "COACH2026":
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# Chat Tuteur IA
st.markdown("### Ton Coach d'Auto-Régulation")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Écris ton message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # Construction de l'historique pour Groq
            messages_history = [
                {"role": "system", "content": "Tu es un coach expert en autorégulation des apprentissages (SRL) pour adultes. Pose des questions socratiques, aide à découper les tâches sans donner les réponses directes."}
            ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_history,
                stream=True,
            )
            
            ai_response = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error(f"Erreur : {e}")
