"""
schemav2.py
-----------
Schéma de validation des données d'entrée pour l'API de scoring CNSS.
 
Ce module définit le modèle Pydantic "InputData" utilisé pour valider
et typer les données envoyées manuellement à l'API (sans passage par Oracle).
 
Chaque champ correspond à une variable financière ou descriptive de l'entreprise
affiliée, couvrant les exercices 2022 et 2023.
"""
from pydantic import BaseModel

class InputData(BaseModel):
    """
    Modèle de données d'entrée pour la prédiction de scoring.
 
    Représente l'ensemble des variables nécessaires au modèle ML.
    Tous les champs numériques sont obligatoires et typés strictement.
 
    Attributs financiers (exercice 2022 et 2023) :
        - TOTAL_DEBIT          : Total des montants débités (cotisations dues)
        - TOTAL_CREDIT         : Total des montants crédités (paiements effectués)
        - MONTANT_IMPAYE       : Montant total des cotisations impayées
        - TOTAL_PENALITE       : Total des pénalités de retard appliquées
        - TAUX_RECOUVREMENT    : Taux de recouvrement des cotisations (en %)
        - TAUX_IMPAYE          : Taux d'impayés par rapport au total dû (en %)
        - NB_IMPAYE_3M         : Nombre de mois avec impayés sur une fenêtre de 3 mois
        - NB_IMPAYE_6M         : Nombre de mois avec impayés sur une fenêtre de 6 mois
        - NB_IMPAYE_12M        : Nombre de mois avec impayés sur une fenêtre de 12 mois
        - SALAIRE_AVG          : Masse salariale moyenne déclarée
 
    Attributs descriptifs de l'entreprise :
        - NB_IMMA              : Nombre d'immatriculations de salariés
        - AGE_ENTREPRISE       : Ancienneté de l'entreprise (en années)
        - SECTEUR_ID           : Code identifiant le secteur d'activité
        - REGION_ID            : Code identifiant la région géographique
        - VILLE_ID             : Code identifiant la ville du siège social
    """

    NUM_AFF: float

    TOTAL_DEBIT_2022: float
    TOTAL_DEBIT_2023: float

    TOTAL_CREDIT_2022: float
    TOTAL_CREDIT_2023: float

    MONTANT_IMPAYE_2022: float
    MONTANT_IMPAYE_2023: float

    TOTAL_PENALITE_2022: float
    TOTAL_PENALITE_2023: float

    TAUX_RECOUVREMENT_2022: float
    TAUX_RECOUVREMENT_2023: float

    TAUX_IMPAYE_2022: float
    TAUX_IMPAYE_2023: float

    NB_IMPAYE_3M_2022: float
    NB_IMPAYE_3M_2023: float

    NB_IMPAYE_6M_2022: float
    NB_IMPAYE_6M_2023: float

    NB_IMPAYE_12M_2022: float
    NB_IMPAYE_12M_2023: float

    SALAIRE_AVG_2022: float
    SALAIRE_AVG_2023: float

    NB_IMMA: float
    AGE_ENTREPRISE: float

    SECTEUR_ID: int
    REGION_ID: int
    VILLE_ID: int