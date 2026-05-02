import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Painel Uber", layout="centered")

st.title("🚗 Painel do Motorista")

# ================= CONFIG =================
st.sidebar.header("⚙️ Configurações")

consumo = st.sidebar.number_input("Consumo (km/L)", value=12.0)
gasolina = st.sidebar.number_input("Gasolina (R$)", value=7.25)
meta = st.sidebar.number_input("Meta diária (R$)", value=200.0)

# ================= SESSION =================
if "abastecimento" not in st.session_state:
    st.session_state.abastecimento = 0.0

# ================= ARQUIVO =================
if not os.path.exists("corridas.csv"):
    df = pd.DataFrame(columns=["data", "hora", "valor", "dinamica", "km", "tempo"])
    df.to_csv("corridas.csv", index=False)

df = pd.read_csv("corridas.csv")

# ================= TRATAMENTO =================
if not df.empty:
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["dinamica"] = pd.to_numeric(df["dinamica"], errors="coerce").fillna(0)
    df["km"] = pd.to_numeric(df["km"], errors="coerce").fillna(0)
    df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce").fillna(1)

    df["ganho_total"] = df["valor"] + df["dinamica"]
    df["custo"] = (df["km"] / consumo) * gasolina
    df["lucro"] = df["ganho_total"] - df["custo"]

# ================= ABASTECIMENTO =================
st.subheader("⛽ Abastecimento")

col_a, col_b = st.columns(2)

with col_a:
    valor_abastecido = st.number_input("Valor abastecido (R$)", min_value=0.0)

with col_b:
    if st.button("Adicionar abastecimento"):
        st.session_state.abastecimento += valor_abastecido
        st.success("Abastecimento registrado!")

# ================= RESUMO =================
st.subheader("💰 Resumo")

if not df.empty:
    total = df["ganho_total"].sum()
    custo = df["custo"].sum()
    lucro = df["lucro"].sum()
    km_total = df["km"].sum()
    media_hora = (df["ganho_total"] / (df["tempo"] / 60)).mean()
    caixa = total - st.session_state.abastecimento

    col1, col2 = st.columns(2)
    col1.metric("Total ganho", f"R$ {total:.2f}")
    col2.metric("Lucro real", f"R$ {lucro:.2f}")

    col3, col4 = st.columns(2)
    col3.metric("Km rodados", f"{km_total:.1f}")
    col4.metric("Média/hora", f"R$ {media_hora:.2f}")

    col5, col6 = st.columns(2)
    col5.metric("Abastecimento", f"R$ {st.session_state.abastecimento:.2f}")
    col6.metric("Caixa do dia", f"R$ {caixa:.2f}")

    progresso = min(int((total / meta) * 100), 100)
    st.progress(progresso)
    st.write(f"Meta: {progresso}%")

# ================= GRÁFICO =================
st.subheader("📊 Ganho ao longo do dia")

if not df.empty:
    df_sorted = df.sort_values("hora")
    st.line_chart(df_sorted.set_index("hora")["ganho_total"])

# ================= NOVA CORRIDA =================
st.subheader("➕ Nova corrida")

with st.form("corrida"):
    valor = st.number_input("Valor corrida (R$)", min_value=0.0)
    dinamica = st.number_input("Dinâmica (R$)", min_value=0.0)
    km = st.number_input("Km", min_value=0.0)
    tempo = st.number_input("Tempo (min)", min_value=1.0)

    enviar = st.form_submit_button("Adicionar")

    if enviar:
        nova = pd.DataFrame([{
            "data": datetime.now().date(),
            "hora": datetime.now().strftime("%H:%M"),
            "valor": valor,
            "dinamica": dinamica,
            "km": km,
            "tempo": tempo
        }])

        nova.to_csv("corridas.csv", mode="a", header=False, index=False)
        st.success("Corrida adicionada!")
        st.rerun()
