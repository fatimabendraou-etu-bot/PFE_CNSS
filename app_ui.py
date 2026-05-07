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
# SIDEBAR
# =========================
st.sidebar.header("Recherche affilié")

num_aff = st.sidebar.number_input("NUM_AFF", min_value=1, step=1)

run = st.sidebar.button("Lancer le scoring")

st.sidebar.divider()

st.sidebar.header("Scoring CSV")
uploaded_file = st.sidebar.file_uploader("Importer fichier CSV", type=["csv"])
run_batch = st.sidebar.button("Scoring fichier")

# =========================
# SCORING INDIVIDUEL
# =========================
if run:

    url = f"http://127.0.0.1:8000/predict?num_aff={num_aff}"
    response = requests.post(url)

    if response.status_code == 200:

        data = response.json()

        risk = data["proba_defaut"]   # p = risque
        score = data["score"]         # p * 1000

        # =========================
        # KPI
        # =========================
        st.subheader("Indicateurs principaux")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Score Risque", round(score, 2))
        col2.metric("Risque (%)", f"{risk:.2%}")
        col3.metric("Segment", data["segment"])
        col4.metric("Action", data["action"])

        st.caption("⚠ Score = niveau de risque (plus élevé = plus risqué)")

        st.divider()

        # =========================
        # GAUGE
        # =========================
        st.subheader("Niveau de risque")

        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk * 100,
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
        # PIE CHART
        # =========================
        st.subheader("Répartition du risque")

        df_risk = pd.DataFrame({
            "Categorie": ["Non Risque", "Risque"],
            "Valeur": [1 - risk, risk]
        })

        fig2 = px.pie(df_risk, names="Categorie", values="Valeur", hole=0.5)
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # =========================
        # KPI BAR
        # =========================
        st.subheader("Indicateurs clés")

        df_kpi = pd.DataFrame({
            "Indicateur": ["Score", "Risque (%)", "Gain", "Risque Coût"],
            "Valeur": [
                score,
                risk * 100,
                data["gain_estime"],
                data["risque_estime"]
            ]
        })

        fig3 = px.bar(df_kpi, x="Indicateur", y="Valeur", text="Valeur")
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

        region = data["client_info"].get("LIBELLE_REGION", "Inconnu")

        region_df = pd.DataFrame([{
            "region": region,
            "risk": risk * 100
        }])

        fig4 = px.bar(region_df, x="region", y="risk", text="risk")
        st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # =========================
        # SYNTHÈSE CLIENT
        # =========================
        st.subheader("Synthèse client")

        client = data["client_info"]

        col1, col2, col3 = st.columns(3)

        col1.markdown("### Identification")
        col1.write(f"NUM AFF : {client.get('NUM_AFF', '')}")
        col1.write(f"Région : {client.get('LIBELLE_REGION', '')}")
        col1.write(f"Ville : {client.get('LIBELLE_VILLE', '')}")
        col1.write(f"Secteur : {client.get('LIBELLE_SECTEUR', '')}")

        col2.markdown("### Risque")
        col2.write(f"Taux impayé : {client.get('2023_TAUX_IMPAYE', 0)}")
        col2.write(f"Impayés 12M : {client.get('2023_NB_IMPAYE_12M', 0)}")
        col2.write(f"Recouvrement : {client.get('2023_TAUX_RECOUVREMENT', 0)}")

        col3.markdown("### Finance")
        col3.write(f"Débit : {client.get('2023_TOTAL_DEBIT', 0)}")
        col3.write(f"Crédit : {client.get('2023_TOTAL_CREDIT', 0)}")
        col3.write(f"Impayé : {client.get('2023_MONTANT_IMPAYE', 0)}")
        col3.write(f"Salaire : {client.get('2023_SALAIRE_AVG', 0)}")

    else:
        st.error("Erreur API CNSS")


# =========================
# SCORING BATCH
# =========================
if run_batch and uploaded_file is not None:

    st.subheader("Résultats scoring fichier CSV")

    df_upload = pd.read_csv(uploaded_file)

    results = []
    progress = st.progress(0)

    for i, row in df_upload.iterrows():

        try:
            num_aff_csv = row["NUM_AFF"]

            url = f"http://127.0.0.1:8000/predict?num_aff={num_aff_csv}"
            response = requests.post(url)

            if response.status_code == 200:

                data = response.json()

                results.append({
                    "NUM_AFF": num_aff_csv,
                    "Score Risque": data["score"],
                    "Risque (%)": round(data["proba_defaut"] * 100, 2),
                    "Segment": data["segment"],
                    "Décision": data["decision"],
                    "Action": data["action"]
                })

        except Exception:
            st.warning(f"Erreur NUM_AFF {num_aff_csv}")

        progress.progress((i + 1) / len(df_upload))

    result_df = pd.DataFrame(results)

    st.dataframe(result_df, use_container_width=True)

    st.subheader("Distribution des segments")

    fig_batch = px.histogram(result_df, x="Segment")
    st.plotly_chart(fig_batch, use_container_width=True)

    csv = result_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Télécharger résultats CSV",
        data=csv,
        file_name="cnss_scoring_results.csv",
        mime="text/csv"
    )