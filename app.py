import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Painel Uber", layout="centered")

st.title("🚗 Painel do Motorista")

# Configuração do carro
consumo_km_l = 12
preco_gasolina = 6.0

# Criar arquivo se não existir
if not os.path.exists("corridas.csv"):
    df = pd.DataFrame(columns=["data", "hora", "valor", "km", "tempo_min"])
    df.to_csv("corridas.csv", index=False)

# Carregar dados
df = pd.read_csv("corridas.csv")

# Converter tipos
if not df.empty:
    df["valor"] = df["valor"].astype(float)
    df["km"] = df["km"].astype(float)
    df["tempo_min"] = df["tempo_min"].astype(float)

    df["custo"] = df["km"] / consumo_km_l * preco_gasolina
    df["lucro"] = df["valor"] - df["custo"]
    df["hora_num"] = pd.to_datetime(df["hora"]).dt.hour

# === RESUMO ===
st.subheader("💰 Resumo")

if not df.empty:
    total = df["valor"].sum()
    lucro = df["lucro"].sum()
    media_hora = (df["valor"] / (df["tempo_min"] / 60)).mean()

    col1, col2 = st.columns(2)
    col1.metric("Total ganho", f"R$ {total:.2f}")
    col2.metric("Lucro", f"R$ {lucro:.2f}")

    col3, col4 = st.columns(2)
    col3.metric("Média/hora", f"R$ {media_hora:.2f}")
    col4.metric("Corridas", len(df))

# === GRÁFICO ===
st.subheader("📊 Ganho ao longo do dia")

if not df.empty:
    df_sorted = df.sort_values("hora")
    st.line_chart(df_sorted.set_index("hora")["valor"])

# === ADICIONAR CORRIDA ===
st.subheader("➕ Nova corrida")

with st.form("nova_corrida"):
    valor = st.number_input("Valor (R$)", min_value=0.0)
    km = st.number_input("Km", min_value=0.0)
    tempo = st.number_input("Tempo (min)", min_value=1.0)

    submitted = st.form_submit_button("Adicionar")

    if submitted:
        nova = pd.DataFrame([{
            "data": datetime.now().date(),
            "hora": datetime.now().strftime("%H:%M"),
            "valor": valor,
            "km": km,
            "tempo_min": tempo
        }])

        nova.to_csv("corridas.csv", mode="a", header=False, index=False)
        st.success("Corrida adicionada!")
        st.rerun()
