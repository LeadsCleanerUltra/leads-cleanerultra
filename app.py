import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="LeadsCleaner Ultra", page_icon="🛡️", layout="wide")

# --- 1. SÉCURITÉ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

VALID_CODES = {"ESSAI-48H": "Trial", "CLE-PRO-2026": "Paid"}
# --- RÉCEPTION DE LA CLÉ APRÈS PAIEMENT ---
if st.query_params.get("payment") == "success":
    st.balloons()
    st.success("✅ Paiement validé ! Bienvenue.")
    st.info("Voici votre clé d'accès à copier ci-contre :")
    st.code("CLE-PRO-2026", language="text")
    st.divider()
if not st.session_state.auth:
    st.title("🚀 LeadsCleaner Ultra Pro")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("### 🔑 Accès & Essai")
        st.write("Le code d'accès est envoyé après paiement ou sur demande.")
        st.link_button("💳 S'ABONNER MAINTENANT", "https://buy.stripe.com/28E3cv4Kj5vD8LWgdyc3m00", use_container_width=True)
    with col_b:
        st.success("### 🔓 Connexion")
        pwd = st.text_input("Code d'accès", type="password")
        if st.button("Lancer l'application", use_container_width=True):
            if pwd in VALID_CODES:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Code erroné.")
    st.stop()

# --- 2. FONCTIONS AVANCÉES ---

def clean_radical(text):
    if pd.isna(text): return ""
    text = str(text)
    try: text = text.encode('latin-1').decode('utf-8')
    except: pass
    parasites = [r'\bS\.?A\.?\b', r'\bSAS\b', r'\bSARL\b', r'\bLTD\b', r'\bREP PAR\b', r'\bSIÈGE\b']
    for p in parasites: text = re.sub(p, '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', ' ', text)
    return " ".join(text.strip().title().split())

def analyze_email(email):
    if pd.isna(email) or "@" not in str(email): return "Invalide", ""
    email = str(email).lower().strip()
    domain = email.split('@')[-1]
    is_pro = "Pro" if domain not in ['gmail.com', 'outlook.fr', 'hotmail.com', 'yahoo.fr', 'orange.fr'] else "Perso"
    return is_pro, domain

def calculate_score(row):
    score = 0
    if len(str(row.get('Dénomination', ''))) > 2: score += 1
    if "@" in str(row.get('Email', '')): score += 1
    if len(str(row.get('Adresse', ''))) > 10: score += 1
    return "⭐" * score if score > 0 else "🌑"

# --- 3. INTERFACE ---
st.title("🛡️ LeadsCleaner Ultra Pro")
uploaded_file = st.file_uploader("Importer votre fichier CSV", type="csv")

if uploaded_file:
    try:
        content = uploaded_file.read()
        try: df = pd.read_csv(BytesIO(content), sep=None, engine='python', encoding='utf-8')
        except: df = pd.read_csv(BytesIO(content), sep=None, engine='python', encoding='latin-1')
        
        cols = df.columns.tolist()
        
        with st.sidebar:
            st.header("⚙️ Options Premium")
            col_to_clean = st.multiselect("Colonnes à nettoyer (Nom/Société)", cols)
            email_col = st.selectbox("Colonne Email (Optionnel)", ["Aucune"] + cols)
            activate_scoring = st.checkbox("Activer le Scoring Qualité ⭐")
            crm_format = st.selectbox("Format d'export", ["Standard CSV", "Format HubSpot", "Format Salesforce"])

        if st.button("🚀 TRAITER LE FICHIER", use_container_width=True):
            # 1. Nettoyage
            for c in col_to_clean:
                df[c] = df[c].apply(clean_radical)
            
            # 2. Analyse Email
            if email_col != "Aucune":
                df[['Type Email', 'Domaine Web']] = df[email_col].apply(lambda x: pd.Series(analyze_email(x)))
            
            # 3. Scoring
            if activate_scoring:
                df['Score Qualité'] = df.apply(calculate_score, axis=1)
            
            st.success("Traitement terminé avec succès !")
            st.dataframe(df.head(20))

            # 4. Export
            sep = ',' if "HubSpot" in crm_format else ';'
            output = BytesIO()
            df.to_csv(output, index=False, sep=sep, encoding='utf-8-sig')
            
            st.download_button(f"📥 TÉLÉCHARGER ({crm_format})", output.getvalue(), "leads_premium.csv", "text/csv", use_container_width=True)
            
    except Exception as e:

        st.error(f"Erreur : {e}")

