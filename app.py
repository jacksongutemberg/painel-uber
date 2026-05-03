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
if "abastecimento_total" not in st.session_state:
    st.session_state.abastecimento_total = 0.0

# ================= ARQUIVO =================
if not os.path.exists("corridas.csv"):
    df = pd.DataFrame(columns=["data", "hora", "valor", "dinamica", "km", "tempo"])
    df.to_csv("corridas.csv", index=False)

df = pd.read_csv("corridas.csv")

# ================= TRATAMENTO =================
if not df.empty:
    df["data"] = pd.to_datetime(df["data"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["dinamica"] = pd.to_numeric(df["dinamica"], errors="coerce").fillna(0)
    df["km"] = pd.to_numeric(df["km"], errors="coerce").fillna(0)
    df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce").fillna(1)

    df["ganho_total"] = df["valor"] + df["dinamica"]
    df["custo"] = (df["km"] / consumo) * gasolina
    df["lucro"] = df["ganho_total"] - df["custo"]
    df["ganho_km"] = df["ganho_total"] / df["km"].replace(0, 1)

    hoje = pd.Timestamp.now().date()
    semana = pd.Timestamp.now() - pd.Timedelta(days=7)
    mes = pd.Timestamp.now().replace(day=1)

    df_hoje = df[df["data"].dt.date == hoje]
    df_semana = df[df["data"] >= semana]
    df_mes = df[df["data"] >= mes]

# ================= ABASTECIMENTO =================
st.subheader("⛽ Abastecimento")

valor_abastecido = st.number_input("Valor abastecido (R$)", min_value=0.0)

if st.button("Adicionar abastecimento"):
    st.session_state.abastecimento_total += valor_abastecido
    st.success("Abastecimento registrado!")

st.write(f"Total abastecido: R$ {st.session_state.abastecimento_total:.2f}")

# ================= RESUMO =================
st.subheader("💰 Hoje")

if not df.empty and not df_hoje.empty:
    total = df_hoje["ganho_total"].sum()
    lucro = df_hoje["lucro"].sum()
    km_total = df_hoje["km"].sum()
    ganho_km = df_hoje["ganho_total"].sum() / max(km_total, 1)
    dinamica_total = df_hoje["dinamica"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total ganho", f"R$ {total:.2f}")
    col2.metric("Lucro real", f"R$ {lucro:.2f}")

    col3, col4 = st.columns(2)
    col3.metric("Ganho por km", f"R$ {ganho_km:.2f}")
    col4.metric("Dinâmica", f"R$ {dinamica_total:.2f}")

    progresso = min(int((total / meta) * 100), 100)
    st.progress(progresso)
    st.write(f"Meta: {progresso}%")

# ================= SEMANA =================
st.subheader("📅 Semana")

if not df.empty:
    st.write(f"Total: R$ {df_semana['ganho_total'].sum():.2f}")
    st.write(f"Dinâmica: R$ {df_semana['dinamica'].sum():.2f}")

# ================= MÊS =================
st.subheader("📆 Mês")

if not df.empty:
    st.write(f"Total: R$ {df_mes['ganho_total'].sum():.2f}")
    st.write(f"Dinâmica: R$ {df_mes['dinamica'].sum():.2f}")

# ================= RANKING =================
st.subheader("🏆 Ranking de dias")

if not df.empty:
    ranking = df.groupby(df["data"].dt.date)["ganho_total"].sum().sort_values(ascending=False)
    st.dataframe(ranking)

# ================= TABELA =================
st.subheader("💸 Corridas")

if not df.empty:
    st.dataframe(df[["data", "hora", "ganho_total", "km", "lucro", "ganho_km"]])

# ================= GRÁFICO =================
st.subheader("📊 Evolução")

if not df.empty:
    st.line_chart(df.groupby(df["data"].dt.date)["ganho_total"].sum())

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
