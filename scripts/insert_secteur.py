import oracledb
import pandas as pd

conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()

df = pd.read_csv("C:/Users/fatimazahra/Downloads/output (1)/output/SECTEUR.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO SECTEUR (SECTEUR_ID, LIBELLE_SECTEUR)
        VALUES (:1, :2)
    """, (
        int(row['secteur_id']),
        row['libelle_secteur']
    ))

conn.commit()
cursor.close()
conn.close()

print("SECTEUR chargé ")