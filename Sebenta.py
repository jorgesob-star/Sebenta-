# -------------------------------
# Dados de entrada
# -------------------------------
st.header("📊 Dados de Entrada")
weekly_earnings = st.number_input("Ganhos Semanais (€)", min_value=0.0, value=750.0, step=10.0)
weekly_hours = st.number_input("Horas Semanais", min_value=0, value=50, step=1)
fuel_cost = st.number_input("Combustível (€)", min_value=0.0, value=200.0, step=5.0)

# Novos campos
tips = st.number_input("Gorjetas (€)", min_value=0.0, value=0.0, step=5.0)
cancellation_fees = st.number_input("Taxas de Cancelamento (€)", min_value=0.0, value=0.0, step=5.0)
tolls = st.number_input("Portagens Pagas (€)", min_value=0.0, value=0.0, step=5.0)
