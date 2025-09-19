import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="Gestor de Valores", page_icon="💰", layout="centered")

# Título da aplicação
st.title("💰 Gestor de Valores com Grupos A e B")
st.markdown("Os valores são salvos automaticamente e persistem entre sessões.")

# Valores padrão iniciais
default_values = {
    "1. Kraken": 678,
    "2. Gate": 1956,
    "3. Coinbase": 2463,
    "4. N26": 195,
    "5. Revolut": 2180,
    "6. Caixa": 927
}

# Nome do arquivo de dados
DATA_FILE = "saved_values.json"

# Função para carregar valores salvos
def load_values():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return default_values.copy()
    return default_values.copy()

# Função para salvar valores
def save_values(values):
    with open(DATA_FILE, 'w') as f:
        json.dump(values, f)

# Inicializar os valores na session_state
if "values" not in st.session_state:
    st.session_state.values = load_values()

# Layout com duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Modificar Valores")
    
    # Inputs para modificar valores - criamos um dicionário temporário
    temp_values = {}
    for key in st.session_state.values.keys():
        temp_values[key] = st.number_input(
            label=key,
            value=st.session_state.values[key],
            key=key,
            step=1
        )
    
    # Botão para salvar alterações
    if st.button("💾 Salvar Alterações", use_container_width=True):
        st.session_state.values = temp_values
        save_values(temp_values)
        st.success("Valores salvos com sucesso!")
        st.rerun()
        
    # Botão para restaurar valores padrão
    if st.button("🔄 Restaurar Valores Padrão", use_container_width=True):
        st.session_state.values = default_values.copy()
        save_values(default_values.copy())
        st.success("Valores padrão restaurados!")
        st.rerun()

with col2:
    st.subheader("Visualização")
    
    # Criar DataFrame com os valores atuais
    df = pd.DataFrame({
        "Plataforma": list(st.session_state.values.keys()),
        "Valor": list(st.session_state.values.values())
    })
    
    # Mostrar tabela
    st.dataframe(df, height=300, use_container_width=True)
    
    # Calcular somas
    total = df['Valor'].sum()
    
    # Calcular soma do grupo A (1-3) e grupo B (4-6)
    group_a_sum = df['Valor'].iloc[:3].sum()
    group_b_sum = df['Valor'].iloc[3:6].sum()
    
    # Mostrar métricas
    st.metric(label="💰 **Total Geral**", value=f"{total:,}")
    
    # Layout para as somas parciais
    col21, col22 = st.columns(2)
    with col21:
        st.metric(label="🅰️ Soma do Grupo A (1-3)", value=f"{group_a_sum:,}")
    with col22:
        st.metric(label="🅱️ Soma do Grupo B (4-6)", value=f"{group_b_sum:,}")
    
    # Gerar timestamp para nome do arquivo
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"valores_{timestamp}.csv"
    
    # Botão de download
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name=file_name,
        mime="text/csv",
        use_container_width=True
    )

# Informações adicionais
st.info("💡 Dica: Os valores são automaticamente salvos no arquivo 'saved_values.json' e persistem entre execuções.")
