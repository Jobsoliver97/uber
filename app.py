import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def carregar_csv(caminho, colunas):
    try:
        df = pd.read_csv(caminho)
    except FileNotFoundError:
        df = pd.DataFrame(columns=colunas)
    return df

def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)

corridas = carregar_csv("corridas.csv", ["data", "valor", "descricao", "km"])
despesas = carregar_csv("despesas_extras.csv", ["data", "valor", "descricao"])
metas = carregar_csv("metas.csv", ["meta"])
receitas = carregar_csv("receitas.csv", ["data", "valor", "descricao"])

st.sidebar.title("Menu")
pagina = st.sidebar.radio("Ir para:", ["Resumo Geral", "Nova Corrida", "Despesas Extras", "Receitas Manuais", "Metas", "Tabelas", "Gráficos"])

st.sidebar.markdown("### Configurações de Consumo")
consumo_medio = st.sidebar.number_input("Consumo médio (km/L)", value=10)
preco_gasolina = st.sidebar.number_input("Preço da gasolina (R$/L)", value=5.89)

if pagina == "Resumo Geral":
    st.title("Resumo Geral")
    ganhos_corridas = corridas["valor"].sum()
    ganhos_receitas = receitas["valor"].sum()
    gastos = despesas["valor"].sum()
    lucro = ganhos_corridas + ganhos_receitas - gastos
    st.metric("Ganhos (Corridas)", f"R$ {ganhos_corridas:.2f}")
    st.metric("Ganhos (Manuais)", f"R$ {ganhos_receitas:.2f}")
    st.metric("Gastos Totais", f"R$ {gastos:.2f}")
    st.metric("Lucro Líquido", f"R$ {lucro:.2f}")
    km_total = corridas["km"].sum()
    gasto_estimado = (km_total / consumo_medio) * preco_gasolina if km_total else 0
    st.metric("KM Rodados", f"{km_total:.2f} km")
    st.metric("Gasto com Gasolina (estimado)", f"R$ {gasto_estimado:.2f}")

elif pagina == "Nova Corrida":
    st.title("Adicionar Nova Corrida")
    with st.form("nova_corrida"):
        data = st.date_input("Data", value=datetime.today())
        valor = st.number_input("Valor recebido (R$)", min_value=0.0, step=0.5)
        km = st.number_input("Quilômetros rodados", min_value=0.0, step=0.1)
        descricao = st.text_input("Descrição")
        submit = st.form_submit_button("Salvar")
        if submit:
            nova = pd.DataFrame([[data, valor, descricao, km]], columns=["data", "valor", "descricao", "km"])
            corridas = pd.concat([corridas, nova], ignore_index=True)
            salvar_csv(corridas, "corridas.csv")
            st.success("Corrida salva com sucesso!")

elif pagina == "Despesas Extras":
    st.title("Adicionar Despesa Extra")
    with st.form("nova_despesa"):
        data = st.date_input("Data", value=datetime.today(), key="despesa_data")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.5, key="despesa_valor")
        descricao = st.text_input("Descrição", key="despesa_desc")
        submit = st.form_submit_button("Salvar")
        if submit:
            nova = pd.DataFrame([[data, valor, descricao]], columns=["data", "valor", "descricao"])
            despesas = pd.concat([despesas, nova], ignore_index=True)
            salvar_csv(despesas, "despesas_extras.csv")
            st.success("Despesa salva com sucesso!")

elif pagina == "Receitas Manuais":
    st.title("Adicionar Receita Manual")
    with st.form("nova_receita"):
        data = st.date_input("Data", value=datetime.today(), key="receita_data")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.5, key="receita_valor")
        descricao = st.text_input("Descrição", key="receita_desc")
        submit = st.form_submit_button("Salvar")
        if submit:
            nova = pd.DataFrame([[data, valor, descricao]], columns=["data", "valor", "descricao"])
            receitas = pd.concat([receitas, nova], ignore_index=True)
            salvar_csv(receitas, "receitas.csv")
            st.success("Receita salva com sucesso!")

elif pagina == "Metas":
    st.title("Meta Mensal")
    meta = metas["meta"].iloc[0] if not metas.empty else 0
    nova_meta = st.number_input("Defina sua meta de lucro mensal (R$)", value=meta, step=50)
    if st.button("Salvar Meta"):
        metas = pd.DataFrame([[nova_meta]], columns=["meta"])
        salvar_csv(metas, "metas.csv")
        st.success("Meta atualizada!")
    ganhos = corridas["valor"].sum() + receitas["valor"].sum()
    gastos = despesas["valor"].sum()
    lucro = ganhos - gastos
    progresso = lucro / nova_meta if nova_meta else 0
    st.metric("Lucro Atual", f"R$ {lucro:.2f}")
    st.progress(min(progresso, 1.0))

elif pagina == "Tabelas":
    st.title("Visualizar e Editar Dados")
    aba = st.radio("Selecione a tabela:", ["Corridas", "Despesas", "Receitas"])
    if aba == "Corridas":
        st.subheader("Corridas")
        edit_corridas = st.data_editor(corridas, num_rows="dynamic", use_container_width=True)
        if st.button("Salvar Corridas Editadas"):
            salvar_csv(edit_corridas, "corridas.csv")
            st.success("Corridas atualizadas com sucesso!")
    elif aba == "Despesas":
        st.subheader("Despesas Extras")
        edit_despesas = st.data_editor(despesas, num_rows="dynamic", use_container_width=True)
        if st.button("Salvar Despesas Editadas"):
            salvar_csv(edit_despesas, "despesas_extras.csv")
            st.success("Despesas atualizadas com sucesso!")
    elif aba == "Receitas":
        st.subheader("Receitas Manuais")
        edit_receitas = st.data_editor(receitas, num_rows="dynamic", use_container_width=True)
        if st.button("Salvar Receitas Editadas"):
            salvar_csv(edit_receitas, "receitas.csv")
            st.success("Receitas atualizadas com sucesso!")

elif pagina == "Gráficos":
    st.title("Gráficos de Desempenho")
    if not corridas.empty:
        corridas["data"] = pd.to_datetime(corridas["data"])
        corridas["semana"] = corridas["data"].dt.isocalendar().week
        semanal = corridas.groupby("semana").sum(numeric_only=True).reset_index()
        fig = px.bar(semanal, x="semana", y="valor", title="Ganhos por Semana", text_auto=True)
        if not metas.empty:
            meta = metas["meta"].iloc[0]
            fig.add_hline(y=meta / 4, line_dash="dash", line_color="red", annotation_text="Meta semanal", annotation_position="top right")
        st.plotly_chart(fig)
        corridas["custo_estimado"] = (corridas["km"] / consumo_medio) * preco_gasolina
        fig2 = px.bar(corridas, x="data", y="custo_estimado", hover_data=["descricao", "km", "valor"], title="Gasto estimado com combustível por corrida", text_auto=".2f")
        st.plotly_chart(fig2)
        corridas["lucro_liquido"] = corridas["valor"] - corridas["custo_estimado"]
        fig3 = px.bar(corridas, x="data", y="lucro_liquido", hover_data=["descricao", "km", "valor", "custo_estimado"], title="Lucro líquido por corrida", text_auto=".2f", color="lucro_liquido")
        st.plotly_chart(fig3)
    else:
        st.info("Nenhuma corrida registrada ainda.")
