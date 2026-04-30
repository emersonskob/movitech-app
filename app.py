import streamlit as st

# =========================

# 🔐 LOGIN MULTIUSUÁRIO

# =========================

usuarios = {
"admin": "1234",
"emerson": "movitech",
"helton": "1234",
"marcelo": "1234",
"daniel": "1234",
"rodrigo": "1234"
}

if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():
import os

```
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)

st.title("Login - MoviTech Robotics")

usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if usuario in usuarios and usuarios[usuario] == senha:
        st.session_state.logado = True
        st.session_state.usuario = usuario
        st.rerun()
    else:
        st.error("Usuário ou senha inválidos")
```

# =========================

# 🚀 APP PRINCIPAL

# =========================

def app():

```
import pandas as pd
import random
from datetime import datetime, timedelta
import psycopg2
import os

st.set_page_config(page_title="MoviTech Robotics", layout="wide")

# 🎨 ESTILO
st.markdown("""
    <style>
        .stApp {
            background-color: #0D1B2A;
            color: #FFFFFF;
        }
        h1, h2, h3 {
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #F77F00;
            color: white;
            height: 50px;
            font-size: 18px;
            border-radius: 12px;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# 🔹 LOGO
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)

st.title("🤖 MoviTech Robotics")
st.caption("Sistema Inteligente de Produção Industrial")

st.success(f"👤 Usuário logado: {st.session_state.usuario}")

# =========================
# ☁️ AWS RDS
# =========================
def salvar_no_aws(df):
    try:
        conn = psycopg2.connect(
            host="movitech-db.cj64e86mcmek.us-east-2.rds.amazonaws.com",
            database="postgres",
            user="postgres",
            password="Paralcool2",
            port=5432
        )

        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO producao 
                (dia, data, produto, id_produto, lote, etapa, usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row["Dia"],
                row["Data"],
                row["Produto"],
                row["ID_Produto"],
                row["Lote"],
                row["Etapa"],
                row["Usuario"]
            ))

        conn.commit()
        conn.close()

        st.success("☁️ Dados enviados para AWS!")

    except Exception as e:
        st.error(f"Erro AWS: {e}")

# =========================
# 📊 VARIÁVEIS
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Dia", "Data", "Produto", "ID_Produto", "Lote", "Etapa", "Usuario"
    ])

if "lote" not in st.session_state:
    st.session_state.lote = 1

# =========================
# 🏭 ETAPAS
# =========================
ETAPAS = [
    "Recebimento",
    "Almoxarifado",
    "Dobradeira",
    "Tornearia",
    "Montagem Mecânica",
    "Montagem Elétrica",
    "Testes",
    "Expedição"
]

st.markdown("---")

# =========================
# 📅 PLANEJAMENTO PPCP
# =========================
st.subheader("📅 Planejamento da Produção")

data_inicio = st.date_input("Selecione a data de início")

if st.button("🚀 Gerar Produção Mensal (PPCP)"):

    novos_dados = []

    dias_uteis = []
    data_atual = data_inicio

    while len(dias_uteis) < 20:
        if data_atual.weekday() < 5:
            dias_uteis.append(data_atual)
        data_atual += timedelta(days=1)

    for i in range(10):

        produto = "MoviTech X1 v2.0"
        id_produto = "MTX1-V2"
        lote = f"Lote-{st.session_state.lote:04d}"

        semana1 = dias_uteis[0:5]
        semana2 = dias_uteis[5:10]
        semana3 = dias_uteis[10:15]
        semana4 = dias_uteis[15:20]

        dia = random.choice(semana1)
        for etapa in ["Recebimento", "Almoxarifado"]:
            novos_dados.append([dia.day, dia.strftime("%Y-%m-%d"), produto, id_produto, lote, etapa, st.session_state.usuario])

        dia = random.choice(semana2)
        novos_dados.append([dia.day, dia.strftime("%Y-%m-%d"), produto, id_produto, lote, "Dobradeira", st.session_state.usuario])

        dia = random.choice(semana3)
        novos_dados.append([dia.day, dia.strftime("%Y-%m-%d"), produto, id_produto, lote, "Tornearia", st.session_state.usuario])

        dia = random.choice(semana4)
        for etapa in ["Montagem Mecânica","Montagem Elétrica","Testes","Expedição"]:
            novos_dados.append([dia.day, dia.strftime("%Y-%m-%d"), produto, id_produto, lote, etapa, st.session_state.usuario])

        st.session_state.lote += 1

    df_novo = pd.DataFrame(novos_dados, columns=[
        "Dia", "Data", "Produto", "ID_Produto", "Lote", "Etapa", "Usuario"
    ])

    salvar_no_aws(df_novo)

    st.session_state.dados = pd.concat([st.session_state.dados, df_novo], ignore_index=True)

    st.success("✅ Produção mensal enviada para AWS")

df = st.session_state.dados

# =========================
# 📊 DASHBOARD
# =========================
if not df.empty:

    st.markdown("---")
    st.subheader("📊 Indicadores")

    col1, col2 = st.columns(2)

    col1.metric("Total Registros", len(df))
    col2.metric("Robôs Produzidos", df["Lote"].nunique())

    st.markdown("---")

    st.subheader("🏭 Fluxo por Etapa")
    st.bar_chart(df["Etapa"].value_counts())

    st.subheader("📈 Produção por Dia")
    st.bar_chart(df.groupby("Dia")["Lote"].nunique())

    st.subheader("👤 Produção por Usuário")
    st.bar_chart(df["Usuario"].value_counts())

    st.subheader("📋 Dados Detalhados")
    st.dataframe(df, use_container_width=True)

if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
```

# =========================

# 🔁 CONTROLE FINAL

# =========================

if st.session_state.logado:
app()
else:
tela_login()
