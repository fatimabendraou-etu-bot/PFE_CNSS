from fastapi import FastAPI, HTTPException, UploadFile, File
import pandas as pd
import numpy as np
import oracledb
import joblib
from io import StringIO
import traceback

# =====================================================
# APP
# =====================================================
app = FastAPI(
    title="CNSS Scoring API",
    description="API de scoring du risque CNSS",
    version="3.0"
)

print("API STARTING ...")

# =====================================================
# LOAD MODELS
# =====================================================
try:
    model = joblib.load("loaddata/NoteBook/models_v2/model_v2.pkl")
    scaler = joblib.load("loaddata/NoteBook/models_v2/scaler_v2.pkl")
    features = joblib.load("loaddata/NoteBook/models_v2/features_v2.pkl")

    print("MODELS LOADED SUCCESSFULLY")

except Exception as e:
    print("MODEL LOADING ERROR :", e)
    raise e


# =====================================================
# DATABASE
# =====================================================
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


# =====================================================
# SEGMENTATION (based on PROBABILITY)
# =====================================================
def segmentation(p):

    if p < 0.05:
        return "NORMAL", "ACCEPTER", "AUCUNE"

    elif p < 0.15:
        return "SURVEILLANCE", "SURVEILLANCE", "SUIVI REGULIER"

    elif p < 0.40:
        return "RISQUE ÉLEVÉ", "SURVEILLANCE RENFORCÉE", "CONTROLE"

    else:
        return "RECOUVREMENT INTENSIF", "RECOUVREMENT", "ACTION URGENTE"


# =====================================================
# HOME
# =====================================================
@app.get("/")
def home():
    return {"message": "CNSS API OK"}


# =====================================================
# SINGLE PREDICTION
# =====================================================
@app.post("/predict")
def predict(num_aff: int):

    try:

        # =========================
        # GET DATA
        # =========================
        df = get_data(num_aff)

        if df.empty:
            raise HTTPException(status_code=404, detail="NUM_AFF introuvable")

        # =========================
        # CLEAN COLUMNS
        # =========================
        df.columns = df.columns.str.upper()

        # =========================
        # FEATURES ALIGNMENT (SAFE)
        # =========================
        X = df.reindex(columns=features)

        # fill missing columns safely
        for col in features:
            if col not in X.columns:
                X[col] = 0

        X = X[features]

        # numeric cleaning
        X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

        # =========================
        # SCALING
        # =========================
        X_scaled = scaler.transform(X)

        # =========================
        # PREDICTION
        # =========================
        p = model.predict_proba(X_scaled)[0, 1]

        # =========================
        # SCORE (RISK SCORE as requested)
        # =========================
        score = float(p * 1000)

        # =========================
        # SEGMENTATION
        # =========================
        segment, decision, action = segmentation(p)

        # =========================
        # BUSINESS METRICS
        # =========================
        gain_estime = float(1000 * (1 - p))
        risque_estime = float(5000 * p)

        # =========================
        # CLIENT INFO
        # =========================
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
            k: v
            for k, v in df.iloc[0].to_dict().items()
            if k.upper() not in exclude
        }

        # =========================
        # RESPONSE
        # =========================
        return {
            "NUM_AFF": int(df["NUM_AFF"].values[0]),
            "proba_defaut": round(float(p), 4),
            "score": score,
            "segment": segment,
            "decision": decision,
            "action": action,
            "gain_estime": round(gain_estime, 2),
            "risque_estime": round(risque_estime, 2),
            "client_info": client_info
        }

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# BATCH SCORING
# =====================================================
@app.post("/predict_batch")
async def predict_batch(file: UploadFile = File(...)):

    try:

        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        df.columns = df.columns.str.upper()

        # =========================
        # FEATURES SAFE ALIGNMENT
        # =========================
        X = df.reindex(columns=features)

        for col in features:
            if col not in X.columns:
                X[col] = 0

        X = X[features]
        X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

        # =========================
        # SCALE
        # =========================
        X_scaled = scaler.transform(X)

        # =========================
        # PREDICT
        # =========================
        proba = model.predict_proba(X_scaled)[:, 1]

        scores = (proba * 1000).astype(int)

        # =========================
        # RESULTS
        # =========================
        results = []

        for i in range(len(df)):

            p = proba[i]
            segment, decision, action = segmentation(p)

            results.append({
                "NUM_AFF": int(df.iloc[i]["NUM_AFF"]),
                "score": int(scores[i]),
                "proba_defaut": round(float(p), 4),
                "segment": segment,
                "decision": decision,
                "action": action
            })

        return results

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))