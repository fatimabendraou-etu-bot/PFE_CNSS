import oracledb
import pandas as pd

conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()

df = pd.read_csv("C:/Users/fatimazahra/Downloads/output (1)/output/VILLE.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO VILLE (VILLE_ID, LIBELLE_VILLE, REGION_ID)
        VALUES (:1, :2, :3)
    """, (
        int(row['ville_id']),
        row['libelle_ville'],
        int(row['region_id'])
    ))

conn.commit()
cursor.close()
conn.close()

print("VILLE chargée ")
