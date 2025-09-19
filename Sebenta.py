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
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                loaded_values = json.load(f)
                # Garantir que todos os valores são números
                return {k: int(v) if isinstance(v, (int, float, str)) and str(v).isdigit() else v 
                        for k, v in loaded_values.items()}
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")
            return default_values.copy()
    return default_values.copy()

# Função para salvar valores
def save_values(values):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(values, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {e}")

# Inicializar os valores
if "app_values" not in st.session_state:
    st.session_state.app_values = load_values()

# Layout com duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Modificar Valores")
    
    # Criar inputs para cada valor
    new_values = {}
    for key, value in st.session_state.app_values.items():
        new_values[key] = st.number_input(
            label=key,
            value=int(value) if value is not None else 0,
            key=f"input_{key}",
            step=1
        )
    
    # Botão para salvar alterações
    if st.button("💾 Salvar Alterações", use_container_width=True):
        st.session_state.app_values = new_values
        save_values(new_values)
        st.success("Valores salvos com sucesso!")
        st.rerun()
        
    # Botão para restaurar valores padrão
    if st.button("🔄 Restaurar Valores Padrão", use_container_width=True):
        st.session_state.app_values = default_values.copy()
        save_values(default_values.copy())
        st.success("Valores padrão restaurados!")
        st.rerun()

with col2:
    st.subheader("Visualização")
    
    # Criar DataFrame com os valores atuais
    df = pd.DataFrame({
        "Plataforma": list(st.session_state.app_values.keys()),
        "Valor": list(st.session_state.app_values.values())
    })
    
    # Mostrar tabela
    st.dataframe(df, height=300, use_container_width=True)
    
    # Calcular somas
    total = sum([v for v in st.session_state.app_values.values() if isinstance(v, (int, float))])
    
    # Calcular soma do grupo A (1-3) e grupo B (4-6)
    values_list = list(st.session_state.app_values.values())
    group_a_sum = sum(values_list[:3])
    group_b_sum = sum(values_list[3:6])
    
    # Mostrar métricas
    st.metric(label="💰 **Total Geral**", value=f"{total:,.0f}")
    
    # Layout para as somas parciais
    col21, col22 = st.columns(2)
    with col21:
        st.metric(label="🅰️ Soma do Grupo A (1-3)", value=f"{group_a_sum:,.0f}")
    with col22:
        st.metric(label="🅱️ Soma do Grupo B (4-6)", value=f"{group_b_sum:,.0f}")
    
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

# Debug (pode remover depois)
with st.expander("🔍 Debug Info"):
    st.write("Valores atuais:", st.session_state.app_values)
    st.write("Arquivo existe:", os.path.exists(DATA_FILE))
