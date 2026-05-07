import oracledb
import pandas as pd

conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()

df = pd.read_csv("C:/Users/fatimazahra/Downloads/output (1)/output/AFF.csv")

df['aff_num'] = df['aff_num'].str.replace('AFF', '').astype(int)
df['date_affiliation'] = pd.to_datetime(df['date_affiliation'], format='%d/%m/%Y')

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO AFF (NUM_AFFILIE, DATE_AFF, SECTEUR_ID, REGION_ID, VILLE_ID)
        VALUES (:1, TO_DATE(:2,'YYYY-MM-DD'), :3, :4, :5)
    """, (
        int(row['aff_num']),
        row['date_affiliation'].strftime('%Y-%m-%d'),
        int(row['secteur_id']),
        int(row['region_id']),
        int(row['ville_id'])
    ))

conn.commit()
cursor.close()
conn.close()

print("AFF chargée ")