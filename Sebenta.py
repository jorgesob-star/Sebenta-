import streamlit as st
import pandas as pd

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(
    page_title="Comparador de Ganhos TVDE",
    page_icon="🚗",
    layout="wide"
)

# -------------------------------
# Título da aplicação
# -------------------------------
st.title("🚗 Comparador de Ganhos TVDE")
st.markdown("Compare os lucros entre usar carro alugado e carro próprio para trabalhar como motorista TVDE.")

# -------------------------------
# Lógica de Inicialização dos Parâmetros
# -------------------------------
if 'show_params' not in st.session_state:
    st.session_state.show_params = False
if 'rental_cost' not in st.session_state:
    st.session_state.rental_cost = 270.0
if 'rental_commission' not in st.session_state:
    st.session_state.rental_commission = 6.0
if 'own_insurance' not in st.session_state:
    st.session_state.own_insurance = 45.0
if 'own_maintenance' not in st.session_state:
    st.session_state.own_maintenance = 25.0
if 'own_commission' not in st.session_state:
    st.session_state.own_commission = 6.0
if 'own_slot_tvde' not in st.session_state:     # <-- Novo parâmetro
    st.session_state.own_slot_tvde = 25.0       # valor inicial (exemplo)
if 'extra_expenses' not in st.session_state:
    st.session_state.extra_expenses = 0.0
if 'include_extra_expenses' not in st.session_state:
    st.session_state.include_extra_expenses = False
if 'calculation_type' not in st.session_state:
    st.session_state.calculation_type = None

# -------------------------------
# Seção de Entrada de Dados e Parâmetros
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Dados de Entrada")
    weekly_earnings = st.number_input(
        "Ganhos Semanais (€):",
        min_value=0.0,
        value=700.0,
        step=10.0,
        help="Valor total recebido pelos serviços TVDE na semana"
    )
    weekly_hours = st.number_input(
        "Horas Trabalhadas na Semana:",
        min_value=0,
        value=50,
        step=1,
        help="Total de horas trabalhadas (incluindo espera)"
    )
    fuel_cost = st.number_input(
        "Custo com Combustível (€):",
        min_value=0.0,
        value=200.0,
        step=5.0,
        help="Gasto semanal estimado com combustível"
    )

# Despesas extras (fora dos parâmetros, sempre visíveis)
st.header("💸 Despesas Extras")

extra_col1, extra_col2 = st.columns(2)

with extra_col1:
    st.session_state.include_extra_expenses = st.checkbox(
        "Incluir despesas extras no cálculo",
        value=st.session_state.include_extra_expenses,
        help="Marque para incluir despesas extras no cálculo do lucro final"
    )

with extra_col2:
    if st.session_state.include_extra_expenses:
        st.session_state.extra_expenses = st.number_input(
            "Despesas Extras Semanais (€):",
            min_value=0.0,
            value=st.session_state.extra_expenses,
            step=5.0,
            help="Despesas adicionais como estacionamento, portagens, lavagens, etc."
        )

# Botão para mostrar/ocultar parâmetros
if st.button("⚙️ Parâmetros Avançados"):
    st.session_state.show_params = not st.session_state.show_params

# Mostrar parâmetros apenas se show_params for True
if st.session_state.show_params:
    st.header("⚙️ Parâmetros Avançados")

    st.subheader("Carro Alugado")
    st.number_input("Custo Aluguel (€)", min_value=0.0, value=st.session_state.rental_cost, step=10.0, key="rental_cost")
    st.number_input("Comissão (%)", min_value=0.0, value=st.session_state.rental_commission, step=0.5, key="rental_commission")

    st.subheader("Carro Próprio")
    st.number_input("Seguro (€)", min_value=0.0, value=st.session_state.own_insurance, step=5.0, key="own_insurance")
    st.number_input("Manutenção (€)", min_value=0.0, value=st.session_state.own_maintenance, step=5.0, key="own_maintenance")
    st.number_input("Comissão (%)", min_value=0.0, value=st.session_state.own_commission, step=0.5, key="own_commission")
    st.number_input("Slot TVDE (€)", min_value=0.0, value=st.session_state.own_slot_tvde, step=5.0, key="own_slot_tvde")  # <-- Novo campo editável

# -------------------------------
# Botões de Cálculo
# -------------------------------
st.header("🧮 Calcular")

calc_col1, calc_col2, calc_col3 = st.columns(3)

with calc_col1:
    if st.button("Calcular Carro Alugado", type="primary", use_container_width=True):
        st.session_state.calculation_type = "alugado"

with calc_col2:
    if st.button("Calcular Carro Próprio", type="primary", use_container_width=True):
        st.session_state.calculation_type = "próprio"

with calc_col3:
    if st.button("Comparar Ambos", type="primary", use_container_width=True):
        st.session_state.calculation_type = "comparar"

# -------------------------------
# Seção de Cálculos
# -------------------------------
def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type):
    resultados = {}

    if calculation_type == "próprio":
        custos = (
            st.session_state.own_insurance
            + st.session_state.own_maintenance
            + st.session_state.own_slot_tvde   # <-- Slot TVDE incluído no cálculo
            + fuel_cost
        )
        if st.session_state.include_extra_expenses:
            custos += st.session_state.extra_expenses

        comissao = weekly_earnings * (st.session_state.own_commission / 100)
        lucro = weekly_earnings - custos - comissao
        resultados["Carro Próprio"] = lucro

    elif calculation_type == "alugado":
        custos = (
            st.session_state.rental_cost
            + fuel_cost
        )
        if st.session_state.include_extra_expenses:
            custos += st.session_state.extra_expenses

        comissao = weekly_earnings * (st.session_state.rental_commission / 100)
        lucro = weekly_earnings - custos - comissao
        resultados["Carro Alugado"] = lucro

    elif calculation_type == "comparar":
        # Carro próprio
        custos_proprio = (
            st.session_state.own_insurance
            + st.session_state.own_maintenance
            + st.session_state.own_slot_tvde
            + fuel_cost
        )
        if st.session_state.include_extra_expenses:
            custos_proprio += st.session_state.extra_expenses

        comissao_proprio = weekly_earnings * (st.session_state.own_commission / 100)
        lucro_proprio = weekly_earnings - custos_proprio - comissao_proprio

        # Carro alugado
        custos_alugado = (
            st.session_state.rental_cost
            + fuel_cost
        )
        if st.session_state.include_extra_expenses:
            custos_alugado += st.session_state.extra_expenses

        comissao_alugado = weekly_earnings * (st.session_state.rental_commission / 100)
        lucro_alugado = weekly_earnings - custos_alugado - comissao_alugado

        resultados["Carro Próprio"] = lucro_proprio
        resultados["Carro Alugado"] = lucro_alugado

    return resultados

# Executar cálculos se algum botão foi pressionado
if st.session_state.calculation_type:
    resultados = calcular_ganhos(
        weekly_earnings=weekly_earnings,
        weekly_hours=weekly_hours,
        fuel_cost=fuel_cost,
        calculation_type=st.session_state.calculation_type
    )
    st.write("📊 Resultados:", resultados)

# -------------------------------
# Informações Adicionais e Rodapé
# -------------------------------
with st.expander("💡 Dicas e Informações"):
    st.markdown("""
    - Ganhos Semanais: Valor total que você recebe pelos serviços de TVDE em uma semana.  
    - Horas Trabalhadas: Total de horas trabalhadas na semana (incluindo tempo de espera).  
    - Custo com Combustível: Gasto semanal estimado com abastecimento.  
    - Comissão: Percentual que a plataforma retém pelos serviços.  
    - Custo do Aluguel: Valor semanal pelo aluguel do veículo (se aplicável).  
    - Seguro: Custo semanal do seguro do veículo próprio.  
    - Manutenção: Custo semanal estimado com manutenção do veículo próprio.  
    - Slot TVDE: Custo semanal da licença TVDE (sempre fixo no carro próprio, editável pelo utilizador).  
    - Despesas Extras: Custos adicionais como estacionamento, portagens, lavagens, etc.  
    """)
