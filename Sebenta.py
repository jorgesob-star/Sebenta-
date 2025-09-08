import streamlit as st
import pandas as pd
import plotly.express as px

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
default_params = {
    'show_params': False,
    'rental_cost': 270.0,
    'rental_commission': 6.0,
    'own_insurance': 45.0,
    'own_maintenance': 15.0,
    'own_commission': 12.0,
    'extra_expenses': 0.0,
    'include_extra_expenses': False,
    'calculation_type': None,
    'weekly_earnings': 1000.0,
    'weekly_hours': 56.0,
    'fuel_cost': 250.0
}

for key, value in default_params.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---
# Funções auxiliares
# ---

def reset_parameters():
    """Redefine os parâmetros para os valores padrão"""
    for key, value in default_params.items():
        if key != 'calculation_type':  # Mantém o tipo de cálculo atual
            st.session_state[key] = value
    st.success("Parâmetros redefinidos para os valores padrão!")

def validate_inputs():
    """Valida se os inputs são válidos antes do cálculo"""
    errors = []
    
    if st.session_state.weekly_earnings <= 0:
        errors.append("Os ganhos semanais devem ser maiores que zero")
    
    if st.session_state.weekly_hours <= 0:
        errors.append("As horas trabalhadas devem ser maiores que zero")
    
    if st.session_state.fuel_cost < 0:
        errors.append("O custo do combustível não pode ser negativo")
    
    if st.session_state.rental_cost < 0:
        errors.append("O custo do aluguel não pode ser negativo")
    
    if st.session_state.rental_commission < 0 or st.session_state.rental_commission > 100:
        errors.append("A comissão com carro alugado deve estar entre 0% e 100%")
    
    if st.session_state.own_commission < 0 or st.session_state.own_commission > 100:
        errors.append("A comissão com carro próprio deve estar entre 0% e 100%")
    
    if st.session_state.own_insurance < 0:
        errors.append("O seguro não pode ser negativo")
    
    if st.session_state.own_maintenance < 0:
        errors.append("A manutenção não pode ser negativa")
    
    if st.session_state.extra_expenses < 0:
        errors.append("As despesas extras não podem ser negativas")
    
    return errors

def calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, calculation_type):
    """Realiza os cálculos de ganhos para os cenários selecionados"""
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
        own_net_before_extras = weekly_earnings - own_commission_value - st.session_state.own_insurance - st.session_state.own_maintenance - fuel_cost
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

# ---
# Seção de Entrada de Dados e Parâmetros
# ---

col1, col2 = st.columns(2)

with col1:
    st.header("📊 Dados de Entrada")
    
    st.session_state.weekly_earnings = st.number_input(
        "Ganhos Semanais (€):", 
        min_value=0.0, 
        value=st.session_state.weekly_earnings, 
        step=50.0,
        help="Valor total ganho por semana antes de despesas",
        key="earnings_input"
    )
    
    st.session_state.weekly_hours = st.number_input(
        "Horas Trabalhadas por Semana:", 
        min_value=0.0, 
        value=st.session_state.weekly_hours, 
        step=1.0,
        help="Total de horas trabalhadas na semana",
        key="hours_input"
    )
    
    st.session_state.fuel_cost = st.number_input(
        "Custo Semanal com Combustível (€):", 
        min_value=0.0, 
        value=st.session_state.fuel_cost, 
        step=10.0,
        help="Custo semanal estimado com combustível",
        key="fuel_input"
    )

# Despesas extras (fora dos parâmetros, sempre visíveis)
st.header("💸 Despesas Extras")

extra_col1, extra_col2 = st.columns(2)

with extra_col1:
    st.session_state.include_extra_expenses = st.checkbox(
        "Incluir despesas extras no cálculo",
        value=st.session_state.include_extra_expenses,
        help="Marque para incluir despesas extras no cálculo do lucro final",
        key="extra_checkbox"
    )

with extra_col2:
    if st.session_state.include_extra_expenses:
        st.session_state.extra_expenses = st.number_input(
            "Despesas Extras Semanais (€):", 
            min_value=0.0, 
            value=st.session_state.extra_expenses, 
            step=5.0,
            help="Despesas adicionais como estacionamento, portagens, lavagens, etc.",
            key="extra_expenses_input"
        )

# Botões para parâmetros avançados e reset
param_col1, param_col2 = st.columns(2)

with param_col1:
    if st.button("⚙️ Parâmetros Avançados", use_container_width=True):
        st.session_state.show_params = not st.session_state.show_params

with param_col2:
    if st.button("🔄 Redefinir Parâmetros", use_container_width=True):
        reset_parameters()

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
            step=10.0,
            key="rental_cost_input"
        )
        
        st.session_state.rental_commission = st.number_input(
            "Comissão com Carro Alugado (%):", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.rental_commission, 
            step=0.5,
            help="Percentual que a plataforma retém pelos serviços com carro alugado",
            key="rental_commission_input"
        )
    
    with adv_col2:
        # Parâmetros para carro próprio
        st.subheader("Carro Próprio")
        st.session_state.own_insurance = st.number_input(
            "Seguro (€/semana):", 
            min_value=0.0, 
            value=st.session_state.own_insurance, 
            step=5.0,
            key="insurance_input"
        )
        
        st.session_state.own_maintenance = st.number_input(
            "Manutenção (€/semana):", 
            min_value=0.0, 
            value=st.session_state.own_maintenance, 
            step=5.0,
            help="Custo semanal estimado com manutenção do veículo próprio",
            key="maintenance_input"
        )
        
        st.session_state.own_commission = st.number_input(
            "Comissão com Carro Próprio (%):", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.own_commission, 
            step=0.5,
            help="Percentual que a plataforma retém pelos serviços com carro próprio",
            key="own_commission_input"
        )

# ---
# Botões de Cálculo
# ---

st.header("🧮 Calcular")

calc_col1, calc_col2, calc_col3 = st.columns(3)

with calc_col1:
    if st.button("Calcular Carro Alugado", type="primary", use_container_width=True):
        errors = validate_inputs()
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state.calculation_type = "alugado"

with calc_col2:
    if st.button("Calcular Carro Próprio", type="primary", use_container_width=True):
        errors = validate_inputs()
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state.calculation_type = "próprio"

with calc_col3:
    if st.button("Comparar Ambos", type="primary", use_container_width=True):
        errors = validate_inputs()
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state.calculation_type = "comparar"

# ---
# Seção de Resultados
# ---

# Executar cálculos se algum botão foi pressionado
if st.session_state.calculation_type:
    resultados = calcular_ganhos(
        st.session_state.weekly_earnings, 
        st.session_state.weekly_hours, 
        st.session_state.fuel_cost, 
        st.session_state.calculation_type
    )
    
    st.header("📈 Resultados")
    
    # Resultado para carro alugado
    if st.session_state.calculation_type == "alugado" and "alugado" in resultados:
        alugado = resultados["alugado"]
        
        st.subheader("Carro Alugado")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Líquido Semanal", 
                f"€ {alugado['líquido']:.2f}",
                delta=f"€ {alugado['líquido'] - alugado['antes_extras']:.2f}" if st.session_state.include_extra_expenses else None,
                delta_color="inverse" if alugado['líquido'] < 0 else "normal",
                help="Lucro líquido após todas as despesas"
            )
        
        with col2:
            st.metric(
                "Média Horária", 
                f"€ {alugado['hora']:.2f}",
                delta_color="inverse" if alugado['hora'] < 0 else "normal",
                help="Valor ganho por hora trabalhada"
            )
            
        with col3:
            st.metric(
                "Rentabilidade", 
                f"{(alugado['líquido'] / st.session_state.weekly_earnings * 100):.1f}%" if st.session_state.weekly_earnings > 0 else "0%",
                help="Percentual dos ganhos que se transforma em lucro"
            )
        
        # Detalhamento dos cálculos
        with st.expander("📋 Detalhamento dos Cálculos - Carro Alugado"):
            detalhes_alugado = {
                "Descrição": [
                    "Ganhos Semanais",
                    f"Comissão ({st.session_state.rental_commission}%)",
                    "Custo do Aluguel",
                    "Custo com Combustível",
                    "Subtotal (antes de despesas extras)",
                ],
                "Valor (€)": [
                    f"{weekly_earnings:.2f}",
                    f"-{alugado['comissao']:.2f}",
                    f"-{st.session_state.rental_cost:.2f}",
                    f"-{st.session_state.fuel_cost:.2f}",
                    f"{alugado['antes_extras']:.2f}",
                ]
            }
            
            if st.session_state.include_extra_expenses:
                detalhes_alugado["Descrição"].append("Despesas Extras")
                detalhes_alugado["Valor (€)"].append(f"-{st.session_state.extra_expenses:.2f}")
                
                detalhes_alugado["Descrição"].append("**Total Líquido Final**")
                detalhes_alugado["Valor (€)"].append(f"**{alugado['líquido']:.2f}**")
            else:
                detalhes_alugado["Descrição"].append("**Total Líquido Final**")
                detalhes_alugado["Valor (€)"].append(f"**{alugado['líquido']:.2f}**")
            
            detalhes_alugado["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
            detalhes_alugado["Valor (€)"].extend([f"{st.session_state.weekly_hours:.1f}", f"{alugado['hora']:.2f}"])
            
            df_alugado = pd.DataFrame(detalhes_alugado)
            st.table(df_alugado)
    
    # Resultado para carro próprio
    elif st.session_state.calculation_type == "próprio" and "próprio" in resultados:
        proprio = resultados["próprio"]
        
        st.subheader("Carro Próprio")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Líquido Semanal", 
                f"€ {proprio['líquido']:.2f}",
                delta=f"€ {proprio['líquido'] - proprio['antes_extras']:.2f}" if st.session_state.include_extra_expenses else None,
                delta_color="inverse" if proprio['líquido'] < 0 else "normal",
                help="Lucro líquido após todas as despesas"
            )
        
        with col2:
            st.metric(
                "Média Horária", 
                f"€ {proprio['hora']:.2f}",
                delta_color="inverse" if proprio['hora'] < 0 else "normal",
                help="Valor ganho por hora trabalhada"
            )
            
        with col3:
            st.metric(
                "Rentabilidade", 
                f"{(proprio['líquido'] / st.session_state.weekly_earnings * 100):.1f}%" if st.session_state.weekly_earnings > 0 else "0%",
                help="Percentual dos ganhos que se transforma em lucro"
            )
        
        # Detalhamento dos cálculos
        with st.expander("📋 Detalhamento dos Cálculos - Carro Próprio"):
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
                    f"{st.session_state.weekly_earnings:.2f}",
                    f"-{proprio['comissao']:.2f}",
                    f"-{st.session_state.own_insurance:.2f}",
                    f"-{st.session_state.own_maintenance:.2f}",
                    f"-{st.session_state.fuel_cost:.2f}",
                    f"{proprio['antes_extras']:.2f}",
                ]
            }
            
            if st.session_state.include_extra_expenses:
                detalhes_proprio["Descrição"].append("Despesas Extras")
                detalhes_proprio["Valor (€)"].append(f"-{st.session_state.extra_expenses:.2f}")
                
                detalhes_proprio["Descrição"].append("**Total Líquido Final**")
                detalhes_proprio["Valor (€)"].append(f"**{proprio['líquido']:.2f}**")
            else:
                detalhes_proprio["Descrição"].append("**Total Líquido Final**")
                detalhes_proprio["Valor (€)"].append(f"**{proprio['líquido']:.2f}**")
            
            detalhes_proprio["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
            detalhes_proprio["Valor (€)"].extend([f"{st.session_state.weekly_hours:.1f}", f"{proprio['hora']:.2f}"])
            
            df_proprio = pd.DataFrame(detalhes_proprio)
            st.table(df_proprio)
    
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
                delta=f"€ {alugado['líquido'] - alugado['antes_extras']:.2f}" if st.session_state.include_extra_expenses else None,
                delta_color="inverse" if alugado['líquido'] < 0 else "normal",
                help="Lucro líquido após todas as despesas"
            )
        
        with col2:
            st.metric(
                "Carro Próprio (Líquido Semanal)", 
                f"€ {proprio['líquido']:.2f}",
                delta=f"€ {proprio['líquido'] - proprio['antes_extras']:.2f}" if st.session_state.include_extra_expenses else None,
                delta_color="inverse" if proprio['líquido'] < 0 else "normal",
                help="Lucro líquido após todas as despesas"
            )
        
        with col3:
            st.metric(
                "Diferença Semanal", 
                f"€ {resultados['diferença']:.2f}",
                delta_color="inverse" if resultados['diferença'] < 0 else "normal",
                help="Diferença entre as duas opções (Alugado - Próprio)"
            )
        
        # Métricas horárias
        st.subheader("Média Horária")
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
        
        # Métricas de rentabilidade
        st.subheader("Rentabilidade")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Carro Alugado", 
                f"{(alugado['líquido'] / st.session_state.weekly_earnings * 100):.1f}%" if st.session_state.weekly_earnings > 0 else "0%",
                help="Percentual dos ganhos que se transforma em lucro"
            )
        
        with col2:
            st.metric(
                "Carro Próprio", 
                f"{(proprio['líquido'] / st.session_state.weekly_earnings * 100):.1f}%" if st.session_state.weekly_earnings > 0 else "0%",
                help="Percentual dos ganhos que se transforma em lucro"
            )
        
        with col3:
            dif_rentabilidade = (alugado['líquido'] / st.session_state.weekly_earnings * 100) - (proprio['líquido'] / st.session_state.weekly_earnings * 100) if st.session_state.weekly_earnings > 0 else 0
            st.metric(
                "Diferença de Rentabilidade", 
                f"{dif_rentabilidade:.1f}%",
                delta_color="inverse" if dif_rentabilidade < 0 else "normal"
            )
        
        # Detalhamento dos cálculos
        with st.expander("📋 Detalhamento dos Cálculos"):
            comparison_data = {
                "Descrição": [
                    "Ganhos Semanais",
                    f"Comissão ({st.session_state.rental_commission}%)",
                    f"Comissão ({st.session_state.own_commission}%)",
                    "Custo do Aluguel",
                    "Seguro",
                    "Manutenção",
                    "Custo com Combustível",
                    "Subtotal (antes de despesas extras)",
                ],
                "Carro Alugado (€)": [
                    f"{st.session_state.weekly_earnings:.2f}",
                    f"-{alugado['comissao']:.2f}",
                    "N/A",
                    f"-{st.session_state.rental_cost:.2f}",
                    "N/A",
                    "N/A",
                    f"-{st.session_state.fuel_cost:.2f}",
                    f"{alugado['antes_extras']:.2f}",
                ],
                "Carro Próprio (€)": [
                    f"{st.session_state.weekly_earnings:.2f}",
                    "N/A",
                    f"-{proprio['comissao']:.2f}",
                    "N/A",
                    f"-{st.session_state.own_insurance:.2f}",
                    f"-{st.session_state.own_maintenance:.2f}",
                    f"-{st.session_state.fuel_cost:.2f}",
                    f"{proprio['antes_extras']:.2f}",
                ]
            }
            
            # Adicionar linha de despesas extras se aplicável
            if st.session_state.include_extra_expenses:
                comparison_data["Descrição"].append("Despesas Extras")
                comparison_data["Carro Alugado (€)"].append(f"-{st.session_state.extra_expenses:.2f}")
                comparison_data["Carro Próprio (€)"].append(f"-{st.session_state.extra_expenses:.2f}")
                
                comparison_data["Descrição"].append("**Total Líquido Final**")
                comparison_data["Carro Alugado (€)"].append(f"**{alugado['líquido']:.2f}**")
                comparison_data["Carro Próprio (€)"].append(f"**{proprio['líquido']:.2f}**")
            else:
                comparison_data["Descrição"].append("**Total Líquido Final**")
                comparison_data["Carro Alugado (€)"].append(f"**{alugado['líquido']:.2f}**")
                comparison_data["Carro Próprio (€)"].append(f"**{proprio['líquido']:.2f}**")
            
            # Adicionar horas e média horária
            comparison_data["Descrição"].extend(["Horas Trabalhadas", "Média Horária (€/hora)"])
            comparison_data["Carro Alugado (€)"].extend([f"{st.session_state.weekly_hours:.1f}", f"{alugado['hora']:.2f}"])
            comparison_data["Carro Próprio (€)"].extend([f"{st.session_state.weekly_hours:.1f}", f"{proprio['hora']:.2f}"])
            
            df = pd.DataFrame(comparison_data)
            st.table(df)
        
        # Recomendação
        st.subheader("💡 Recomendação")
        if resultados['diferença'] > 50:
            st.success(f"✅ **O carro alugado é significativamente mais vantajoso** - € {resultados['diferença']:.2f} por semana a mais")
        elif resultados['diferença'] > 0.01:
            st.success(f"✅ **O carro alugado é mais vantajoso** - € {resultados['diferença']:.2f} por semana a mais")
        elif resultados['diferença'] < -50:
            st.success(f"✅ **O carro próprio é significativamente mais vantajoso** - € {abs(resultados['diferença']):.2f} por semana a mais")
        elif resultados['diferença'] < -0.01:
            st.success(f"✅ **O carro próprio é mais vantajoso** - € {abs(resultados['diferença']):.2f} por semana a mais")
        else:
            st.info("ℹ️ **Ambas as opções têm resultados financeiros muito similares** - diferença inferior a € 0.01")
        
        # Visualização gráfica
        st.subheader("📊 Comparação Visual")
        
        tab1, tab2, tab3 = st.tabs(["Lucro Semanal", "Média Horária", "Rentabilidade"])
        
        with tab1:
            chart_data_weekly = pd.DataFrame({
                "Opção": ["Carro Alugado", "Carro Próprio"],
                "Lucro Líquido Semanal (€)": [alugado['líquido'], proprio['líquido']]
            })
            fig = px.bar(chart_data_weekly, x="Opção", y="Lucro Líquido Semanal (€)", 
                         title="Comparação do Lucro Semanal Líquido",
                         color="Opção", color_discrete_map={"Carro Alugado": "#1f77b4", "Carro Próprio": "#ff7f0e"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            chart_data_hourly = pd.DataFrame({
                "Opção": ["Carro Alugado", "Carro Próprio"],
                "Média Horária (€)": [alugado['hora'], proprio['hora']]
            })
            fig = px.bar(chart_data_hourly, x="Opção", y="Média Horária (€)", 
                         title="Comparação da Média Horária",
                         color="Opção", color_discrete_map={"Carro Alugado": "#1f77b4", "Carro Próprio": "#ff7f0e"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            rent_alugado = (alugado['líquido'] / st.session_state.weekly_earnings * 100) if st.session_state.weekly_earnings > 0 else 0
            rent_proprio = (proprio['líquido'] / st.session_state.weekly_earnings * 100) if st.session_state.weekly_earnings > 0 else 0
            
            chart_data_rent = pd.DataFrame({
                "Opção": ["Carro Alugado", "Carro Próprio"],
                "Rentabilidade (%)": [rent_alugado, rent_proprio]
            })
            fig = px.bar(chart_data_rent, x="Opção", y="Rentabilidade (%)", 
                         title="Comparação da Rentabilidade (% dos ganhos que viram lucro)",
                         color="Opção", color_discrete_map={"Carro Alugado": "#1f77b4", "Carro Próprio": "#ff7f0e"})
            fig.update_layout(showlegend=False, yaxis_ticksuffix="%")
            st.plotly_chart(fig, use_container_width=True)

# ---
# Informações Adicionais e Rodapé
# ---

with st.expander("💡 Dicas e Informações"):
    st.markdown("""
    ### 📋 Como usar esta calculadora:
    
    1. **Dados Básicos**: Preencha seus ganhos semanais, horas trabalhadas e custo com combustível
    2. **Despesas Extras**: Adicione custos como estacionamento, portagens e lavagens (opcional)
    3. **Parâmetros Avançados**: Ajuste valores específicos para cada tipo de veículo
    4. **Calcule**: Escolha entre calcular para carro alugado, próprio ou comparar ambos
    
    ### 📊 Explicação dos campos:
    - **Ganhos Semanais**: Valor total que você recebe pelos serviços de TVDE em uma semana
    - **Horas Trabalhadas**: Total de horas trabalhadas na semana (incluindo tempo de espera)
    - **Custo com Combustível**: Gasto semanal estimado com abastecimento
    - **Comissão**: Percentual que a plataforma retém pelos serviços
    - **Custo do Aluguel**: Valor semanal pelo aluguel do veículo (se aplicável)
    - **Seguro**: Custo semanal do seguro do veículo próprio
    - **Manutenção**: Custo semanal estimado com manutenção do veículo próprio
    - **Despesas Extras**: Custos adicionais como estacionamento, portagens, lavagens, etc.
    
    ### ⚠️ Notas importantes:
    - As médias horárias são calculadas considerando todas as despesas
    - Considere outros custos não incluídos aqui, como desvalorização do veículo e impostos
    - Esta calculadora fornece estimativas - valores reais podem variar
    """)

st.markdown("---")
st.caption("Desenvolvido para ajudar motoristas TVDE a tomar decisões financeiras informadas. | v2.0")
