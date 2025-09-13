import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="Gestor de Valores", page_icon="💰", layout="centered")

# Título da aplicação
st.title("💰 Gestor de Valores com Somas Parciais")
st.markdown("Os valores são salvos automaticamente e persistem entre sessões.")

# Valores padrão iniciais
default_values = {
    "Kraken": 678,
    "Gate": 1956,
    "Coinbase": 2463,
    "N26": 195,
    "Revolut": 2180,
    "Caixa": 927
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
            return default_values
    return default_values

# Função para salvar valores
def save_values(values):
    with open(DATA_FILE, 'w') as f:
        json.dump(values, f)

# Carregar valores
saved_values = load_values()

# Inicializar session_state se necessário
if "values" not in st.session_state:
    st.session_state["values"] = saved_values

# Atualizar valores no session_state se houver mudanças no arquivo
if saved_values != st.session_state["values"]:
    st.session_state["values"] = saved_values

# Layout com duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Modificar Valores")
    
    # Inputs para modificar valores
    new_values = {}
    for key in st.session_state["values"].keys():
        new_values[key] = st.number_input(
            label=key,
            value=st.session_state["values"][key],
            key=key,
            step=1
        )
    
    # Botão para salvar alterações
    if st.button("💾 Salvar Alterações", use_container_width=True):
        st.session_state["values"] = new_values
        save_values(new_values)
        st.success("Valores salvos com sucesso!")
        
    # Botão para restaurar valores padrão
    if st.button("🔄 Restaurar Valores Padrão", use_container_width=True):
        st.session_state["values"] = default_values
        save_values(default_values)
        st.success("Valores padrão restaurados!")

with col2:
    st.subheader("Visualização")
    
    # Criar DataFrame com os valores atuais
    df = pd.DataFrame({
        "Plataforma": list(st.session_state["values"].keys()),
        "Valor": list(st.session_state["values"].values())
    })
    
    # Mostrar tabela
    st.dataframe(df, height=300, use_container_width=True)
    
    # Calcular somas
    total = df['Valor'].sum()
    
    # Calcular soma dos 3 primeiros e 3 segundos
    first_three_sum = df['Valor'].iloc[:3].sum()
    second_three_sum = df['Valor'].iloc[3:6].sum()
    
    # Mostrar métricas
    st.metric(label="💰 **Total Geral**", value=f"{total:,}")
    
    # Layout para as somas parciais
    col21, col22 = st.columns(2)
    with col21:
        st.metric(label="📊 Soma dos 3 primeiros", value=f"{first_three_sum:,}")
    with col22:
        st.metric(label="📈 Soma dos 3 segundos", value=f"{second_three_sum:,}")
    
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
