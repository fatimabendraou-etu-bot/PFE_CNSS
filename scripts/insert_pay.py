import oracledb
import pandas as pd
import math


conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()


df = pd.read_csv(r"C:/Users/fatimazahra/Downloads/output (1)/output/PAYMENT.csv")


df.columns = df.columns.str.strip().str.lower()
print("Colonnes :", df.columns)
print("Début chargement...")

num_cols = ['debit_cnss','debit_amo','debit_tfp','credit_cnss','credit_tfp','pn_cnss','pn_tfp']

for col in num_cols:
    df[col] = df[col].astype(str).str.replace(',', '.').str.strip()
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)


df['periode'] = df['periode'].astype(str).str.strip()
df['periode'] = pd.to_numeric(df['periode'], errors='coerce').fillna(0).astype(int)


chunk_size = 200000
num_chunks = math.ceil(len(df) / chunk_size)
print("debut")
for i in range(num_chunks):
    start = i * chunk_size
    end = start + chunk_size
    chunk = df.iloc[start:end]

    data = []
    for idx, row in chunk.iterrows():
        try:
            data.append((
                int(str(row['aff_num'])[3:]),
                int(row['periode']),
                float(row['debit_cnss']),
                float(row['debit_amo']),
                float(row['debit_tfp']),
                float(row['credit_cnss']),
                float(row['credit_tfp']),
                float(row['pn_cnss']),
                float(row['pn_tfp'])
            ))
        except Exception as e:
            print(f"Ligne ignorée idx {idx} pour erreur : {e}")

    if data:
        cursor.executemany("""
            INSERT INTO PAYEMENT (
                NUM_AFF, PERIODE, DEBIT_CNSS, DEBIT_AMO, DEBIT_TPF,
                CREDIT_CNSS, CREDIT_TPF, PN_CNSS, PN_TPF
            )
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9)
        """, data)
        conn.commit()
        print(f"Chunk {i+1}/{num_chunks} terminé (enregistrement {start+1} à {min(end,len(df))})")

cursor.close()
conn.close()
print("Tous les enregistrements ont été chargés avec succès !")