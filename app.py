import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ------------------------------
# CONFIGURAÇÕES
# ------------------------------
st.set_page_config(page_title="Agendamento - Barbearia", layout="centered")
st.title("💈 Sistema de Agendamento - Barbearia")

ARQUIVO_CSV = "agendamentos.csv"
BARBEIROS = ["Barbeiro1", "Barbeiro2", "Barbeiro3"]

HORARIOS_FUNCIONAMENTO = {
    "segunda-feira": ("09:00", "20:00"),
    "terça-feira": ("09:00", "20:00"),
    "quarta-feira": ("09:00", "20:00"),
    "quinta-feira": ("09:00", "20:00"),
    "sexta-feira": ("09:00", "20:00"),
    "sábado": ("09:00", "16:00")
}

DIAS_TRADUCAO = {
    "Monday": "segunda-feira",
    "Tuesday": "terça-feira",
    "Wednesday": "quarta-feira",
    "Thursday": "quinta-feira",
    "Friday": "sexta-feira",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

# ------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------
def carregar_dados():
    if not Path(ARQUIVO_CSV).exists():
        df = pd.DataFrame(columns=["Nome", "Telefone", "Barbeiro", "Data", "Hora"])
        df.to_csv(ARQUIVO_CSV, index=False)
    try:
        return pd.read_csv(ARQUIVO_CSV)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["Nome", "Telefone", "Barbeiro", "Data", "Hora"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False)

def gerar_horarios(data):
    dia_semana = DIAS_TRADUCAO.get(data.strftime("%A"))
    if dia_semana not in HORARIOS_FUNCIONAMENTO:
        return []

    inicio_str, fim_str = HORARIOS_FUNCIONAMENTO[dia_semana]
    inicio = datetime.strptime(inicio_str, "%H:%M")
    fim = datetime.strptime(fim_str, "%H:%M")

    horarios = []
    atual = inicio
    while atual < fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=30)
    return horarios

# ------------------------------
# INTERFACE
# ------------------------------
menu = st.sidebar.radio("Menu", ["📅 Agendar", "🔐 Admin"])

if menu == "📅 Agendar":
    st.header("📋 Agende seu Horário")
    nome = st.text_input("Nome completo")
    telefone = st.text_input("Telefone (WhatsApp)")
    barbeiro = st.selectbox("Barbeiro desejado", BARBEIROS)
    data = st.date_input("Escolha a data", min_value=datetime.today())

    horarios_disponiveis = gerar_horarios(data)
    hora = st.selectbox("Horário disponível", horarios_disponiveis) if horarios_disponiveis else None

    if not horarios_disponiveis:
        st.warning("❌ Barbearia fechada nesse dia.")

    if st.button("✅ Confirmar Agendamento"):
        if nome and telefone and hora:
            df = carregar_dados()
            conflito = df[
                (df["Barbeiro"] == barbeiro) &
                (df["Data"] == data.strftime("%Y-%m-%d")) &
                (df["Hora"] == hora)
            ]
            if not conflito.empty:
                st.error("❌ Horário já reservado para esse barbeiro. Escolha outro horário.")
            else:
                novo = pd.DataFrame([{
                    "Nome": nome.strip(),
                    "Telefone": telefone.strip(),
                    "Barbeiro": barbeiro,
                    "Data": data.strftime("%Y-%m-%d"),
                    "Hora": hora
                }])
                df = pd.concat([df, novo], ignore_index=True)
                salvar_dados(df)
                st.success("🎉 Agendamento realizado com sucesso!")
        else:
            st.error("Preencha todos os campos para confirmar o agendamento.")

elif menu == "🔐 Admin":
    st.header("🔒 Painel Administrativo")
    senha = st.text_input("Senha de administrador", type="password")

    if senha == "admin123":
        df = carregar_dados()
        if df.empty:
            st.info("Nenhum agendamento registrado.")
        else:
            st.markdown("### 📑 Lista de Agendamentos")
            df_sorted = df.sort_values(by=["Data", "Hora"])
            filtro_barbeiro = st.multiselect("Filtrar por barbeiro", options=BARBEIROS, default=BARBEIROS)
            df_filtrado = df_sorted[df_sorted["Barbeiro"].isin(filtro_barbeiro)]
            st.dataframe(df_filtrado, use_container_width=True)

            st.download_button(
                label="📥 Baixar lista (CSV)",
                data=df_filtrado.to_csv(index=False),
                file_name="agendamentos_filtrados.csv",
                mime="text/csv"
            )
    elif senha:
        st.error("Senha incorreta.")
