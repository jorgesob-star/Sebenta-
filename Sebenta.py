import streamlit as st import pandas as pd

Configuração da página

st.set_page_config( page_title="Comparador de Ganhos TVDE", page_icon="🚗", layout="wide" )

Título da aplicação

st.title("🚗 Comparador de Ganhos TVDE") st.markdown("Compare os lucros entre usar carro alugado e carro próprio para trabalhar como motorista TVDE.")

---

Lógica de Inicialização dos Parâmetros

---

Inicializa todos os parâmetros no session_state com valores padrão

if 'show_params' not in st.session_state: st.session_state.show_params = False if 'rental_cost' not in st.session_state: st.session_state.rental_cost = 270.0 if 'rental_commission' not in st.session_state: st.session_state.rental_commission = 6.0 if 'own_insurance' not in st.session_state: st.session_state.own_insurance = 45.0 if 'own_maintenance' not in st.session_state: st.session_state.own_maintenance = 25.0 if 'own_commission' not in st.session_state: st.session_state.own_commission = 12.0 if 'extra_expenses' not in st.session_state: st.session_state.extra_expenses = 0.0 if 'include_extra_expenses' not in st.session_state: st.session_state.include_extra_expenses = False if 'calculation_type' not in st.session_state: st.session_state.calculation_type = None

---

Seção de Entrada de Dados e Parâmetros

---

col1, col2 = st.columns(2)

with col1: st.header("📊 Dados de Entrada")

weekly_earnings = st.number_input(
    "Ganhos Semanais (€):", 
    min_value=0.0, 
    value=900.0, 
    step=50.0,
    help="Valor total ganho por semana antes de despesas"
)

# Primeiro combustível
fuel_cost = st.number_input(
    "Custo Semanal com Combustível (€):", 
    min_value=0.0, 
    value=210.0, 
    step=10.0,
    help="Custo semanal estimado com combustível"
)

# Depois horas trabalhadas
weekly_hours = st.number_input(
    "Horas Trabalhadas por Semana:", 
    min_value=0.0, 
    value=50.0, 
    step=1.0,
    help="Total de horas trabalhadas na semana"
)

Despesas extras (fora dos parâmetros, sempre visíveis)

st.header("💸 Despesas Extras")

extra_col1, extra_col2 = st.columns(2)

with extra_col1: st.session_state.include_extra_expenses = st.checkbox( "Incluir despesas extras no cálculo", value=st.session_state.include_extra_expenses, help="Marque para incluir despesas extras no cálculo do lucro final" )

with extra_col2: if st.session_state.include_extra_expenses: st.session_state.extra_expenses = st.number_input( "Despesas Extras Semanais (€):", min_value=0.0, value=st.session_state.extra_expenses, step=5.0, help="Despesas adicionais como estacionamento, portagens, lavagens, etc." )

Botão para mostrar/ocultar parâmetros

if st.button("⚙️ Parâmetros Avançados"): st.session_state.show_params = not st.session_state.show_params

Mostrar parâmetros apenas if show_params for True

if st.session_state.show_params: st.header("⚙️ Parâmetros Avançados")

adv_col1, adv_col2 = st.columns(2)

with adv_col1:
    # Parâmetros para carro alugado
    st.subheader("Carro Alugado")
    st.session_state.rental_cost = st.number_input(
        "Custo do Aluguel (€/semana):", 
        min_value=0.0, 
        value=st.session_state.rental_cost, 
        step=10.0
    )
    
    st.session_state.rental_commission = st.number_input(
        "Comissão com Carro Alugado (%):", 
        min_value=0.0, 
        max_value=30.0, 
        value=st.session_state.rental_commission, 
        step=0.5,
        help="Percentual que a plataforma retém pelos serviços com carro alugado"
    )

with adv_col2:
    # Parâmetros para carro próprio
    st.subheader("Carro Próprio")
    st.session_state.own_insurance = st.number_input(
        "Seguro (€/semana):", 
        min_value=0.0, 
        value=st.session_state.own_insurance, 
        step=5.0
    )
    
    st.session_state.own_maintenance = st.number_input(
        "Manutenção (€/semana):", 
        min_value=0.0, 
        value=st.session_state.own_maintenance, 
        step=5.0,
        help="Custo semanal estimado com manutenção do veículo próprio"
    )
    
    st.session_state.own_commission = st.number_input(
        "Comissão com Carro Próprio (%):", 
        min_value=0.0, 
        max_value=30.0, 
        value=st.session_state.own_commission, 
        step=0.5,
        help="Percentual que a plataforma retém pelos serviços com carro próprio"
    )

---

Botões de Cálculo

---

st.header("🧮 Calcular")

calc_col1, calc_col2, calc_col3 = st.columns(3)

with calc_col1: if st.button("Calcular Carro Alugado", type="primary", use_container_width=True): st.session_state.calculation_type = "alugado"

with calc_col2: if st.button("Calcular Carro Próprio", type="primary", use_container_width=True): st.session_state.calculation_type = "próprio"

with calc_col3: if st.button("Comparar Ambos", type="primary", use_container_width=True): st.session_state.calculation_type = "comparar"

---

Função de cálculos

---

def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type): resultados = {}

if calculation_type == "alugado":
    commission = (st.session_state.rental_commission / 100) * weekly_earnings
    total_expenses = fuel_cost + st.session_state.rental_cost + commission
    if st.session_state.include_extra_expenses:
        total_expenses += st.session_state.extra_expenses
    net_income = weekly_earnings - total_expenses
    hourly_income = net_income / weekly_hours if weekly_hours > 0 else 0

    resultados = {
        "Tipo": "Carro Alugado",
        "Ganhos Brutos (€)": weekly_earnings,
        "Despesas Totais (€)": total_expenses,
        "Lucro Líquido (€)": net_income,
        "Lucro por Hora (€)": hourly_income
    }

elif calculation_type == "próprio":
    commission = (st.session_state.own_commission / 100)

