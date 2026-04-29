import streamlit as st
import pyodbc
from datetime import date
import os

st.set_page_config(page_title="Movitech", layout="centered")

# LOGO
if os.path.exists("logo.png"):
    st.image("logo.png", width=220)

# CONEXÃO
def conectar():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={st.secrets['DB_SERVER']};"
        f"DATABASE={st.secrets['DB_NAME']};"
        f"UID={st.secrets['DB_USER']};"
        f"PWD={st.secrets['DB_PASSWORD']};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

# LOGIN
usuarios = ["emerson", "rodrigo", "admin"]

if "usuario" not in st.session_state:
    st.session_state.usuario = None

def tela_login():
    st.subheader("Login")
    user = st.selectbox("Usuário", usuarios)

    if st.button("Entrar"):
        st.session_state.usuario = user
        st.rerun()

if st.session_state.usuario is None:
    tela_login()
    st.stop()

st.success(f"Usuário logado: {st.session_state.usuario}")

# FORM
st.title("Controle de Produção")

produto = st.text_input("Produto")
id_produto = st.text_input("ID Produto")
lote = st.text_input("Lote")

etapas = [
    "Recebimento",
    "Almoxarifado",
    "Dobradeira",
    "Tornearia",
    "Montagem Mecânica",
    "Montagem Elétrica",
    "Testes",
    "Expedição"
]

etapa = st.selectbox("Etapa", etapas)

if st.button("Registrar Produção"):
    conn = conectar()
    cursor = conn.cursor()

    hoje = date.today()

    cursor.execute("""
        INSERT INTO producao (dia, data, produto, id_produto, lote, etapa, usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, hoje.day, hoje, produto, id_produto, lote, etapa, st.session_state.usuario)

    conn.commit()
    conn.close()

    st.success("Produção registrada com sucesso!")

# VISUAL
st.subheader("Produções registradas")

if st.button("Atualizar dados"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM producao")

    rows = cursor.fetchall()
    conn.close()

    st.write(rows)
