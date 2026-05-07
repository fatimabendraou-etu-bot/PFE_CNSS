# Modélisation prédictive et scoring du risque de défaut des cotisations sociales  
## Système d’aide à la décision pour l’optimisation du recouvrement (Cas CNSS)

---

# 1. Contexte et objectif

Ce projet consiste à développer un système de scoring prédictif permettant d’évaluer le risque de défaut de paiement des cotisations sociales.

Objectifs :
- Identifier les affiliés à risque  
- Optimiser les actions de recouvrement  
- Automatiser la prise de décision  
- Déployer un système complet basé sur le Machine Learning  

---

# 2. Structure du projet


```
CNSS-SCORING/

├── apiv2/
│   ├── mainv2.py
│   ├── schemav2.py
│
├── notebooks/
│   ├── modelisation.ipynb
│   ├── scoring.ipynb
│
├── sql/
│   ├── mld.sql
│   ├── features.sql
│   ├── dataset_final.sql
│
├── models_v2/
│   ├── model_v2.pkl
│   ├── scaler_v2.pkl
│   ├── features_v2.pkl
│
├── script/
│   ├── insert_aff.py
│   ├── insert_imma.py
│   ├── insert_pay.py
│
├── app_ui.py
└── README.md
```

---

# 3. Données

Les données sont synthétiques, générées avec Faker et enrichies par des règles SQL afin de simuler un comportement proche des données CNSS.

Sources :
- AFFILIE  
- TRANSACTIONS  
- DATASET FINAL (2022 / 2023)

---

# 4. Variable cible

TARGET_FLAG_CLEAN (classification binaire)

- 0 : affilié bon payeur  
- 1 : affilié à risque  

---

# 5. Prétraitement

- Nettoyage des données  
- Encodage des variables catégorielles  
- Normalisation / standardisation  
- Feature engineering (SQL + Python)  
- Gestion du déséquilibre des classes  
- Séparation train / test  

---

# 6. Modèles utilisés

- Logistic Regression  
- Random Forest  
- XGBoost (modèle final optimisé)  

---

# 7. Résultats des modèles

## Tableau comparatif

| Modèle              | AUC     | Gini    | Accuracy | F1 (classe 1) | Recall (classe 1) |
|---------------------|--------|--------|----------|---------------|------------------|
| XGBoost (optimized) | 0.9782 | 0.9563 | 0.95     | 0.74          | 0.87             |
| Random Forest       | 0.9783 | 0.9566 | 0.95     | 0.72          | 0.71             |
| Logistic Regression | 0.9744 | 0.9488 | 0.95     | 0.68          | 0.64             |

---

# 8. Matrices de confusion

## XGBoost

|           | Pred 0 | Pred 1 |
|----------|--------|--------|
| Actual 0 | 19859  | 963    |
| Actual 1 | 261    | 1751   |

---

## Random Forest

|           | Pred 0 | Pred 1 |
|----------|--------|--------|
| Actual 0 | 20267  | 555    |
| Actual 1 | 575    | 1437   |

---

## Logistic Regression

|           | Pred 0 | Pred 1 |
|----------|--------|--------|
| Actual 0 | 20307  | 515    |
| Actual 1 | 717    | 1295   |

---

# 9. Optimisation du seuil (XGBoost)

Seuil optimal : 0.8182  

| Métrique   | Valeur |
|------------|--------|
| Precision  | 0.65   |
| Recall     | 0.87   |
| F1-score   | 0.74   |
| AUC        | 0.978  |

---

# 10. API FastAPI (apiv2)

Endpoint :
POST /predict?num_aff=ID

Fonctionnalités :
- Chargement du modèle ML  
- Récupération des données client  
- Calcul du score de risque  
- Segmentation du risque  
- Recommandation d’action  

Exemple réponse :

```json
{
  "proba_defaut": 0.83,
  "score": 720,
  "risque_estime": 15000,
  "segment": "HIGH RISK",
  "action": "Recovery priority",
  "decision": "Follow-up required",
  "client_info": {
    "NUM_AFF": 2001,
    "TOTAL_DEBIT_2023": 50000,
    "TOTAL_IMPAYE_2023": 12000
  }
}
```

---

# 11. Interface Streamlit

Fonctionnalités :
- Saisie NUM_AFF  
- Appel API FastAPI  
- Affichage KPIs :
  - Probabilité de défaut  
  - Score de risque  
  - Risque estimé  

- Décision :
  - Segment  
  - Action  
  - Décision finale  

- Visualisations :
  - Score de risque  
  - Répartition du risque  
  - Évolution des impayés (2022 vs 2023)  

---

# 12. SQL Scripts

- Insertion des affiliés  
- Insertion des transactions  
- Feature engineering  
- Agrégation 2022 / 2023  
- Préparation dataset ML  

---

# 13. Modèles sauvegardés

- model_v2.pkl  
- scaler_v2.pkl  
- features_v2.pkl  

Utilisés directement par l’API pour la prédiction.

---

# 14. Pipeline global

SQL → Feature Engineering → Dataset → ML Models → Evaluation → Saving → FastAPI → Streamlit

---

# 15. Conclusion

Le projet met en place un système complet de scoring CNSS basé sur le Machine Learning.

Résultats :
- XGBoost optimisé retenu  
- AUC ≈ 0.98  
- Bonne détection des affiliés à risque  
- Système end-to-end (Data → ML → API → UI)  

Ce système améliore la prise de décision et optimise les stratégies de recouvrement.
