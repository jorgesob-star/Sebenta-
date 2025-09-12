# -------------------------------
# Imports
# -------------------------------
import streamlit as st
import pandas as pd
import altair as alt

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(
    page_title="Comparador de Ganhos TVDE",
    page_icon="🚗",
    layout="wide"
)

# -------------------------------
# Inicialização do estado
# -------------------------------
defaults = {
    "rental_cost": 250.0,
    "rental_commission": 6.0,
    "own_insurance": 45.0,
    "own_maintenance": 25.0,
    "own_commission": 6.0,
    "own_slot_tvde": 25.0,
    "extra_expenses": 0.0,
    "include_extra_expenses": False,
    "calculation_type": None,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------
# Título
# -------------------------------
st.title("🚗 Comparador de Ganhos TVDE")
st.markdown("Compare os lucros entre carro alugado e carro próprio.")

# -------------------------------
# Dados de entrada
# -------------------------------
st.header("📊 Dados de Entrada")
weekly_earnings = st.number_input("Ganhos Semanais (€)", min_value=0.0, value=700.0, step=10.0)
weekly_hours = st.number_input("Horas Semanais", min_value=0, value=50, step=1)
fuel_cost = st.number_input("Combustível (€)", min_value=0.0, value=200.0, step=5.0)

# -------------------------------
# Despesas extras
# -------------------------------
st.header("💸 Despesas Extras")
st.session_state.include_extra_expenses = st.checkbox(
    "Incluir despesas extras", value=st.session_state.include_extra_expenses
)
if st.session_state.include_extra_expenses:
    st.session_state.extra_expenses = st.number_input(
        "Despesas Extras (€)",
        min_value=0.0,
        value=st.session_state.extra_expenses,
        step=5.0
    )

# -------------------------------
# Parâmetros avançados
# -------------------------------
with st.expander("⚙️ Parâmetros Avançados"):
    st.subheader("Carro Alugado")
    st.number_input("Custo Aluguel (€)", min_value=0.0, step=10.0, key="rental_cost")
    st.number_input("Comissão (%)", min_value=0.0, step=0.5, key="rental_commission")

    st.subheader("Carro Próprio")
    st.number_input("Seguro (€)", min_value=0.0, step=5.0, key="own_insurance")
    st.number_input("Manutenção (€)", min_value=0.0, step=5.0, key="own_maintenance")
    st.number_input("Comissão (%)", min_value=0.0, step=0.5, key="own_commission")
    st.number_input("Slot TVDE (€)", min_value=0.0, step=5.0, key="own_slot_tvde")

# -------------------------------
# Botões de cálculo (mobile-first)
# -------------------------------
st.header("🧮 Calcular")

screen_width = int(st.query_params.get("width", [0])[0])

if screen_width < 600:
    if st.button("🚘 Alugado", use_container_width=True):
        st.session_state.calculation_type = "alugado"
    if st.button("🚗 Próprio", use_container_width=True):
        st.session_state.calculation_type = "próprio"
    if st.button("⚖️ Comparar", use_container_width=True):
        st.session_state.calculation_type = "comparar"
else:
    btn1, btn2, btn3 = st.columns([1, 1, 1], gap="small")
    with btn1:
        if st.button("🚘 Alugado", use_container_width=True):
            st.session_state.calculation_type = "alugado"
    with btn2:
        if st.button("🚗 Próprio", use_container_width=True):
            st.session_state.calculation_type = "próprio"
    with btn3:
        if st.button("⚖️ Comparar", use_container_width=True):
            st.session_state.calculation_type = "comparar"

# -------------------------------
# Função de cálculo
# -------------------------------
def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type):
    resultados = {}
    detalhes = []

    if calculation_type in ["próprio", "comparar"]:
        seguro = st.session_state.own_insurance
        manutencao = st.session_state.own_maintenance
        slot = st.session_state.own_slot_tvde
        combustivel = fuel_cost
        comissao_valor = weekly_earnings * (st.session_state.own_commission / 100)
        custos = seguro + manutencao + slot + combustivel
        if st.session_state.include_extra_expenses:
            custos += st.session_state.extra_expenses
        lucro_liquido = weekly_earnings - custos - comissao_valor
        resultados["Carro Próprio"] = lucro_liquido

        detalhes.append({
            "Opção": "Carro Próprio",
            "Seguro (€)": seguro,
            "Manutenção (€)": manutencao,
            "Slot TVDE (€)": slot,
            "Combustível (€)": combustivel,
            "Despesas Extras (€)": st.session_state.extra_expenses if st.session_state.include_extra_expenses else 0,
            "Comissão (%)": st.session_state.own_commission,
            "Comissão (€)": comissao_valor,
            "Lucro Líquido (€)": lucro_liquido
        })

    if calculation_type in ["alugado", "comparar"]:
        aluguel = st.session_state.rental_cost
        combustivel = fuel_cost
        comissao_valor = weekly_earnings * (st.session_state.rental_commission / 100)
        custos = aluguel + combustivel
        if st.session_state.include_extra_expenses:
            custos += st.session_state.extra_expenses
        lucro_liquido = weekly_earnings - custos - comissao_valor
        resultados["Carro Alugado"] = lucro_liquido

        detalhes.append({
            "Opção": "Carro Alugado",
            "Aluguel (€)": aluguel,
            "Combustível (€)": combustivel,
            "Despesas Extras (€)": st.session_state.extra_expenses if st.session_state.include_extra_expenses else 0,
            "Comissão (%)": st.session_state.rental_commission,
            "Comissão (€)": comissao_valor,
            "Lucro Líquido (€)": lucro_liquido
        })

    return resultados, detalhes

# -------------------------------
# Resultados
# -------------------------------
if st.session_state.calculation_type:
    resultados, detalhes = calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, st.session_state.calculation_type)

    st.subheader("📊 Resultados Resumidos")
    for tipo, lucro in resultados.items():
        lucro_hora = lucro / weekly_hours if weekly_hours > 0 else 0
        st.metric(label=tipo, value=f"€ {lucro:,.2f}", delta=f"{lucro_hora:.2f} €/h")

    st.subheader("📋 Detalhamento de Custos")
    st.dataframe(pd.DataFrame(detalhes).fillna("–"), use_container_width=True)

    theme = st.get_option("theme.base")
    if theme == "dark":
        bar_colors = alt.Scale(domain=["Carro Próprio", "Carro Alugado"], range=["#FFB347", "#1E90FF"])
    else:
        bar_colors = alt.Scale(domain=["Carro Próprio", "Carro Alugado"], range=["#FF7F50", "#6495ED"])

    if len(resultados) > 1:
        df_chart = pd.DataFrame({
            "Opção": list(resultados.keys()),
            "Lucro (€)": list(resultados.values())
        })
        chart = alt.Chart(df_chart).mark_bar(size=60).encode(
            x=alt.X("Opção", sort=None),
            y="Lucro (€)",
            color=alt.Color("Opção", scale=bar_colors)
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

# -------------------------------
# Dicas
# -------------------------------
with st.expander("💡 Dicas e Informações"):
    st.markdown("""
    - **Ganhos Semanais**: valor total recebido pelos serviços TVDE.  
    - **Horas Semanais**: total de horas trabalhadas (incluindo espera).  
    - **Combustível**: gasto médio semanal.  
    - **Comissão**: taxa que a plataforma retém.  
    - **Aluguel**: custo semanal do carro alugado.  
    - **Seguro / Manutenção / Slot TVDE**: custos semanais fixos do carro próprio.  
    - **Despesas Extras**: portagens, estacionamento, lavagens, etc.  
    """)
