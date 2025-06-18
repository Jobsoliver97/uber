
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def load_data():
    try:
        return pd.read_csv('data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Data', 'Receita', 'Despesa', 'KM', 'Obs'])

def save_data(df):
    df.to_csv('data.csv', index=False)

def load_despesas():
    try:
        return pd.read_csv('despesas_extras.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Data', 'Descrição', 'Valor'])

def save_despesas(df):
    df.to_csv('despesas_extras.csv', index=False)

def calcular_saldo_semana_passada(df):
    if df.empty:
        return 0.0
    hoje = datetime.today().date()
    segunda_atual = hoje - timedelta(days=hoje.weekday())
    segunda_passada = segunda_atual - timedelta(days=7)
    domingo_passado = segunda_atual - timedelta(days=1)
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    semana_passada = df[(df['Data'] >= segunda_passada) & (df['Data'] <= domingo_passado)]
    saldo = semana_passada['Receita'].sum() - semana_passada['Despesa'].sum()
    return round(saldo, 2)

st.title("Controle de Corridas Uber 🚗")

df = load_data()
despesas_extras = load_despesas()

if not df.empty:
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['Data_str'] = df['Data'].astype(str)

if not despesas_extras.empty:
    despesas_extras['Data'] = pd.to_datetime(despesas_extras['Data']).dt.date

saldo_total = df['Receita'].sum() - despesas_extras['Valor'].sum()
st.metric("💰 Saldo Geral Atual", f"R$ {saldo_total:.2f}")

saldo_semana_passada = calcular_saldo_semana_passada(df)
st.info(f"💡 Saldo acumulado da semana passada: R$ {saldo_semana_passada:.2f}")

if datetime.today().weekday() == 0:
    st.subheader("⛽ Registrar Abastecimento de Segunda-feira")
    valor_abastecido = st.number_input("Valor abastecido (R$)", min_value=0.0, step=1.0, key="auto_abastecimento")
    if st.button("Registrar abastecimento com saldo acumulado"):
        nova_despesa = pd.DataFrame([[datetime.today().date(), 'Abastecimento semanal', valor_abastecido]],
                                    columns=['Data', 'Descrição', 'Valor'])
        despesas_extras = pd.concat([despesas_extras, nova_despesa], ignore_index=True)
        save_despesas(despesas_extras)
        st.success("Abastecimento registrado com sucesso!")

st.markdown("---")

# Entrada de ganho manual
st.subheader("➕ Adicionar Receita Manual")
with st.expander("Clique aqui para registrar ganho manual"):
    data_receita = st.date_input("Data da receita", value=datetime.today(), key="manual_data_receita")
    valor_receita = st.number_input("Valor (R$)", min_value=0.0, key="manual_valor_receita")
    obs_receita = st.text_input("Observação", key="manual_obs_receita")
    if st.button("Registrar receita manual"):
        nova = pd.DataFrame([[data_receita, valor_receita, 0.0, 0.0, obs_receita]],
                            columns=['Data', 'Receita', 'Despesa', 'KM', 'Obs'])
        df = pd.concat([df, nova], ignore_index=True)
        save_data(df)
        st.success("Receita manual registrada com sucesso!")

# Despesa extra manual
st.subheader("➕ Adicionar Despesa Extra Manualmente")
with st.expander("Clique aqui para registrar despesa"):
    data_extra = st.date_input("Data da despesa", value=datetime.today(), key="manual_data")
    descricao_extra = st.text_input("Descrição", value="Abastecimento semanal", key="manual_desc")
    valor_extra = st.number_input("Valor (R$)", min_value=0.0, key="manual_valor")
    if st.button("Registrar despesa extra manual"):
        nova_extra = pd.DataFrame([[data_extra, descricao_extra, valor_extra]],
                                  columns=['Data', 'Descrição', 'Valor'])
        despesas_extras = pd.concat([despesas_extras, nova_extra], ignore_index=True)
        save_despesas(despesas_extras)
        st.success("Despesa extra registrada com sucesso!")

st.markdown("---")

# Formulário padrão de corrida
st.subheader("📝 Nova Corrida")
with st.form("nova_corrida"):
    data = st.date_input("Data", value=datetime.today(), key="nova_data")
    receita = st.number_input("Receita (R$)", min_value=0.0, key="nova_receita")
    km = st.number_input("KM percorrido", min_value=0.0, key="nova_km")
    despesa_calculada = (km / 10) * 5.89
    st.markdown(f"**Despesa estimada com combustível:** R$ {despesa_calculada:.2f}")
    obs = st.text_input("Observações", key="nova_obs")
    enviar = st.form_submit_button("Registrar corrida")

    if enviar:
        nova_linha = pd.DataFrame([[data, receita, despesa_calculada, km, obs]],
                                   columns=['Data', 'Receita', 'Despesa', 'KM', 'Obs'])
        df = pd.concat([df, nova_linha], ignore_index=True)
        save_data(df)
        st.success("Corrida registrada com sucesso!")
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        df['Data_str'] = df['Data'].astype(str)

st.markdown("---")

# Editar lançamento
st.subheader("✏️ Editar Lançamento")
if not df.empty:
    index = st.selectbox("Escolha o registro para editar:", df.index, format_func=lambda i: f"{df.loc[i, 'Data']} - R$ {df.loc[i, 'Receita']}")
    if st.button("Editar este registro"):
        with st.form("editar_corrida"):
            nova_data = st.date_input("Data", value=df.loc[index, 'Data'], key="edit_data")
            nova_receita = st.number_input("Receita", value=float(df.loc[index, 'Receita']), key="edit_receita")
            nova_km = st.number_input("KM", value=float(df.loc[index, 'KM']), key="edit_km")
            nova_despesa = (nova_km / 10) * 5.89
            nova_obs = st.text_input("Observações", value=df.loc[index, 'Obs'], key="edit_obs")
            confirm = st.form_submit_button("Salvar alterações")
            if confirm:
                df.loc[index] = [nova_data, nova_receita, nova_despesa, nova_km, nova_obs]
                save_data(df)
                st.success("Registro atualizado com sucesso!")

st.markdown("---")

# Tabela e resumo
st.subheader("📋 Tabela de Corridas")
st.dataframe(df.drop(columns=['Data_str']) if not df.empty else pd.DataFrame())

st.subheader("📋 Tabela de Despesas Extras")
st.dataframe(despesas_extras if not despesas_extras.empty else pd.DataFrame())
