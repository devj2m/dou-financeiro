import requests
import psycopg2
from datetime import datetime

# 🔹 CONFIGURE AQUI DEPOIS (vamos voltar nisso)
DB_HOST = "SEU_HOST"
DB_NAME = "SEU_DB"
DB_USER = "SEU_USER"
DB_PASS = "SEU_PASSWORD"

# 🔹 CONEXÃO
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cursor = conn.cursor()

# 🔹 CRIAR TABELA
cursor.execute("""
CREATE TABLE IF NOT EXISTS publicacoes (
    id SERIAL PRIMARY KEY,
    data DATE,
    titulo TEXT,
    orgao TEXT,
    score INT,
    impacto TEXT,
    resumo TEXT,
    link TEXT
)
""")

conn.commit()

# 🔹 DATA DE HOJE
data = datetime.today().strftime('%Y-%m-%d')

# 🔹 BUSCAR DOU
url = f"https://www.in.gov.br/en/web/dou/-/search?q=&publishDate={data}"
response = requests.get(url)
items = response.json().get("items", [])

# 🔹 FUNÇÃO DE SCORE
def calcular_score(titulo, orgao):
    score = 0
    t = titulo.lower()

    alto = ["resolução", "selic", "taxa de juros", "regulação"]
    medio = ["crédito", "banco", "financeiro"]
    baixo = ["nomeação", "designação"]

    if any(p in t for p in alto):
        score += 50
    if any(p in t for p in medio):
        score += 30
    if any(p in t for p in baixo):
        score -= 10

    if "banco central" in orgao.lower():
        score += 30

    return max(0, min(score, 100))

# 🔹 CLASSIFICAÇÃO
def classificar(score):
    if score >= 70:
        return "ALTO"
    elif score >= 40:
        return "MÉDIO"
    else:
        return "BAIXO"

# 🔹 PROCESSAR
for item in items:
    titulo = item.get("title", "")
    orgao = item.get("hierarchyStr", "")

    score = calcular_score(titulo, orgao)
    impacto = classificar(score)

    if score < 40:
        continue

    resumo = titulo[:200]

    cursor.execute("""
        INSERT INTO publicacoes (data, titulo, orgao, score, impacto, resumo, link)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data, titulo, orgao, score, impacto, resumo, item.get("urlTitle")
    ))

conn.commit()
cursor.close()
conn.close()

print("Finalizado com sucesso")
