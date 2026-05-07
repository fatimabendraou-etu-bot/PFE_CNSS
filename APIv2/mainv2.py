from fastapi import FastAPI, HTTPException
import pandas as pd
import oracledb
import joblib

# =====================
# APP INIT
# =====================
app = FastAPI(
    title="CNSS Scoring API",
    description="API de scoring de risque pour les affiliés CNSS",
    version="2.1"
)

# =====================
# LOAD MODELS
# =====================
model = joblib.load("loaddata/NoteBook/models_v2/model_v2.pkl")
scaler = joblib.load("loaddata/NoteBook/models_v2/scaler_v2.pkl")
features = joblib.load("loaddata/NoteBook/models_v2/features_v2.pkl")

# =====================
# DB FUNCTION
# =====================
def get_data(num_aff: int):

    conn = oracledb.connect(
        user="pfe",
        password="pfe",
        dsn="localhost:1521/XEPDB1"
    )

    query = """
    SELECT *
    FROM dataset_final1
    WHERE NUM_AFF = :num_aff
    """

    df = pd.read_sql(query, conn, params={"num_aff": num_aff})
    conn.close()

    return df

# =====================
# HOME
# =====================
@app.get("/")
def home():
    return {"message": "CNSS Scoring API OK"}

# =====================
# PREDICT
# =====================
@app.post("/predict")
def predict(num_aff: int):

    try:
        # =====================
        # 1. DATA
        # =====================
        df = get_data(num_aff)

        if df.empty:
            raise HTTPException(status_code=404, detail="NUM_AFF introuvable")

        df.columns = [c.upper() for c in df.columns]

        # =====================
        # 2. FEATURES ALIGNMENT
        # =====================
        X = df.reindex(columns=features).copy()

        if X.isnull().all().any():
            raise Exception("Feature mismatch detected")

        X = X.fillna(0)

        # =====================
        # 3. SCALING
        # =====================
        X_scaled = scaler.transform(X)

        # =====================
        # 4. PREDICTION
        # =====================
        p = model.predict_proba(X_scaled)[0, 1]

        # =====================
        # 5. SEGMENTATION
        # =====================
        if p < 0.05:
            segment = "NORMAL"
            decision = "ACCEPTER"
            action = "AUCUNE"
        elif p < 0.15:
            segment = "SURVEILLANCE"
            decision = "SURVEILLANCE"
            action = "SUIVI REGULIER"
        elif p < 0.40:
            segment = "RISQUE ÉLEVÉ"
            decision = "SURVEILLANCE RENFORCÉE"
            action = "CONTROLE"
        else:
            segment = "RECOUVREMENT INTENSIF"
            decision = "RECOUVREMENT"
            action = "ACTION URGENTE"
        
        # =====================
        # 6. METRICS
        # =====================
        gain_estime = 1000 * (1 - p)
        risque_estime = 5000 * p

        # =====================
        # 7. CLIENT INFO
        # =====================
        exclude = [
            "TARGET_FLAG_CLEAN",
            "TARGET_RECOUVREMENT",
            "TARGET_POURCENTAGE_IMPAYE",
            "TARGET_POURCENTAGE_NEW1",
            "TARGET_RECOUVREMENT_NEW1",
            "FLAG_GLOBAL",
            "TARGET_RECOUVREMENT_NEW2"
        ]

        client_info = {
            k: v for k, v in df.iloc[0].to_dict().items()
            if k not in exclude
        }

        # =====================
        # RESPONSE
        # =====================
        return {
     "NUM_AFF": int(df["NUM_AFF"].values[0]),
    "proba_defaut": float(round(p, 4)),
    "score": int(p * 1000),
    "segment": str(segment),
    "decision": str(decision),
    "action": str(action),
    "gain_estime": float(round(gain_estime, 2)),
    "risque_estime": float(round(risque_estime, 2)),
    "client_info": client_info
}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))