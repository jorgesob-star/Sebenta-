with col1:
    st.header("📊 Dados de Entrada")
    
    weekly_earnings = st.number_input(
        "Ganhos Semanais (€):", 
        min_value=0.0, 
        value=900.0, 
        step=50.0,
        help="Valor total ganho por semana antes de despesas"
    )
    
    # Primeiro o combustível
    fuel_cost = st.number_input(
        "Custo Semanal com Combustível (€):", 
        min_value=0.0, 
        value=210.0, 
        step=10.0,
        help="Custo semanal estimado com combustível"
    )
    
    # Depois as horas trabalhadas
    weekly_hours = st.number_input(
        "Horas Trabalhadas por Semana:", 
        min_value=0.0, 
        value=50.0, 
        step=1.0,
        help="Total de horas trabalhadas na semana"
    )
