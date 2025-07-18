import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações da barbearia
barbeiros = ["Barbeiro1", "Barbeiro2", "Barbeiro3"]
dias_funcionamento = {
    "segunda-feira": ("09:00", "20:00"),
    "terça-feira": ("09:00", "20:00"),
    "quarta-feira": ("09:00", "20:00"),
    "quinta-feira": ("09:00", "20:00"),
    "sexta-feira": ("09:00", "20:00"),
    "sábado": ("09:00", "16:00")
}
arquivo_csv = "agendamentos.csv"

# Inicializa o arquivo se não existir
try:
    df = pd.read_csv(arquivo_csv)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Nome", "Telefone", "Barbeiro", "Data", "Hora"])
    df.to_csv(arquivo_csv, index=False)

# Função para gerar horários disponíveis
def gerar_horarios(data_selecionada):
    dia_semana = data_selecionada.strftime("%A").lower()
    if dia_semana not in dias_funcionamento:
        return []

    inicio, fim = dias_funcionamento[dia_semana]
    inicio_dt = datetime.strptime(inicio, "%H:%M")
    fim_dt = datetime.strptime(fim, "%H:%M")
    horarios = []
    atual = inicio_dt
    while atual < fim_dt:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=30)
    return horarios

# Interface do app
st.set_page_config(page_title="Agendamento - barbearia_teste")
st.title("💈 Plataforma de Agendamento - barbearia_teste")

menu = st.sidebar.selectbox("Menu", ["Agendar horário", "Admin (ver agendamentos)"])

if menu == "Agendar horário":
    st.subheader("📅 Faça seu agendamento")

    nome = st.text_input("Nome completo")
    telefone = st.text_input("Telefone (WhatsApp)")
    barbeiro = st.selectbox("Escolha o barbeiro", barbeiros)
    data = st.date_input("Escolha o dia", min_value=datetime.today())
    
    horarios_disponiveis = gerar_horarios(data)
    if horarios_disponiveis:
        hora = st.selectbox("Escolha o horário", horarios_disponiveis)
    else:
        st.warning("Barbearia fechada neste dia.")
        hora = None

    if st.button("Confirmar Agendamento") and nome and telefone and hora:
        novo_agendamento = {
            "Nome": nome,
            "Telefone": telefone,
            "Barbeiro": barbeiro,
            "Data": data.strftime("%Y-%m-%d"),
            "Hora": hora
        }
        df = pd.read_csv(arquivo_csv)
        df = pd.concat([df, pd.DataFrame([novo_agendamento])], ignore_index=True)
        df.to_csv(arquivo_csv, index=False)
        st.success("✅ Agendamento realizado com sucesso!")

elif menu == "Admin (ver agendamentos)":
    st.subheader("🧾 Lista de Agendamentos")
    senha = st.text_input("Senha de admin", type="password")
    if senha == "admin123":  # Troque para uma senha segura
        df = pd.read_csv(arquivo_csv)
        filtro_barbeiro = st.multiselect("Filtrar por barbeiro", barbeiros, default=barbeiros)
        df_filtrado = df[df["Barbeiro"].isin(filtro_barbeiro)]

        st.dataframe(df_filtrado.sort_values(by=["Data", "Hora"]))
        st.download_button("📥 Baixar CSV", df_filtrado.to_csv(index=False), "agendamentos.csv", "text/csv")
    elif senha != "":
        st.error("Senha incorreta.")
