import streamlit as st
import pandas as pd
import datetime

# Arquivos CSV
CLIENTES_CSV = "clientes.csv"
AGENDAMENTOS_CSV = "agendamentos.csv"

# Barbeiros
BARBEIROS = ["Barbeiro1", "Barbeiro2", "Barbeiro3"]

# Horários de funcionamento (Seg-Sex: 9h-20h, Sáb: 9h-16h)
HORARIOS_SEMANA = [f"{h:02d}:00" for h in range(9, 21)]
HORARIOS_SABADO = [f"{h:02d}:00" for h in range(9, 17)]


# === Funções auxiliares ===
def carregar_csv(caminho, colunas):
    try:
        return pd.read_csv(caminho)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df_vazio = pd.DataFrame(columns=colunas)
        df_vazio.to_csv(caminho, index=False)
        return df_vazio


def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)


def cliente_existente(telefone, df_clientes):
    return telefone in df_clientes["Telefone"].astype(str).values


def agendamento_existente(data, hora, barbeiro, df_agendamentos):
    filtro = (
        (df_agendamentos["Data"] == data)
        & (df_agendamentos["Hora"] == hora)
        & (df_agendamentos["Barbeiro"] == barbeiro)
    )
    return filtro.any()


def horarios_disponiveis(data_str, barbeiro, df_agendamentos):
    data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
    dia_semana = data.weekday()

    horarios_possiveis = HORARIOS_SEMANA if dia_semana < 5 else HORARIOS_SABADO

    agendados = df_agendamentos[
        (df_agendamentos["Data"] == data_str) & (df_agendamentos["Barbeiro"] == barbeiro)
    ]["Hora"].tolist()

    return [h for h in horarios_possiveis if h not in agendados]


def barbearia_fechada(data_str):
    data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
    return data.weekday() > 5 and data.hour >= 16  # após 16h no sábado


# === INÍCIO DO APP ===
st.set_page_config(page_title="Agendamento de Barbearia", layout="centered")
st.title("💈 Agendamento de Horários - Barbearia Teste")

# Carregar dados
df_clientes = carregar_csv(CLIENTES_CSV, ["Telefone", "Nome", "Observações"])
df_agendamentos = carregar_csv(AGENDAMENTOS_CSV, ["Telefone", "Nome", "Barbeiro", "Data", "Hora"])

# Formulário
with st.form("form_agendamento"):
    st.subheader("📱 Identificação do Cliente")

    telefone = st.text_input("Telefone (WhatsApp)", max_chars=15)

    cliente_encontrado = cliente_existente(telefone, df_clientes)

    if cliente_encontrado:
        nome = df_clientes[df_clientes["Telefone"] == telefone]["Nome"].values[0]
        st.success(f"Cliente encontrado: {nome}")
    else:
        nome = st.text_input("Nome do Cliente")

    st.subheader("✂️ Agendamento")

    barbeiro = st.selectbox("Escolha o Barbeiro", BARBEIROS)
    data = st.date_input("Escolha a Data", min_value=datetime.date.today())
    data_str = data.strftime("%Y-%m-%d")

    horarios = horarios_disponiveis(data_str, barbeiro, df_agendamentos)

    if not horarios:
        st.warning("Barbearia fechada ou sem horários disponíveis.")
        hora = None
    else:
        hora = st.selectbox("Horário disponível", horarios)

    submitted = st.form_submit_button("Agendar")

    if submitted and telefone and nome and hora:
        # Salvar cliente novo
        if not cliente_encontrado:
            df_clientes.loc[len(df_clientes)] = [telefone, nome, ""]
            salvar_csv(df_clientes, CLIENTES_CSV)

        # Verificar agendamento simultâneo
        if agendamento_existente(data_str, hora, barbeiro, df_agendamentos):
            st.error("⚠️ Já existe um agendamento nesse horário para esse barbeiro.")
        else:
            # Salvar agendamento
            novo_agendamento = pd.DataFrame(
                [[telefone, nome, barbeiro, data_str, hora]],
                columns=df_agendamentos.columns
            )
            df_agendamentos = pd.concat([df_agendamentos, novo_agendamento], ignore_index=True)
            salvar_csv(df_agendamentos, AGENDAMENTOS_CSV)

            st.success(f"✅ Agendamento confirmado para {nome} com {barbeiro} em {data_str} às {hora}.")
            st.markdown(f"[💬 Enviar WhatsApp](https://wa.me/55{telefone}?text=Olá%20{nome},%20seu%20agendamento%20foi%20confirmado%20para%20{data_str}%20às%20{hora}%20com%20{barbeiro}.)")


# === ADMIN ===
with st.expander("🔐 Painel do Administrador"):
    st.subheader("📋 Agendamentos do dia")
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    agendamentos_hoje = df_agendamentos[df_agendamentos["Data"] == hoje]

    if not agendamentos_hoje.empty:
        st.dataframe(agendamentos_hoje)
    else:
        st.info("Nenhum agendamento para hoje.")
