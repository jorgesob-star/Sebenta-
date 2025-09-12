# -------------------------------
# Resultados
# -------------------------------
if st.session_state.calculation_type:
    resultados = calcular_ganhos(weekly_earnings, weekly_hours, fuel_cost, st.session_state.calculation_type)

    st.subheader("📊 Resultados")

    # Métricas (mobile-friendly)
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

    # -------------------------------
    # Mostrar diferença de valor
    # -------------------------------
    if st.session_state.calculation_type == "comparar" and len(resultados) == 2:
        lucro_proprio = resultados.get("Carro Próprio", 0)
        lucro_alugado = resultados.get("Carro Alugado", 0)
        diferenca = lucro_proprio - lucro_alugado
        st.markdown(f"**💰 Diferença entre Carro Próprio e Carro Alugado:** € {diferenca:,.2f}")

    # -------------------------------
    # Cores automáticas do gráfico conforme tema
    # -------------------------------
    theme = st.get_option("theme.base")  # "light" ou "dark"
    if theme == "dark":
        bar_colors = alt.Scale(domain=["Carro Próprio", "Carro Alugado"],
                               range=["#FFB347", "#1E90FF"])
    else:
        bar_colors = alt.Scale(domain=["Carro Próprio", "Carro Alugado"],
                               range=["#FF7F50", "#6495ED"])

    # Gráfico comparativo
    if len(resultados) > 1:
        df_chart = pd.DataFrame({
            "Opção": list(resultados.keys()),
            "Lucro (€)": list(resultados.values())
        })
        chart = alt.Chart(df_chart).mark_bar(size=60).encode(
            x=alt.X("Opção", sort=None),
            y="Lucro (€)",
            color=alt.Color("Opção", scale=bar_colors)
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
