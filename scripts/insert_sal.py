import pandas as pd
import oracledb

conn = oracledb.connect(user="pfe", password="pfe", dsn="localhost:1521/xepdb1")
cursor = conn.cursor()
cursor.arraysize = 1000
conn.autocommit = False

print("Connexion Oracle etablie")

CSV_PATH = r"C:/Users/fatimazahra/Downloads/output (1)/output/SALAIRE.csv"
CHUNK_SIZE = 250_000

total_inserted = 0
chunk_num = 0

for chunk in pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE):
    chunk_num += 1
    print(f"\nTraitement du chunk {chunk_num} ({len(chunk):,} lignes)...")
    
    chunk.rename(columns=lambda x: x.strip().lower(), inplace=True)
    
    chunk['aff_num'] = pd.to_numeric(chunk['aff_num'].astype(str).str.replace('AFF','',regex=False), errors='coerce')
    
    chunk['salaire_brut'] = pd.to_numeric(chunk['salaire_brut'], errors='coerce').round(2)
  
    chunk['periode'] = pd.to_datetime(chunk['periode'], format='%Y%m', errors='coerce')
    
    
    chunk = chunk.dropna(subset=['aff_num','salaire_brut','periode'])
    
    rows = [
        (int(row.aff_num), row.imma_num, float(row.salaire_brut), row.periode.strftime('%Y-%m'))
        for row in chunk.itertuples(index=False)
    ]
    
    if rows:
        cursor.executemany("""
            INSERT INTO SAL (NUM_AFF, NUM_IMMA, SALAIRE_BRUTE, PERIODE)
            VALUES (:1, :2, :3, TO_DATE(:4,'YYYY-MM'))
        """, rows)
        conn.commit()
    
    total_inserted += len(rows)
    print(f"Chunk {chunk_num} : {len(rows):,} lignes insérées")

cursor.close()
conn.close()

print(f"\nInsertion terminée. Total inséré : {total_inserted:,} lignes")