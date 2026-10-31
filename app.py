import streamlit as st
from groq import Groq

st.set_page_config(page_title="Coach SRL", page_icon="🧠", layout="centered")

# Connexion sécurisée
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Écran de connexion minimaliste
if not st.session_state.logged_in:
    st.title("🧠 Connexion Coach SRL")
    code = st.text_input("Code d'accès", type="password")
    if st.button("Entrer") and code == "COACH2026":
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# Interface de Chat
st.title("💬 Ton Coach d'Auto-Régulation")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Écris ton message ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # Appel direct et ultra-rapide sans fioritures
            history = [{"role": "system", "content": "Tu es un coach socratique bienveillant en autorégulation des apprentissages (SRL). Aide l'étudiant à réfléchir par lui-même."}] + st.session_state.messages
            
    stream = client.chat.completions.create(
                model="llama3-70b-8192", 
                messages=history,
                stream=True
            )
            
            ai_response = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error("Oups, un petit raté. Réessaie dans une petite seconde !")
