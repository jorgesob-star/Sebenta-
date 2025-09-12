for i, (tipo, lucro) in enumerate(resultados.items()):
    with cards[i]:
        st.markdown(f"### {tipo}")
        if tipo == "Diferença":
            st.markdown(f"<h2>€ {lucro[0]:,.2f}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p>Δ {lucro[1]:.1f}%</p>", unsafe_allow_html=True)
        else:
            # Lucro por hora
            if weekly_hours > 0:
                lucro_hora = lucro / weekly_hours
            else:
                lucro_hora = 0
                st.warning("⚠️ Horas semanais = 0, lucro/hora não calculado.")

            # Alerta se o lucro for negativo
            if lucro < 0:
                st.warning(f"⚠️ Lucro negativo: € {lucro:,.2f}")

            st.markdown(f"<h2>€ {lucro:,.2f}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p>Lucro/hora: € {lucro_hora:.2f} €/h</p>", unsafe_allow_html=True)

            # Mini-resumo dos custos e comissão
            detalhe = next((d for d in detalhes if d["Opção"] == tipo), None)
            if detalhe:
                for k, v in detalhe.items():
                    if k not in ["Opção", "Lucro Líquido (€)"]:
                        if "%" in k:
                            st.markdown(f"{k}: {v:.1f}%")
                        else:
                            st.markdown(f"{k}: € {v:,.2f}")
