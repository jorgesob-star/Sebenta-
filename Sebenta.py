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
    st.session_state.setdefault(key, val)

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
# Função de cálculo otimizada
# -------------------------------
def calcular_lucro(earnings, custos, comissao_pct, extra_expenses=0.0):
    total_custos = custos + extra_expenses
    comissao_valor = earnings * (comissao_pct / 100)
    lucro_liquido = earnings - total_custos - comissao_valor
    return lucro_liquido, comissao_valor

def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type):
    resultados = {}
    detalhes = []

    extra = st.session_state.extra_expenses if st.session_state.include_extra_expenses else 0.0

    if calculation_type in ["próprio", "comparar"]:
        custos = st.session_state.own_insurance + st.session_state.own_maintenance + st.session_state.own_slot_tvde + fuel_cost
        lucro, comissao_valor = calcular_lucro(weekly_earnings, custos, st.session_state.own_commission, extra)
        resultados["Carro Próprio"] = lucro
        detalhes.append({
            "Opção": "Carro Próprio",
            "Seguro (€)": st.session_state.own_insurance,
            "Manutenção (€)": st.session_state.own_maintenance,
            "Slot TVDE (€)": st.session_state.own_slot_tvde,
            "Combustível (€)": fuel_cost,
            "Despesas Extras (€)": extra,
            "Comissão (%)": st.session_state.own_commission,
            "Comissão (€)": comissao_valor,
            "Lucro Líquido (€)": lucro
        })

    if calculation_type in ["alugado", "comparar"]:
        custos = st.session_state.rental_cost + fuel_cost
        lucro, comissao_valor = calcular_lucro(weekly_earnings, custos, st.session_state.rental_commission, extra)
        resultados["Carro Alugado"] = lucro
        detalhes.append({
            "Opção": "Carro Alugado",
            "Aluguel (€)": st.session_state.rental_cost,
            "Combustível (€)": fuel_cost,
            "Despesas Extras (€)": extra,
            "Comissão (%)": st.session_state.rental_commission,
            "Comissão (€)": comissao_valor,
            "Lucro Líquido (€)": lucro
        })

    return resultados, detalhes

# -------------------------------
# Botões mobile-first
# -------------------------------
st.header("🧮 Calcular")

btn_cols = st.columns(3, gap="small")
with btn_cols[0]:
    if st.button("🚘 Alugado", use_container_width=True):
        st.session_state.calculation_type = "alugado"
with btn_cols[1]:
    if st.button("🚗 Próprio", use_container_width=True):
        st.session_state.calculation_type = "próprio"
with btn_cols[2]:
    if st.button("⚖️ Comparar", use_container_width=True):
        st.session_state.calculation_type = "comparar"

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

    # Gráfico Altair responsivo
    theme = st.get_option("theme.base")
    colors = {"dark": ["#FFB347", "#1E90FF"], "light": ["#FF7F50", "#6495ED"]}
    bar_colors = alt.Scale(domain=list(resultados.keys()), range=colors.get(theme, colors["light"]))

    if len(resultados) > 1:
        df_chart = pd.DataFrame({
            "Opção": list(resultados.keys()),
            "Lucro (€)": list(resultados.values())
        })
        chart = alt.Chart(df_chart).mark_bar(size=60).encode(
            x=alt.X("Opção", sort=None),
            y="Lucro (€)",
            color=alt.Color("Opção", scale=bar_colors),
            tooltip=["Opção", "Lucro (€)"]
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
