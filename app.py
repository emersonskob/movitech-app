import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pyodbc
import os

# -------------------------
# CONFIGURAÇÃO
# -------------------------
st.set_page_config(page_title="MoviTech Robotics", layout="wide")

# -------------------------
# ESTILO VISUAL (MOVITECH)
# -------------------------
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

        .stMetric {
            background-color: #1B263B;
            padding: 15px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# LOGO (SE EXISTIR)
# -------------------------
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)
else:
    st.warning("Logo não encontrado (adicione logo.png na pasta)")

st.title("🤖 MoviTech Robotics")
st.caption("Sistema Inteligente de Produção Industrial")

# -------------------------
# FUNÇÃO AZURE
# -------------------------
def salvar_no_azure(df):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=movitech-server.database.windows.net;"
            "DATABASE=movitech_db;"
            "UID=adminmovitech;"
            "PWD=P@ralcool2"
        )

        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO producao (dia, data, produto, id_produto, lote, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            row["Dia"], row["Data"], row["Produto"],
            row["ID_Produto"], row["Lote"], row["Status"])

        conn.commit()
        conn.close()

        st.success("☁️ Dados enviados para Azure!")

    except Exception as e:
        st.error(f"Erro Azure: {e}")

# -------------------------
# INICIALIZAÇÃO
# -------------------------
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Dia", "Data", "Produto", "ID_Produto", "Lote", "Status"
    ])

if "dia" not in st.session_state:
    st.session_state.dia = 1

if "lote" not in st.session_state:
    st.session_state.lote = 1

if "ultima_producao" not in st.session_state:
    st.session_state.ultima_producao = 5

# -------------------------
# BOTÃO PRODUÇÃO
# -------------------------
st.markdown("---")

if st.button("🚀 Gerar Produção do Dia"):

    quantidade_dia = random.choices(
        [3, 4, 5, 6, 7, 8],
        weights=[10, 20, 40, 15, 10, 5]
    )[0]

    if st.session_state.ultima_producao == 8 and quantidade_dia == 8:
        quantidade_dia = random.choice([5, 6, 7])

    st.session_state.ultima_producao = quantidade_dia

    novos_dados = []

    for i in range(quantidade_dia):

        produto = "MoviTech X1 v2.0"
        id_produto = "MTX1-V2"
        lote = f"Lote-{st.session_state.lote:04d}"

        st.session_state.lote += 1

        chance = random.random()

        if chance < 0.2:
            status = "Correção"
        elif chance < 0.6:
            status = "Vendido"
        else:
            status = "Estoque"

        novos_dados.append([
            st.session_state.dia,
            datetime.now().strftime("%Y-%m-%d"),
            produto,
            id_produto,
            lote,
            status
        ])

    df_novo = pd.DataFrame(novos_dados, columns=[
        "Dia", "Data", "Produto", "ID_Produto", "Lote", "Status"
    ])

    # ☁️ ENVIO AZURE
    salvar_no_azure(df_novo)

    # Local
    st.session_state.dados = pd.concat(
        [st.session_state.dados, df_novo],
        ignore_index=True
    )

    # ciclo 60 dias
    if st.session_state.dia == 60:
        st.session_state.dia = 1
    else:
        st.session_state.dia += 1

    st.success(f"Produção do dia: {quantidade_dia} robôs")

# -------------------------
# INFO
# -------------------------
st.info(f"📅 Próximo dia de produção: {st.session_state.dia}")

df = st.session_state.dados

# -------------------------
# DASHBOARD
# -------------------------
if not df.empty:

    st.markdown("---")
    st.subheader("📊 Indicadores")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Produzidos", len(df))
    col2.metric("Vendidos", len(df[df["Status"] == "Vendido"]))
    col3.metric("Estoque", len(df[df["Status"] == "Estoque"]))
    col4.metric("Correção", len(df[df["Status"] == "Correção"]))

    st.markdown("---")

    st.subheader("📈 Produção por Dia")
    st.bar_chart(df.groupby("Dia").size())

    st.subheader("📊 Status dos Robôs")
    st.bar_chart(df["Status"].value_counts())

    st.subheader("📋 Dados Detalhados")
    st.dataframe(df, use_container_width=True)

    df.to_csv("producao.csv", index=False)