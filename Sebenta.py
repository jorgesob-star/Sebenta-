import streamlit as st
import pandas as pd
import altair as alt

# Configuração da página
st.set_page_config(
    page_title="Calculadora TVDE Semanal",
    page_icon="🚗",
    layout="centered"
)

# Título da aplicação
st.title("🚗 Calculadora de Ganhos Semanais TVDE")
st.markdown("Calcule seus rendimentos líquidos semanais como motorista TVDE")

# Inicializar variáveis de sessão
if 'comissao_plataforma' not in st.session_state:
    st.session_state.comissao_plataforma = 6.0
if 'aluguer' not in st.session_state:
    st.session_state.aluguer = 270.0
if 'seguro' not in st.session_state:
    st.session_state.seguro = 0.0
if 'slot' not in st.session_state:
    st.session_state.slot = 0.0
if 'despesas_fixas' not in st.session_state:
    st.session_state.despesas_fixas = st.session_state.aluguer + st.session_state.seguro + st.session_state.slot
if 'show_advanced' not in st.session_state:
    st.session_state.show_advanced = False

# Função para alternar a visualização da seção de parâmetros
def toggle_advanced():
    st.session_state.show_advanced = not st.session_state.show_advanced

# Botão para mostrar/ocultar seção de alteração de parâmetros
st.button(
    "⚙️ Alterar Parâmetros" if not st.session_state.show_advanced else "⬆️ Ocultar Alterar Parâmetros",
    on_click=toggle_advanced
)

# Mostrar inputs de alteração de parâmetros se a seção estiver ativa
if st.session_state.show_advanced:
    with st.expander("Alterar Parâmetros", expanded=True):
        st.session_state.comissao_plataforma = st.number_input(
            "Comissão da Plataforma (%)", 
            min_value=0.0, max_value=100.0, 
            value=st.session_state.comissao_plataforma, step=0.5,
            key="comissao_input"
        )
        
        # Inputs detalhados de despesas fixas
        st.markdown("### Despesas Fixas Detalhadas (€)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.aluguer = st.number_input("Aluguer", min_value=0.0, value=st.session_state.aluguer, step=5.0)
        with col2:
            st.session_state.seguro = st.number_input("Seguro", min_value=0.0, value=st.session_state.seguro, step=5.0)
        with col3:
            st.session_state.slot = st.number_input("Slot", min_value=0.0, value=st.session_state.slot, step=5.0)
        
        # Recalcular total das despesas fixas
        st.session_state.despesas_fixas = st.session_state.aluguer + st.session_state.seguro + st.session_state.slot
        st.info(f"💡 Total de Despesas Fixas: €{st.session_state.despesas_fixas:.2f}")

# Entradas principais do usuário
st.header("Entradas Semanais")

apuro_semanal = 900.0
combustivel_semanal = 200.0

col1, col2 = st.columns(2)

with col1:
    dias_trabalhados = st.slider("Dias trabalhados na semana", 1, 7, 7)
    ganhos_brutos_semana = st.number_input(
        "Ganhos Brutos Semanais (€)", 
        min_value=0.0, 
        value=apuro_semanal, 
        step=10.0,
        help="Total de ganhos brutos na semana (apuro)"
    )
    horas_trabalhadas_semana = st.number_input(
        "Total de horas trabalhadas na semana", 
        min_value=0.0, 
        value=50.0, 
        step=0.5,
        help="Número total de horas que trabalhou durante a semana"
    )

with col2:
    custo_gasolina_semana = st.number_input(
        "Custo com Gasolina Semanal (€)", 
        min_value=0.0, 
        value=combustivel_semanal, 
        step=10.0
    )
    outros_custos = st.number_input(
        "Outros Custos Semanais (€)", 
        min_value=0.0, 
        value=0.0, 
        step=5.0,
        help="Lavagens, portagens, estacionamento, etc."
    )

# Cálculos
comissao_valor_semana = ganhos_brutos_semana * (st.session_state.comissao_plataforma / 100)

ganhos_liquidos_semana = (ganhos_brutos_semana - comissao_valor_semana - 
                          custo_gasolina_semana - st.session_state.despesas_fixas - outros_custos)

margem_lucro = (ganhos_liquidos_semana / ganhos_brutos_semana) * 100 if ganhos_brutos_semana > 0 else 0
valor_por_hora = ganhos_liquidos_semana / horas_trabalhadas_semana if horas_trabalhadas_semana > 0 else 0

if ganhos_liquidos_semana < 0:
    st.warning("⚠️ Atenção: os custos excedem os ganhos! Verifique suas entradas.")

# Resultados
st.header("Resultados Semanais")
col1, col2, col3 = st.columns(3)
col1.metric("Ganhos Líquidos Semanais", f"€{ganhos_liquidos_semana:.2f}")
col2.metric("Comissão Plataforma", f"€{comissao_valor_semana:.2f}")
col3.metric("Margem de Lucro", f"{margem_lucro:.1f}%")

st.subheader("💰 Valor por Hora")
st.metric("Ganho Líquido por Hora", f"€{valor_por_hora:.2f}")

# Distribuição de custos usando Altair
st.subheader("Distribuição dos Custos e Ganhos")
categorias = ['Ganhos Líquidos', 'Comissão', 'Gasolina', 'Despesas Fixas', 'Outros']
valores = [
    max(ganhos_liquidos_semana, 0), 
    comissao_valor_semana, 
    custo_gasolina_semana, 
    st.session_state.despesas_fixas, 
    outros_custos
]
tipos = ["Ganho", "Custo", "Custo", "Custo", "Custo"]

df = pd.DataFrame({
    "Categoria": categorias,
    "Valor (€)": valores,
    "Tipo": tipos
})

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Categoria', sort=None),
    y='Valor (€)',
    color='Tipo',
    tooltip=['Categoria', 'Valor (€)', 'Tipo']
).properties(
    width=600,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# Tabela de detalhamento
st.subheader("📊 Detalhamento dos Custos")
det_col1, det_col2 = st.columns(2)

with det_col1:
    st.write("**Ganhos:**")
    st.write(f"- Apuro Bruto: €{ganhos_brutos_semana:.2f}")
    st.write("")
    st.write("**Custos:**")
    st.write(f"- Comissão Plataforma: €{comissao_valor_semana:.2f}")
    st.write(f"- Gasolina: €{custo_gasolina_semana:.2f}")
    st.write(f"- Aluguer: €{st.session_state.aluguer:.2f}")
    st.write(f"- Seguro: €{st.session_state.seguro:.2f}")
    st.write(f"- Slot: €{st.session_state.slot:.2f}")
    st.write(f"- Total Despesas Fixas: €{st.session_state.despesas_fixas:.2f}")
    st.write(f"- Outros Custos: €{outros_custos:.2f}")

with det_col2:
    total_custos = comissao_valor_semana + custo_gasolina_semana + st.session_state.despesas_fixas + outros_custos
    st.write("**Totais:**")
    st.write(f"- Total Ganhos: €{ganhos_brutos_semana:.2f}")
    st.write(f"- Total Custos: €{total_custos:.2f}")
    st.write(f"- **Lucro Líquido: €{ganhos_liquidos_semana:.2f}**")
    st.write(f"- Margem de Lucro: {margem_lucro:.1f}%")
    st.write(f"- **Valor por Hora: €{valor_por_hora:.2f}**")

# Cálculos diários
st.subheader("💰 Médias Diárias")
ganho_bruto_diario = ganhos_brutos_semana / dias_trabalhados
ganho_liquido_diario = ganhos_liquidos_semana / dias_trabalhados
horas_diarias = horas_trabalhadas_semana / dias_trabalhados

col1, col2, col3 = st.columns(3)
col1.metric("Ganho Bruto Diário", f"€{ganho_bruto_diario:.2f}")
col2.metric("Ganho Líquido Diário", f"€{ganho_liquido_diario:.2f}")
col3.metric("Média Horas por Dia", f"{horas_diarias:.1f}h")

# Projeção mensal
st.header("📈 Projeção Mensal")
dias_uteis_mes = st.slider("Dias úteis no mês", 20, 31, 22)
semanas_mes = dias_uteis_mes / dias_trabalhados
ganhos_mensais = ganhos_liquidos_semana * semanas_mes

proj_col1, proj_col2, proj_col3 = st.columns(3)
proj_col1.metric("Projeção de Ganhos Mensais", f"€{ganhos_mensais:.2f}")
proj_col2.metric("Média Diária Líquida", f"€{ganho_liquido_diario:.2f}")
proj_col3.metric("Valor por Hora", f"€{valor_por_hora:.2f}")

# Resumo financeiro
st.header("💶 Resumo Financeiro Semanal")
resumo_col1, resumo_col2, resumo_col3 = st.columns(3)
resumo_col1.metric("Apuro Semanal", f"€{ganhos_brutos_semana:.2f}")
resumo_col2.metric("Custos Semanais", f"€{total_custos:.2f}")
resumo_col3.metric("Lucro Semanal", f"€{ganhos_liquidos_semana:.2f}", delta=f"{margem_lucro:.1f}%")

# Resumo de horas
st.subheader("⏰ Resumo de Horas")
horas_col1, horas_col2, horas_col3 = st.columns(3)
horas_col1.metric("Total Horas Trabalhadas", f"{horas_trabalhadas_semana:.1f}h")
horas_col2.metric("Média Horas por Dia", f"{horas_diarias:.1f}h")
horas_col3.metric("Valor por Hora", f"€{valor_por_hora:.2f}")

# Valores de parâmetros atuais
if st.session_state.show_advanced:
    st.info(f"ℹ️ **Valores atuais dos parâmetros:** Comissão: {st.session_state.comissao_plataforma}%, "
            f"Aluguer: €{st.session_state.aluguer:.2f}, Seguro: €{st.session_state.seguro:.2f}, Slot: €{st.session_state.slot:.2f}, "
            f"Total Despesas Fixas: €{st.session_state.despesas_fixas:.2f}")

# Rodapé
st.markdown("---")
st.caption("App desenvolvido para cálculo de ganhos no TVDE. Use o botão 'Alterar Parâmetros' para ajustar a comissão e despesas fixas detalhadas.")
