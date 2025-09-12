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
# Botões de cálculo
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
    btn1, btn2, btn3 = st.columns([1,1,1], gap="small")
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
    if calculation_type in ["próprio", "comparar"]:
        custos = st.session_state.own_insurance + st.session_state.own_maintenance + st.session_state.own_slot_tvde + fuel_cost
        if st.session_state.include_extra_expenses:
            custos += st.session_state.extra_expenses
        comissao = weekly_earnings * (st.session_state.own_commission / 100)
        resultados["Carro Próprio"] = weekly_earnings - custos - comissao
    if calculation_type in ["alugado", "comparar"]:
        custos = st.session_state.rental_cost + fuel_cost
        if st.session_state.include_extra_expenses:
            custos += st.session_state.extra_expenses
        comissao = weekly_earnings * (st.session_state.rental_commission / 100)
        resultados["Carro Alugado"] = weekly_earnings - custos - comissao
    return resultados

# -------------------------------
# Resultados
# -------------------------------
calculation_type = st.session_state.get("calculation_type")

if calculation_type:
    resultados = calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type)

    st.subheader("📊 Resultados")

    # Métricas
    for tipo, lucro in resultados.items():
        lucro_hora = lucro / weekly_hours if weekly_hours > 0 else 0
        st.metric(label=tipo, value=f"€ {lucro:,.2f}", delta=f"{lucro_hora:.2f} €/h")

    # Tabela detalhada
    df_resultados = pd.DataFrame({
        "Opção": list(resultados.keys()),
        "Lucro (€)": [f"{v:,.2f}" for v in resultados.values()],
        "Lucro por Hora (€)": [f"{(v/weekly_hours):,.2f}" if weekly_hours > 0 else "0.00" for v in resultados.values()]
    })
    st.dataframe(df_resultados, use_container_width=True)

    # Diferença de valor
    if calculation_type == "comparar" and len(resultados) == 2:
        lucro_proprio = resultados.get("Carro Próprio", 0)
        lucro_alugado = resultados.get("Carro Alugado", 0)
        diferenca = lucro_proprio - lucro_alugado
        st.markdown(f"**💰 Diferença entre Carro Próprio e Carro Alugado:** € {diferenca:,.2f}")

    # Cores automáticas
    theme = st.get_option("theme.base")
    if theme == "dark":
        bar_colors = alt.Scale(domain=["Carro Próprio", "Carro Alugado"], range=["#FFB347", "#1E90FF"])
    else:
        bar_colors = alt.Scale(domain=["Carro Próprio", "Carro Alugado"], range=["#FF7F50", "#6495ED"])

    # Gráfico comparativo com anotação
    if len(resultados) > 1:
        df_chart = pd.DataFrame({"Opção": list(resultados.keys()), "Lucro (€)": list(resultados.values())})

        chart = alt.Chart(df_chart).mark_bar(size=60).encode(
            x=alt.X("Opção", sort=None),
            y="Lucro (€)",
            color=alt.Color("Opção", scale=bar_colors)
        ).properties(height=300)

        if calculation_type == "comparar" and len(resultados) == 2:
            y_pos = max(resultados.values()) + 10
            diferenca_text = f"Δ € {diferenca:,.2f}"
            annotation = alt.Chart(pd.DataFrame({"y": [y_pos], "text": [diferenca_text]})).mark_text(
                align='center', baseline='bottom', color='black', fontWeight='bold'
            ).encode(
                x=alt.value(200),  # posição fixa para evitar TypeError
                y='y:Q',
                text='text:N'
            )
            st.altair_chart(chart + annotation, use_container_width=True)
        else:
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
