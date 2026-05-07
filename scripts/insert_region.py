import oracledb
import pandas as pd

conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()

df = pd.read_csv("C:/Users/fatimazahra/Downloads/output (1)/output/REGION.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO REGION (REGION_ID, LIBELLE_REGION)
        VALUES (:1, :2)
    """, (
        int(row['region_id']),
        row['libelle_region']
    ))

conn.commit()
cursor.close()
conn.close()

print("REGION chargée ")
