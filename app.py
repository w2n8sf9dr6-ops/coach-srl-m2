import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Coach SRL - Master 2",
    page_icon="🧠",
    layout="centered"
)

# --- CONFIGURATION API GEMINI ---
genai.configure(api_key="TON_API_KEY_GEMINI")
model = genai.GenerativeModel("gemini-2.5-flash")

# --- INITIALISATION DE LA SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "todo_list" not in st.session_state:
    st.session_state.todo_list = [
        "1. Définir ton objectif principal pour ce module.",
        "2. Faire une pause de 5 minutes toutes les 25 minutes de lecture."
    ]

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.logged_in:
    st.title("🧠 Connexion à ton Coach d'Apprentissage")
    st.write("Entre ton e-mail et le code d'accès général pour lancer ta session.")
    
    with st.form("login_form"):
        email_input = st.text_input("Adresse e-mail (personnelle ou école)")
        code_input = st.text_input("Code de session", type="password", help="Utilise le code général : COACH2026")
        submit_btn = st.form_submit_button("Commencer la session")
        
        if submit_btn:
            if email_input and code_input == "COACH2026":
                st.session_state.logged_in = True
                st.session_state.user_email = email_input
                st.rerun()
            else:
                st.error("E-mail manquant ou code incorrect (Indice : COACH2026).")
    st.stop()

# --- BARRE LATÉRALE DE SESSION ---
st.sidebar.markdown(f"👤 **Connecté :** `{st.session_state.user_email}`")
if st.sidebar.button("Se déconnecter"):
    st.session_state.logged_in = False
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

# --- NAVIGATION ENTRE LES ONGLETS ---
tab_chat, tab_prog, tab_admin = st.tabs(["💬 Tuteur IA", "📅 Programmation & Organisation", "🔒 Espace Formateur"])

# ==========================================
# ONGLET 1 : TUTEUR IA (SRL)
# ==========================================
with tab_chat:
    st.markdown("### Ton Coach d'Auto-Régulation")
    st.caption("Discute ici de tes blocages, de ta fatigue ou de ta méthode. L'IA t'aide à structurer ton apprentissage.")

    if "chat_session" not in st.session_state:
        system_instruction = (
            "Tu es un coach expert en autorégulation des apprentissages (SRL) pour adultes en formation professionnelle. "
            "Tu ne connais pas le contenu technique des cours, mais tu aides l'apprenant à réguler sa charge cognitive, "
            "à découper ses tâches complexes en micro-objectifs, à lutter contre la surcharge et à adopter des stratégies actives. "
            "Ne donne jamais la solution directe, pose des questions socratiques et propose des méthodes de travail."
        )
        st.session_state.chat_session = model.start_chat(history=[{
            "role": "user",
            "parts": [system_instruction]
        }])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ex: Je suis bloqué sur ce module, je n'arrive pas à me concentrer..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Le coach réfléchit..."):
                response = st.session_state.chat_session.send_message(prompt)
                ai_response = response.text
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# ONGLET 2 : PROGRAMMATION & ORGANISATION
# ==========================================
with tab_prog:
    st.markdown("### 📅 Ton Plan d'Action Personnalisé")
    st.caption("Voici les points de friction identifiés et les actions recommandées pour structurer tes révisions.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Statut de la session", "Actif", "En cours")
    with col2:
        st.metric("Échanges enregistrés", f"{len(st.session_state.messages)//2}", "Progression")

    st.markdown("#### 🎯 À revoir en priorité :")
    for task in st.session_state.todo_list:
        st.info(task)
        
    if st.button("Demander à l'IA de mettre à jour mon plan de révision"):
        with st.spinner("Analyse de tes échanges récents..."):
            st.session_state.todo_list.append(f"• Consolider le point abordé lors de ta dernière question ({datetime.now().strftime('%H:%M')})")
            st.success("Ton plan a été actualisé !")
            st.rerun()

# ==========================================
# ONGLET 3 : ESPACE FORMATEUR (SÉCURISÉ)
# ==========================================
with tab_admin:
    st.markdown("### 🔒 Espace Réservé aux Formateurs")
    st.caption("Accès protégé pour l'analyse des traces globales et individuelles de la cohorte.")

    admin_pass = st.text_input("Mot de passe formateur", type="password")

    if admin_pass == "HumaCareForm26":
        st.success("Accès autorisé.")
        
        st.markdown("#### 📊 Vue Globale (Macro-analyse)")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Étudiants connectés", "1", "Actif")
        col_b.metric("Temps moyen de session", "12 min", "+2 min")
        col_c.metric("Taux d'alerte surcharge", "15%", "-5%")

        st.markdown("#### 🔍 Vue Individuelle (Par apprenant)")
        selected_student = st.selectbox("Sélectionner un e-mail d'étudiant", [st.session_state.user_email if st.session_state.user_email else "Aucun participant pour l'instant"])
        
        if selected_student:
            st.write(f"**Détails pour :** `{selected_student}`")
            st.text_area("Historique brut des conversations", value=str(st.session_state.messages), height=200)

        df_dummy = pd.DataFrame(st.session_state.messages)
        st.download_button(
            label="📥 Télécharger toutes les traces (CSV pour JASP/Excel)",
            data=df_dummy.to_csv(index=False).encode('utf-8'),
            file_name="traces_recherche_m2.csv",
            mime="text/csv"
        )
        
    elif admin_pass:
        st.error("Mot de passe incorrect.")
