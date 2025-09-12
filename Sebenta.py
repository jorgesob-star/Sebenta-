# Entrada de dados (layout em coluna única no mobile)
st.header("📊 Dados de Entrada")
weekly_earnings = st.number_input(
    "Ganhos Semanais (€)",
    min_value=0.0,
    value=700.0,
    step=10.0,
)
weekly_hours = st.number_input(
    "Horas Semanais",
    min_value=0,
    value=50,
    step=1,
)
fuel_cost = st.number_input(
    "Combustível (€)",
    min_value=0.0,
    value=200.0,
    step=5.0,
)

# Botões em linha mas responsivos
st.header("🧮 Calcular")
calc_col1, calc_col2, calc_col3 = st.columns([1,1,1], gap="small")

with calc_col1:
    st.button("🚘 Alugado", type="primary", use_container_width=True, key="btn_alugado")
with calc_col2:
    st.button("🚗 Próprio", type="primary", use_container_width=True, key="btn_proprio")
with calc_col3:
    st.button("⚖️ Comparar", type="primary", use_container_width=True, key="btn_comparar")

# Gráfico adaptado
if len(resultados) > 1:
    chart = alt.Chart(df_chart).mark_bar(size=60).encode(
        x=alt.X("Opção", sort=None),
        y="Lucro (€)",
        color="Opção"
    ).properties(height=300)   # altura maior para caber bem no mobile
    st.altair_chart(chart, use_container_width=True)
