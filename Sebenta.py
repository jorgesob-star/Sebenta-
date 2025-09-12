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
# Lógica de Inicialização dos Parâmetros
# ---

# Inicializa todos os parâmetros no session_state com valores padrão
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
if 'own_slot' not in st.session_state:
    st.session_state.own_slot = 0.0
if 'own_commission' not in st.session_state:
    st.session_state.own_commission = 12.0
if 'extra_expenses' not in st.session_state:
    st.session_state.extra_expenses = 0.0
if 'include_extra_expenses' not in st.session_state:
    st.session_state.include_extra_expenses = False
if 'calculation_type' not in st.session_state:
    st.session_state.calculation_type = None

# ---
# Seção de Entrada de Dados e Parâmetros
# ---

col1, col2 = st.columns(2)

with col1:
    st.header("📊 Dados de Entrada")
    
    weekly_earnings = st.number_input(
        "Ganhos Semanais (€):", 
        min_value=0.0, 
        value=900.0, 
        step=50.0,
        help="Valor total ganho por semana antes de despesas"
    )
    
    weekly_hours = st.number_input(
        "Horas Trabalhadas por Semana:", 
        min_value=0.0, 
        value=50.0, 
        step=1.0,
        help="Total de horas trabalhadas na semana"
    )
    
    fuel_cost = st.number_input(
        "Custo Semanal com Combustível (€):", 
        min_value=0.0, 
        value=210.0, 
        step=10.0,
        help="Custo semanal estimado com combustível"
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
        
        st.session_state.own_slot = st.number_input(
            "Despesas com Slot (€/semana):", 
            min_value=0.0, 
            value=st.session_state.own_slot, 
            step=5.0,
            help="Custo semanal com o aluguel do slot TVDE"
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
# Botões de Cálculo
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
# Seção de Cálculos
# ---

# Função para realizar os cálculos
def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type):
    resultados = {}
    
    # Calcular para carro alugado
    if calculation_type in ["alugado", "comparar"]:
        rental_commission_value = weekly_earnings * (st.session_state.rental_commission / 100)
        rental_net_before_extras = weekly_earnings - rental_commission_value - st.session_state.rental_cost - fuel_cost
        rental_hourly = rental_net_before_extras / weekly_hours if weekly_hours > 0 else 0
        
        # Aplicar despesas extras se selecionado
        if st.session_state.include_extra_expenses:
            rental_net_final = rental_net_before_extras - st.session_state.extra_expenses
        else:
            rental_net_final = rental_net_before_extras
        
        resultados["alugado"] = {
            "líquido": rental_net_final,
            "antes_extras": rental_net_before_extras,
            "hora": rental_hourly,
            "comissao": rental_commission_value
        }
    
    # Calcular para carro próprio
    if calculation_type in ["próprio", "comparar"]:
        own_commission_value = weekly_earnings * (st.session_state.own_commission / 100)
        own_net_before_extras = weekly_earnings - own_commission_value - st.session_state.own_insurance - st.session_state.own_maintenance - st.session_state.own_slot - fuel_cost
        own_hourly = own_net_before_extras / weekly_hours if weekly_hours > 0 else 0
        
        # Aplicar despesas extras se selecionado
        if st.session_state.include_extra_expenses:
            own_net_final = own_net_before_extras - st.session_state.extra_expenses
        else:
            own_net_final = own_net_before_extras
        
        resultados["próprio"] = {
            "líquido": own_net_final,
            "antes_extras": own_net_before_extras,
            "hora": own_hourly,
            "comissao": own_commission_value
        }
    
    # Calcular diferenças se for comparação
    if calculation_type == "comparar" and "alugado" in resultados and "próprio" in resultados:
        resultados["diferença"] = resultados["alugado"]["líquido"] - resultados["próprio"]["líquido"]
        resultados["diferença_hora"] = resultados["alugado"]["hora"] - resultados["próprio"]["hora"]
    
    return resultados

# Executar cálculos se algum botão foi pressionado
if st.session_state.calculation_type:
    resultados = calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, st.session_state.calculation_type)
    
    # ---
    # Seção de Resultados
    # ---

    st.header("📈 Resultados")
    
    # Resultado para carro alugado
    if st.session_state.calculation_type == "alugado" and "alugado" in resultados:
        alugado = resultados["alugado"]
        
        st.subheader("Carro Alugado")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Total Líquido Semanal", 
                f"€ {alugado['líquido']:.2f}",
                delta_color="inverse" if alugado['líquido'] < 0 else "normal"
            )
            
            if st.session_state.include_extra_expenses:
                st.metric(
                    "Antes das Despesas Extras", 
                    f"€ {alugado['antes_extras']:.2f}",
                    help="Valor sem considerar as despesas extras"
                )
        
        with col2:
            st.metric(
                "Média Horária", 
                f"€ {alugado['hora']:.2f}",
                delta_color="inverse" if alugado['hora'] < 0 else "normal"
            )
        
        # Detalhamento dos cálculos
        st.subheader("Detalhamento dos Cálculos - Carro Alugado")
        
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
        else:
            detalhes_alugado["Descrição"].append("Total Líquido Final")
            detalhes_alugado["Valor (€)"].append(alugado['líquido'])
        
        detalhes_alugado["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
        detalhes_alugado["Valor (€)"].extend([weekly_hours, alugado['hora']])
        
        df_alugado = pd.DataFrame(detalhes_alugado)
        st.dataframe(df_alugado, use_container_width=True, hide_index=True)
    
    # Resultado para carro próprio
    elif st.session_state.calculation_type == "próprio" and "próprio" in resultados:
        proprio = resultados["próprio"]
        
        st.subheader("Carro Próprio")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Total Líquido Semanal", 
                f"€ {proprio['líquido']:.2f}",
                delta_color="inverse" if proprio['líquido'] < 0 else "normal"
            )
            
            if st.session_state.include_extra_expenses:
                st.metric(
                    "Antes das Despesas Extras", 
                    f"€ {proprio['antes_extras']:.2f}",
                    help="Valor sem considerar as despesas extras"
                )
        
        with col2:
            st.metric(
                "Média Horária", 
                f"€ {proprio['hora']:.2f}",
                delta_color="inverse" if proprio['hora'] < 0 else "normal"
            )
        
        # Detalhamento dos cálculos
        st.subheader("Detalhamento dos Cálculos - Carro Próprio")
        
        detalhes_proprio = {
            "Descrição": [
                "Ganhos Semanais",
                f"Comissão ({st.session_state.own_commission}%)",
                "Seguro",
                "Manutenção",
                "Despesas com Slot",
                "Custo com Combustível",
                "Subtotal (antes de despesas extras)",
            ],
            "Valor (€)": [
                weekly_earnings,
                -proprio['comissao'],
                -st.session_state.own_insurance,
                -st.session_state.own_maintenance,
                -st.session_state.own_slot,
                -fuel_cost,
                proprio['antes_extras'],
            ]
        }
        
        if st.session_state.include_extra_expenses:
            detalhes_proprio["Descrição"].append("Despesas Extras")
            detalhes_proprio["Valor (€)"].append(-st.session_state.extra_expenses)
            
            detalhes_proprio["Descrição"].append("Total Líquido Final")
            detalhes_proprio["Valor (€)"].append(proprio['líquido'])
        else:
            detalhes_proprio["Descrição"].append("Total Líquido Final")
            detalhes_proprio["Valor (€)"].append(proprio['líquido'])
        
        detalhes_proprio["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
        detalhes_proprio["Valor (€)"].extend([weekly_hours, proprio['hora']])
        
        df_proprio = pd.DataFrame(detalhes_proprio)
        st.dataframe(df_proprio, use_container_width=True, hide_index=True)
    
    # Resultado para comparação
    elif st.session_state.calculation_type == "comparar" and "alugado" in resultados and "próprio" in resultados:
        alugado = resultados["alugado"]
        proprio = resultados["próprio"]
        
        # Métricas semanais
        st.subheader("Resultados Semanais")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Carro Alugado (Líquido Semanal)", 
                f"€ {alugado['líquido']:.2f}",
                delta_color="inverse" if alugado['líquido'] < 0 else "normal"
            )
            
            if st.session_state.include_extra_expenses:
                st.metric(
                    "Antes das Despesas Extras", 
                    f"€ {alugado['antes_extras']:.2f}",
                    help="Valor sem considerar as despesas extras"
                )
        
        with col2:
            st.metric(
                "Carro Próprio (Líquido Semanal)", 
                f"€ {proprio['líquido']:.2f}",
                delta_color="inverse" if proprio['líquido'] < 0 else "normal"
            )
            
            if st.session_state.include_extra_expenses:
                st.metric(
                    "Antes das Despesas Extras", 
                    f"€ {proprio['antes_extras']:.2f}",
                    help="Valor sem considerar as despesas extras"
                )
        
        with col3:
            st.metric(
                "Diferença Semanal", 
                f"€ {resultados['diferença']:.2f}",
                delta_color="inverse" if resultados['diferença'] < 0 else "normal"
            )
        
        # Métricas horárias
        st.subheader("Média Horária (sem despesas extras)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Carro Alugado (€/hora)", 
                f"€ {alugado['hora']:.2f}",
                delta_color="inverse" if alugado['hora'] < 0 else "normal"
            )
        
        with col2:
            st.metric(
                "Carro Próprio (€/hora)", 
                f"€ {proprio['hora']:.2f}",
                delta_color="inverse" if proprio['hora'] < 0 else "normal"
            )
        
        with col3:
            st.metric(
                "Diferença Horária", 
                f"€ {resultados['diferença_hora']:.2f}",
                delta_color="inverse" if resultados['diferença_hora'] < 0 else "normal"
            )
        
        # Detalhamento dos cálculos
        st.subheader("Detalhamento dos Cálculos")
        
        comparison_data = {
            "Descrição": [
                "Ganhos Semanais",
                f"Comissão ({st.session_state.rental_commission}%)",
                f"Comissão ({st.session_state.own_commission}%)",
                "Custo do Aluguel",
                "Seguro",
                "Manutenção",
                "Despesas com Slot",
                "Custo com Combustível",
                "Subtotal (antes de despesas extras)",
            ],
            "Carro Alugado (€)": [
                weekly_earnings,
                -alugado['comissao'],
                "N/A",
                -st.session_state.rental_cost,
                "N/A",
                "N/A",
                "N/A",
                -fuel_cost,
                alugado['antes_extras'],
            ],
            "Carro Próprio (€)": [
                weekly_earnings,
                "N/A",
                -proprio['comissao'],
                "N/A",
                -st.session_state.own_insurance,
                -st.session_state.own_maintenance,
                -st.session_state.own_slot,
                -fuel_cost,
                proprio['antes_extras'],
            ]
        }
        
        # Adicionar linha de despesas extras se aplicável
        if st.session_state.include_extra_expenses:
            comparison_data["Descrição"].append("Despesas Extras")
            comparison_data["Carro Alugado (€)"].append(-st.session_state.extra_expenses)
            comparison_data["Carro Próprio (€)"].append(-st.session_state.extra_expenses)
            
            comparison_data["Descrição"].append("Total Líquido Final")
            comparison_data["Carro Alugado (€)"].append(alugado['líquido'])
            comparison_data["Carro Próprio (€)"].append(proprio['líquido'])
        else:
            comparison_data["Descrição"].append("Total Líquido Final")
            comparison_data["Carro Alugado (€)"].append(alugado['líquido'])
            comparison_data["Carro Próprio (€)"].append(proprio['líquido'])
        
        # Adicionar horas e média horária
        comparison_data["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
        comparison_data["Carro Alugado (€)"].extend([weekly_hours, alugado['hora']])
        comparison_data["Carro Próprio (€)"].extend([weekly_hours, proprio['hora']])
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Recomendação
        st.subheader("Recomendação")
        if resultados['diferença'] > 0.01:
            st.success(f"✅ O carro alugado é mais vantajoso por € {resultados['diferença']:.2f} por semana.")
        elif resultados['diferença'] < -0.01:
            st.success(f"✅ O carro próprio é mais vantajoso por € {abs(resultados['diferença']):.2f} por semana.")
        else:
            st.info("ℹ️ Ambas as opções têm o mesmo resultado financeiro.")
        
        # Visualização gráfica
        st.subheader("Comparação Visual")
        
        tab1, tab2 = st.tabs(["Lucro Semanal", "Média Horária"])
        
        with tab1:
            chart_data_weekly = pd.DataFrame({
                "Opção": ["Carro Alugado", "Carro Próprio"],
                "Lucro Líquido Semanal (€)": [alugado['líquido'], proprio['líquido']]
            })
            st.bar_chart(chart_data_weekly, x="Opção", y="Lucro Líquido Semanal (€)")
        
        with tab2:
            chart_data_hourly = pd.DataFrame({
                "Opção": ["Carro Alugado", "Carro Próprio"],
                "Média Horária (€)": [alugado['hora'], proprio['hora']]
            })
            st.bar_chart(chart_data_hourly, x="Opção", y="Média Horária (€)")

# ---
# Informações Adicionais e Rodapé
# ---

with st.expander("💡 Dicas e Informações"):
    st.markdown("""
    - **Ganhos Semanais**: Valor total que você recebe pelos serviços de TVDE em uma semana.
    - **Horas Trabalhadas**: Total de horas trabalhadas na semana (incluindo temp
