import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================
# CONFIGURATION
# =========================
st.set_page_config(
    page_title="CNSS Risk Dashboard",
    layout="wide"
)

st.title("CNSS Risk Scoring Dashboard")

st.markdown("Système de scoring du risque de défaut des cotisations sociales CNSS.")

# =========================
# INPUT
# =========================
st.sidebar.header("Recherche affilié")

num_aff = st.sidebar.number_input("NUM_AFF", min_value=1, step=1)

run = st.sidebar.button("Lancer le scoring")

# =========================
# API
# =========================
if run:

    url = f"http://127.0.0.1:8000/predict?num_aff={num_aff}"
    response = requests.post(url)

    if response.status_code == 200:

        data = response.json()
        proba = data["proba_defaut"]

        # =========================
        # KPI
        # =========================
        st.subheader("Indicateurs principaux")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Score", data["score"])
        col2.metric("Probabilité défaut", f"{proba:.2%}")
        col3.metric("Segment", data["segment"])
        col4.metric("Action", data["action"])

        st.divider()

        # =========================
        # ANALYSE RISQUE (GAUGE)
        # =========================
        st.subheader("Niveau de risque")

        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=proba * 100,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkred"},
                "steps": [
                    {"range": [0, 15], "color": "green"},
                    {"range": [15, 40], "color": "orange"},
                    {"range": [40, 100], "color": "red"}
                ]
            }
        ))

        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # =========================
        # RISQUE VS NON RISQUE
        # =========================
        st.subheader("Répartition du risque")

        df_risk = pd.DataFrame({
            "Categorie": ["Non Risque", "Risque"],
            "Valeur": [1 - proba, proba]
        })

        fig2 = px.pie(
            df_risk,
            names="Categorie",
            values="Valeur",
            hole=0.5
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # =========================
        # KPI COMPARATIFS
        # =========================
        st.subheader("Indicateurs clés")

        df_kpi = pd.DataFrame({
            "Indicateur": ["Score", "Proba (%)", "Gain", "Risque"],
            "Valeur": [
                data["score"],
                proba * 100,
                data["gain_estime"],
                data["risque_estime"]
            ]
        })

        fig3 = px.bar(
            df_kpi,
            x="Indicateur",
            y="Valeur",
            text="Valeur"
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # =========================
        # DECISION
        # =========================
        st.subheader("Décision métier CNSS")

        st.success(f"Segment : {data['segment']}")
        st.info(f"Décision : {data['decision']}")
        st.warning(f"Action : {data['action']}")

        st.divider()

        # =========================
        # REGION
        # =========================
        st.subheader("Risque par région")

        region_df = pd.DataFrame([{
            "region": data["client_info"]["LIBELLE_REGION"],
            "risk": proba * 100
        }])

        fig4 = px.bar(
            region_df,
            x="region",
            y="risk",
            text="risk"
        )

        st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # =========================
        # SYNTHÈSE CLIENT (SANS JSON)
        # =========================
        st.subheader("Synthèse client")

        client = data["client_info"]

        col1, col2, col3 = st.columns(3)

        col1.markdown("Identification")
        col1.write(f"NUM AFF : {client['NUM_AFF']}")
        col1.write(f"Région : {client['LIBELLE_REGION']}")
        col1.write(f"Ville : {client['LIBELLE_VILLE']}")
        col1.write(f"Secteur : {client['LIBELLE_SECTEUR']}")

        col2.markdown("Risque")
        col2.write(f"Taux impayé 2023 : {client['2023_TAUX_IMPAYE']:.2%}")
        col2.write(f"Impayés 12M : {client['2023_NB_IMPAYE_12M']}")
        col2.write(f"Recouvrement : {client['2023_TAUX_RECOUVREMENT']:.2%}")

        col3.markdown("Finance")
        col3.write(f"Débit 2023 : {client['2023_TOTAL_DEBIT']}")
        col3.write(f"Crédit 2023 : {client['2023_TOTAL_CREDIT']}")
        col3.write(f"Impayé : {client['2023_MONTANT_IMPAYE']}")
        col3.write(f"Salaire : {client['2023_SALAIRE_AVG']}")

    else:
        st.error("Erreur API CNSS")