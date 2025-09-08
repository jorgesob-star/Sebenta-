import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Comparador de Ganhos TVDE",
    page_icon="🚗",
    layout="wide"
)

# Título da aplicação
st.title("🚗 Comparador de Ganhos TVDE")
st.markdown("Compare os lucros entre usar carro alugado e carro próprio para trabalhar como motorista TVDE.")

# ---
# Inicialização dos parâmetros no session_state
# ---

if 'show_params' not in st.session_state:
    st.session_state.show_params = False
if 'rental_cost' not in st.session_state:
    st.session_state.rental_cost = 270.0
if 'rental_commission' not in st.session_state:
    st.session_state.rental_commission = 6.0
if 'own_insurance' not in st.session_state:
    st.session_state.own_insurance = 45.0
if 'own_maintenance' not in st.session_state:
    st.session_state.own_maintenance = 15.0
if 'own_commission' not in st.session_state:
    st.session_state.own_commission = 12.0
if 'extra_expenses' not in st.session_state:
    st.session_state.extra_expenses = 0.0
if 'include_extra_expenses' not in st.session_state:
    st.session_state.include_extra_expenses = False
if 'calculation_type' not in st.session_state:
    st.session_state.calculation_type = None

# ---
# Entrada de dados
# ---

col1, col2 = st.columns(2)
with col1:
    st.header("📊 Dados de Entrada")
    
    weekly_earnings = st.number_input(
        "Ganhos Semanais (€):", 
        min_value=0.0, 
        value=1000.0, 
        step=50.0,
        help="Valor total ganho por semana antes de despesas"
    )
    
    fuel_cost = st.number_input(
        "Custo Semanal com Combustível (€):", 
        min_value=0.0, 
        value=250.0, 
        step=10.0,
        help="Custo semanal estimado com combustível"
    )

    weekly_hours = st.number_input(
        "Horas Trabalhadas por Semana:", 
        min_value=0.0, 
        value=56.0, 
        step=1.0,
        help="Total de horas trabalhadas na semana"
    )

# Despesas extras
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

# Parâmetros avançados
if st.button("⚙️ Parâmetros Avançados"):
    st.session_state.show_params = not st.session_state.show_params

if st.session_state.show_params:
    st.header("⚙️ Parâmetros Avançados")
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
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

# ---
# Botões de cálculo
# ---

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

# ---
# Função de cálculo
# ---

def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type):
    resultados = {}
    
    if calculation_type in ["alugado", "comparar"]:
        rental_commission_value = weekly_earnings * (st.session_state.rental_commission / 100)
        rental_net_before_extras = weekly_earnings - rental_commission_value - st.session_state.rental_cost - fuel_cost
        rental_hourly = rental_net_before_extras / weekly_hours if weekly_hours > 0 else 0
        rental_net_final = rental_net_before_extras - st.session_state.extra_expenses if st.session_state.include_extra_expenses else rental_net_before_extras
        resultados["alugado"] = {
            "líquido": rental_net_final,
            "antes_extras": rental_net_before_extras,
            "hora": rental_hourly,
            "comissao": rental_commission_value
        }
    
    if calculation_type in ["próprio", "comparar"]:
        own_commission_value = weekly_earnings * (st.session_state.own_commission / 100)
        own_net_before_extras = weekly_earnings - own_commission_value - st.session_state.own_insurance - st.session_state.own_maintenance - fuel_cost
        own_hourly = own_net_before_extras / weekly_hours if weekly_hours > 0 else 0
        own_net_final = own_net_before_extras - st.session_state.extra_expenses if st.session_state.include_extra_expenses else own_net_before_extras
        resultados["próprio"] = {
            "líquido": own_net_final,
            "antes_extras": own_net_before_extras,
            "hora": own_hourly,
            "comissao": own_commission_value
        }
    
    if calculation_type == "comparar" and "alugado" in resultados and "próprio" in resultados:
        resultados["diferença"] = resultados["alugado"]["líquido"] - resultados["próprio"]["líquido"]
        resultados["diferença_hora"] = resultados["alugado"]["hora"] - resultados["próprio"]["hora"]
    
    return resultados

# ---
# Exibir resultados
# ---

if st.session_state.calculation_type:
    resultados = calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, st.session_state.calculation_type)

    st.header("📈 Resultados")
    
    # Carro Alugado
    if st.session_state.calculation_type in ["alugado", "comparar"] and "alugado" in resultados:
        alugado = resultados["alugado"]
        st.subheader("Carro Alugado")
        detalhes_alugado = {
            "Descrição": [
                "Ganhos Semanais",
                f"Comissão ({st.session_state.rental_commission}%)",
                "Custo do Aluguel",
                "Custo com Combustível",
                "Subtotal (antes de despesas extras)",
            ],
            "Valor (€)": [
                weekly_earnings,
                -alugado['comissao'],
                -st.session_state.rental_cost,
                -fuel_cost,
                alugado['antes_extras'],
            ]
        }
        if st.session_state.include_extra_expenses:
            detalhes_alugado["Descrição"].append("Despesas Extras")
            detalhes_alugado["Valor (€)"].append(-st.session_state.extra_expenses)
        detalhes_alugado["Descrição"].append("Total Líquido Final")
        detalhes_alugado["Valor (€)"].append(alugado['líquido'])
        detalhes_alugado["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
        detalhes_alugado["Valor (€)"].extend([weekly_hours, alugado['hora']])
        st.dataframe(pd.DataFrame(detalhes_alugado), use_container_width=True, hide_index=True)
    
    # Carro Próprio
    if st.session_state.calculation_type in ["próprio", "comparar"] and "próprio" in resultados:
        proprio = resultados["próprio"]
        st.subheader("Carro Próprio")
        detalhes_proprio = {
            "Descrição": [
                "Ganhos Semanais",
                f"Comissão ({st.session_state.own_commission}%)",
                "Seguro",
                "Manutenção",
                "Custo com Combustível",
                "Subtotal (antes de despesas extras)",
            ],
            "Valor (€)": [
                weekly_earnings,
                -proprio['comissao'],
                -st.session_state.own_insurance,
                -st.session_state.own_maintenance,
                -fuel_cost,
                proprio['antes_extras'],
            ]
        }
        if st.session_state.include_extra_expenses:
            detalhes_proprio["Descrição"].append("Despesas Extras")
            detalhes_proprio["Valor (€)"].append(-st.session_state.extra_expenses)
        detalhes_proprio["Descrição"].append("Total Líquido Final")
        detalhes_proprio["Valor (€)"].append(proprio['líquido'])
        detalhes_proprio["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
        detalhes_proprio["Valor (€)"].extend([weekly_hours, proprio['hora']])
        st.dataframe(pd.DataFrame(detalhes_proprio), use_container_width=True, hide_index=True)
    
    # Comparação
    if st.session_state.calculation_type == "comparar":
        st.subheader("Comparação Visual")
        chart_data_weekly = pd.DataFrame({
            "Opção": ["Carro Alugado", "Carro Próprio"],
            "Lucro Líquido Semanal (€)": [alugado['líquido'], proprio['líquido']]
        })
        chart_data_hourly = pd.DataFrame({
            "Opção": ["Carro Alugado", "Carro Próprio"],
            "Média Horária (€)": [alugado['hora'], proprio['hora']]
        })
        tab1, tab2 = st.tabs(["Lucro Semanal", "Média Horária"])
        with tab1:
            st.bar_chart(chart_data_weekly, x="Opção", y="Lucro Líquido Semanal (€)")
        with tab2:
            st.bar_chart(chart_data_hourly, x="Opção", y="Média Horária (€)")
        
        st.subheader("Recomendação")
        if resultados['diferença'] > 0.01:
            st.success(f"✅ O carro alugado é mais vantajoso por € {resultados['diferença']:.2f} por semana.")
        elif resultados['diferença'] < -0.01:
            st.success(f"✅ O carro próprio é mais vantajoso por € {abs(resultados['diferença']):.2f} por semana.")
        else:
            st.info("ℹ️ Ambas as opções têm o mesmo resultado financeiro.")

# ---
# Rodapé e dicas
# ---

with st.expander("💡 Dicas e Informações"):
    st.markdown("""
    - **Ganhos Semanais**: Valor total que você recebe pelos serviços de TVDE em uma semana.
    - **Horas Trabalhadas**: Total de horas trabalhadas na semana (incluindo tempo de espera).
    - **Custo com Combustível**: Gasto semanal estimado com abastecimento.
    - **Comissão**: Percentual que a plataforma retém pelos serviços.
    - **Custo do Aluguel**: Valor semanal pelo aluguel do veículo (se aplicável).
    - **Seguro**: Custo semanal do seguro do veículo próprio.
    - **Manutenção**: Custo semanal estimado com manutenção do veículo próprio.
    - **Despesas Extras**: Custos adicionais como estacionamento, portagens, lavagens, etc.
                
    ⚠️ Notas importantes:
    - As médias horárias são calculadas SEM incluir as despesas extras
    - As despesas extras são aplicadas apenas no lucro final
    - Considere outros custos não incluídos aqui, como desvalorização do veículo e impostos
    """)

st.markdown("---")
st.caption("Desenvolvido para ajudar motoristas TVDE a tomar decisões financeiras informadas.")
