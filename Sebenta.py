import streamlit as st
import pandas as pd
import altair as alt

st.title("Soma de Valores por Plataforma")

st.subheader("Insira os valores:")

kraken = st.number_input("Kraken", value=678)
gate = st.number_input("Gate", value=1956)
coinbase = st.number_input("Coinbase", value=2463)
n26 = st.number_input("N26", value=195)
revolut = st.number_input("Revolut", value=2180)
caixa = st.number_input("Caixa", value=927)

# Criar DataFrame
valores = {
    "Plataforma": ["Kraken", "Gate", "Coinbase", "N26", "Revolut", "Caixa"],
    "Valor": [kraken, gate, coinbase, n26, revolut, caixa],
}
df = pd.DataFrame(valores)

st.subheader("Valores Digitados")
st.dataframe(df)

# Soma total
total = df["Valor"].sum()
st.subheader("Soma Total")
st.success(f"💰 Total = {total}")

# Gráfico de barras
st.subheader("Gráfico de Valores")
chart = (
    alt.Chart(df)
    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x="Plataforma",
        y="Valor",
        tooltip=["Plataforma", "Valor"]
    )
)
st.altair_chart(chart, use_container_width=True)
