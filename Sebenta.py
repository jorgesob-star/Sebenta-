import streamlit as st

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(
    page_title="Calculadora TVDE Semanal",
    page_icon="🚗",
    layout="centered"
)

# -------------------------------
# Título da aplicação
# -------------------------------
st.title("🚗 Calculadora de Ganhos Semanais TVDE")
st.markdown("Calcule seus rendimentos líquidos semanais como motorista TVDE")

# -------------------------------
# Inicializar variáveis de sessão
# -------------------------------
if 'comissao_plataforma' not in st.session_state:
    st.session_state.comissao_plataforma = 6.0

if 'despesas_fixas_detalhadas' not in st.session_state:
    st.session_state.despesas_fixas_detalhadas = {
        "Aluguer": 270.0,
        "Seguro": 0.0,
        "Slot TVDE": 0.0,
        "Manutenção": 0.0
    }

if 'show_advanced' not in st.session_state:
    st.session_state.show_advanced = False

# -------------------------------
# Função para alternar a visualização da seção de parâmetros
# -------------------------------
def toggle_advanced():
    st.session_state.show_advanced = not st.session_state.show_advanced

# -------------------------------
# Botão para mostrar/ocultar seção de alteração de parâmetros
# -------------------------------
st.button(
    "⚙️ Alterar Parâmetros" if not st.session_state.show_advanced else "⬆️ Ocultar Alterar Parâmetros",
    on_click=toggle_advanced
)

# -------------------------------
# Alterar parâmetros
# -------------------------------
if st.session_state.show_advanced:
    with st.expander("Alterar Parâmetros", expanded=True):
        st.session_state.comissao_plataforma = st.number_input(
            "Comissão da Plataforma (%)", 
            min_value=0.0, max_value=100.0, 
            value=st.session_state.comissao_plataforma, step=0.5
        )

        st.markdown("### Despesas Fixas Detalhadas (€)")
        remover_despesa = None
        for despesa, valor in list(st.session_state.despesas_fixas_detalhadas.items()):
            col1, col2 = st.columns([3,1])
            with col1:
                st.session_state.despesas_fixas_detalhadas[despesa] = st.number_input(
                    despesa, min_value=0.0, value=valor, step=5.0, key=f"input_{despesa}"
                )
            with col2:
                if st.button("❌", key=f"remove_{despesa}", help=f"Remover {despesa}"):
                    remover_despesa = despesa
        if remover_despesa:
            del st.session_state.despesas_fixas_detalhadas[remover_despesa]

        st.markdown("### ➕ Adicionar Nova Despesa Fixa")
        nova_despesa = st.text_input("Nome da nova despesa", key="nova_despesa")
        novo_valor = st.number_input("Valor (€)", min_value=0.0, step=5.0, key="novo_valor")
        if st.button("Adicionar Despesa"):
            if nova_despesa and nova_despesa not in st.session_state.despesas_fixas_detalhadas:
                st.session_state.despesas_fixas_detalhadas[nova_despesa] = novo_valor
                st.success(f"Despesa '{nova_despesa}' adicionada com sucesso!")

        # Total de despesas fixas
        st.session_state.despesas_fixas = sum(st.session_state.despesas_fixas_detalhadas.values())
        st.info(f"💡 Total de Despesas Fixas: €{st.session_state.despesas_fixas:.2f}")

# -------------------------------
# Entradas principais do usuário
# -------------------------------
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
        step=10.0
    )
    horas_trabalhadas_semana = st.number_input(
        "Total de horas trabalhadas na semana", 
        min_value=0.0, 
        value=50.0, 
        step=0.5
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
        step=5.0
    )

# -------------------------------
# Cálculos
# -------------------------------
comissao_valor_semana = ganhos_brutos_semana * (st.session_state.comissao_plataforma / 100)
ganhos_liquidos_semana = (ganhos_brutos_semana - comissao_valor_semana - 
                          custo_gasolina_semana - st.session_state.despesas_fixas - outros_custos)

margem_lucro = (ganhos_liquidos_semana / ganhos_brutos_semana) * 100 if ganhos_brutos_semana > 0 else 0
valor_por_hora = ganhos_liquidos_semana / horas_trabalhadas_semana if horas_trabalhadas_semana > 0 else 0

# -------------------------------
# Resultados Semanais
# -------------------------------
st.header("Resultados Semanais")
col1, col2, col3 = st.columns(3)
col1.metric("Ganhos Líquidos Semanais", f"€{ganhos_liquidos_semana:.2f}")
col2.metric("Comissão Plataforma", f"€{comissao_valor_semana:.2f}")
col3.metric("Margem de Lucro", f"{margem_lucro:.1f}%")

st.subheader("💰 Valor por Hora")
st.metric("Ganho Líquido por Hora", f"€{valor_por_hora:.2f}")

# -------------------------------
# Distribuição de custos
# -------------------------------
st.subheader("Distribuição dos Custos e Ganhos")
categorias = ['Ganhos Líquidos', 'Comissão', 'Gasolina', 'Despesas Fixas', 'Outros']
valores = [
    max(ganhos_liquidos_semana, 0), 
    comissao_valor_semana, 
    custo_gasolina_semana, 
    st.session_state.despesas_fixas, 
    outros_custos
]
data = {
    "Categoria": categorias,
    "Valor (€)": valores,
    "Tipo": ["Ganho", "Custo", "Custo", "Custo", "Custo"]
}
st.bar_chart(data, x="Categoria", y="Valor (€)", color="Tipo")

# -------------------------------
# Detalhamento
# -------------------------------
st.subheader("📊 Detalhamento dos Custos")
det_col1, det_col2 = st.columns(2)

with det_col1:
    st.write("**Ganhos:**")
    st.write(f"- Apuro Bruto: €{ganhos_brutos_semana:.2f}")
    st.write("")
    st.write("**Custos Fixos Detalhados:**")
    for despesa, valor in st.session_state.despesas_fixas_detalhadas.items():
        st.write(f"- {despesa}: €{valor:.2f}")
    st.write(f"- Total Despesas Fixas: €{st.session_state.despesas_fixas:.2f}")
    st.write("")
    st.write("**Outros Custos:**")
    st.write(f"- Gasolina: €{custo_gasolina_semana:.2f}")
    st.write(f"- Outros: €{outros_custos:.2f}")
    st.write(f"- Comissão Plataforma: €{comissao_valor_semana:.2f}")

with det_col2:
    total_custos = comissao_valor_semana + custo_gasolina_semana + st.session_state.despesas_fixas + outros_custos
    st.write("**Totais:**")
    st.write(f"- Total Ganhos: €{ganhos_brutos_semana:.2f}")
    st.write(f"- Total Custos: €{total_custos:.2f}")
    st.write(f"- **Lucro Líquido: €{ganhos_liquidos_semana:.2f}**")
    st.write(f"- Margem de Lucro: {margem_lucro:.1f}%")
    st.write(f"- **Valor por Hora: €{valor_por_hora:.2f}**")

# -------------------------------
# Médias Diárias
# -------------------------------
st.subheader("💰 Médias Diárias")
ganho_bruto_diario = ganhos_brutos_semana / dias_trabalhados
ganho_liquido_diario = ganhos_liquidos_semana / dias_trabalhados
horas_diarias = horas_trabalhadas_semana / dias_trabalhados

col1, col2, col3 = st.columns(3)
col1.metric("Ganho Bruto Diário", f"€{ganho_bruto_diario:.2f}")
col2.metric("Ganho Líquido Diário", f"€{ganho_liquido_diario:.2f}")
col3.metric("Média Horas por Dia", f"{horas_diarias:.1f}h")

# -------------------------------
# Projeção Mensal
# -------------------------------
st.header("📈 Projeção Mensal")
dias_uteis_mes = st.slider("Dias úteis no mês", 20, 31, 22)
semanas_mes = dias_uteis_mes / dias_trabalhados
ganhos_mensais = ganhos_liquidos_semana * semanas_mes

proj_col1, proj_col2, proj_col3 = st.columns(3)
proj_col1.metric("Projeção de Ganhos Mensais", f"€{ganhos_mensais:.2f}")
proj_col2.metric("Média Diária Líquida", f"€{ganho_liquido_diario:.2f}")
proj_col3.metric("Valor por Hora", f"€{valor_por_hora:.2f}")

# -------------------------------
# Resumo Financeiro
# -------------------------------
st.header("💶 Resumo Financeiro Semanal")
resumo_col1, resumo_col2, resumo_col3 = st.columns(3)
resumo_col1.metric("Apuro Semanal", f"€{ganhos_brutos_semana:.2f}")
resumo_col2.metric("Custos Semanais", f"€{total_custos:.2f}")
resumo_col3.metric("Lucro Semanal", f"€{ganhos_liquidos_semana:.2f}", delta=f"{margem_lucro:.1f}%")

# -------------------------------
# Resumo de Horas
# -------------------------------
st.subheader("⏰ Resumo de Horas")
horas_col1, horas_col2, horas_col3 = st.columns(3)
horas_col1.metric("Total Horas Trabalhadas", f"{horas_trabalhadas_semana:.1f}h")
horas_col2.metric("Média Horas por Dia", f"{horas_diarias:.1f}h")
horas_col3.metric("Valor por Hora", f"€{valor_por_hora:.2f}")

# -------------------------------
# Rodapé
# -------------------------------
st.markdown("---")
st.caption("App desenvolvido para cálculo de ganhos no TVDE. Agora pode adicionar ou remover despesas fixas livremente.")
