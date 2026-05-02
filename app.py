import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Painel Uber", layout="centered")

st.title("🚗 Painel do Motorista")

# === CONFIGURAÇÕES ===
st.sidebar.header("⚙️ Configurações")

consumo_km_l = st.sidebar.number_input("Consumo do carro (km/L)", value=12.0)
preco_gasolina = st.sidebar.number_input("Preço da gasolina (R$)", value=7.25)
meta_dia = st.sidebar.number_input("Meta diária (R$)", value=200.0)

# === ARQUIVO ===
if not os.path.exists("corridas.csv"):
    df = pd.DataFrame(columns=["data", "hora", "valor", "km", "tempo_min", "dinamica"])
    df.to_csv("corridas.csv", index=False)

df = pd.read_csv("corridas.csv")

if not df.empty:
    df["valor"] = df["valor"].astype(float)
    df["km"] = df["km"].astype(float)
    df["tempo_min"] = df["tempo_min"].astype(float)
    df["dinamica"] = df["dinamica"].astype(float)

    df["custo"] = df["km"] / consumo_km_l * preco_gasolina
    df["lucro"] = df["valor"] - df["custo"]
    df["ganho_total"] = df["valor"] + df["dinamica"]

# === RESUMO ===
st.subheader("💰 Resumo do dia")

if not df.empty:
    total = df["ganho_total"].sum()
    lucro = df["lucro"].sum()
    km_total = df["km"].sum()
    media_hora = (df["ganho_total"] / (df["tempo_min"] / 60)).mean()

    col1, col2 = st.columns(2)
    col1.metric("Total ganho", f"R$ {total:.2f}")
    col2.metric("Lucro", f"R$ {lucro:.2f}")

    col3, col4 = st.columns(2)
    col3.metric("Média/hora", f"R$ {media_hora:.2f}")
    col4.metric("Km rodados", f"{km_total:.1f} km")

    progresso = (total / meta_dia) * 100
    st.progress(min(int(progresso), 100))
    st.write(f"Meta: {progresso:.1f}% concluída")

# === GRÁFICO ===
st.subheader("📊 Ganho ao longo do dia")

if not df.empty:
    df_sorted = df.sort_values("hora")
    st.line_chart(df_sorted.set_index("hora")["ganho_total"])

# === ABASTECIMENTO ===
st.subheader("⛽ Abastecimento")

valor_abastecido = st.number_input("Quanto você abasteceu (R$)", min_value=0.0)

if st.button("Registrar abastecimento"):
    st.success(f"Abastecimento de R$ {valor_abastecido:.2f} registrado!")

# === NOVA CORRIDA ===
st.subheader("➕ Nova corrida")

with st.form("nova_corrida"):
    valor = st.number_input("Valor da corrida (R$)", min_value=0.0)
    dinamica = st.number_input("Dinâmica (R$)", min_value=0.0)
    km = st.number_input("Km", min_value=0.0)
    tempo = st.number_input("Tempo (min)", min_value=1.0)

    submitted = st.form_submit_button("Adicionar")

    if submitted:
        nova = pd.DataFrame([{
            "data": datetime.now().date(),
            "hora": datetime.now().strftime("%H:%M"),
            "valor": valor,
            "km": km,
            "tempo_min": tempo,
            "dinamica": dinamica
        }])

        nova.to_csv("corridas.csv", mode="a", header=False, index=False)
        st.success("Corrida adicionada!")
        st.rerun()
