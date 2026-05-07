import pandas as pd
import oracledb

conn = oracledb.connect(
    user="pfe",
    password="pfe",
    dsn="127.0.0.1:1521/XEPDB1"
)

query = "SELECT * FROM dataset"

df = pd.read_sql(query, conn)  