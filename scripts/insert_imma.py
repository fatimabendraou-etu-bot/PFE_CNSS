import oracledb
import pandas as pd

conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()

df = pd.read_csv("C:/Users/fatimazahra/Downloads/output (1)/output/IMMA.csv")

df['aff_num'] = df['aff_num'].str.replace('AFF', '').astype(int)
df['date_entree'] = pd.to_datetime(df['date_entree'], format='%d/%m/%Y')

for _, row in df.iterrows():
    num_imma_int = int(row['imma_num'].replace('IMMA',''))  
    cursor.execute("""
        INSERT INTO IMMA (NUM_IMMA, NUM_AFF, DATE_ENTREE)
        VALUES (:1, :2, TO_DATE(:3,'YYYY-MM-DD'))
    """, (
        num_imma_int,
        row['aff_num'],                  
        row['date_entree'].strftime('%Y-%m-%d')
    ))

conn.commit()
cursor.close()
conn.close()

print("IMMA chargée ")