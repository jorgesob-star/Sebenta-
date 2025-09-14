import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Gestor de Valores", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .group-a {
        border-left: 5px solid #1f77b4;
    }
    .group-b {
        border-left: 5px solid #ff7f0e;
    }
    .stButton button {
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .platform-name {
        font-weight: bold;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Título da aplicação
st.markdown('<h1 class="main-header">💰 Gestor de Valores com Grupos A e B</h1>', unsafe_allow_html=True)
st.markdown("Personalize os nomes e valores, que são salvos automaticamente entre sessões.")

# Valores padrão iniciais (agora com IDs em vez de nomes fixos)
default_data = {
    "platforms": {
        "group_a": [
            {"id": 1, "name": "Kraken", "value": 678},
            {"id": 2, "name": "Gate", "value": 1956},
            {"id": 3, "name": "Coinbase", "value": 2463}
        ],
        "group_b": [
            {"id": 4, "name": "N26", "value": 195},
            {"id": 5, "name": "Revolut", "value": 2180},
            {"id": 6, "name": "Caixa", "value": 927}
        ]
    }
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
            return default_data
    return default_data

# Função para salvar valores
def save_values(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Carregar dados
saved_data = load_values()

# Inicializar session_state se necessário
if "app_data" not in st.session_state:
    st.session_state["app_data"] = saved_data

# Atualizar dados no session_state se houver mudanças no arquivo
if saved_data != st.session_state["app_data"]:
    st.session_state["app_data"] = saved_data

# Layout com duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Modificar Nomes e Valores")
    
    # Dividir inputs em duas colunas para melhor organização
    input_col1, input_col2 = st.columns(2)
    
    new_data = {"platforms": {"group_a": [], "group_b": []}}
    
    with input_col1:
        st.markdown("**Grupo A**")
        for platform in st.session_state["app_data"]["platforms"]["group_a"]:
            st.markdown(f'<div class="platform-name">Plataforma {platform["id"]}</div>', unsafe_allow_html=True)
            new_name = st.text_input(
                label=f"Nome Plataforma {platform['id']}",
                value=platform["name"],
                key=f"name_a_{platform['id']}",
                label_visibility="collapsed"
            )
            new_value = st.number_input(
                label=f"Valor Plataforma {platform['id']}",
                value=platform["value"],
                key=f"value_a_{platform['id']}",
                step=1,
                min_value=0
            )
            new_data["platforms"]["group_a"].append({
                "id": platform["id"],
                "name": new_name,
                "value": new_value
            })
    
    with input_col2:
        st.markdown("**Grupo B**")
        for platform in st.session_state["app_data"]["platforms"]["group_b"]:
            st.markdown(f'<div class="platform-name">Plataforma {platform["id"]}</div>', unsafe_allow_html=True)
            new_name = st.text_input(
                label=f"Nome Plataforma {platform['id']}",
                value=platform["name"],
                key=f"name_b_{platform['id']}",
                label_visibility="collapsed"
            )
            new_value = st.number_input(
                label=f"Valor Plataforma {platform['id']}",
                value=platform["value"],
                key=f"value_b_{platform['id']}",
                step=1,
                min_value=0
            )
            new_data["platforms"]["group_b"].append({
                "id": platform["id"],
                "name": new_name,
                "value": new_value
            })
    
    # Botões em colunas
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 Salvar Alterações", use_container_width=True):
            st.session_state["app_data"] = new_data
            save_values(new_data)
            st.success("Dados salvos com sucesso!")
            st.rerun()
            
    with btn_col2:
        if st.button("🔄 Restaurar Valores Padrão", use_container_width=True):
            st.session_state["app_data"] = default_data
            save_values(default_data)
            st.success("Valores padrão restaurados!")
            st.rerun()

with col2:
    st.subheader("Visualização")
    
    # Preparar dados para visualização
    all_platforms = (
        st.session_state["app_data"]["platforms"]["group_a"] + 
        st.session_state["app_data"]["platforms"]["group_b"]
    )
    
    # Criar DataFrame com os valores atuais
    df = pd.DataFrame({
        "ID": [p["id"] for p in all_platforms],
        "Plataforma": [p["name"] for p in all_platforms],
        "Valor": [p["value"] for p in all_platforms],
        "Grupo": ["A"] * 3 + ["B"] * 3
    })
    
    # Mostrar tabela com formatação
    st.dataframe(
        df[["Plataforma", "Valor", "Grupo"]].style.format({'Valor': '{:,.0f}'}), 
        height=300, 
        use_container_width=True,
        hide_index=True
    )
    
    # Calcular somas
    total = df['Valor'].sum()
    
    # Calcular soma do grupo A e grupo B
    group_a_sum = df[df['Grupo'] == 'A']['Valor'].sum()
    group_b_sum = df[df['Grupo'] == 'B']['Valor'].sum()
    
    # Mostrar métricas com cards estilizados
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="💰 **Total Geral**", value=f"€{total:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Layout para as somas parciais
    col21, col22 = st.columns(2)
    with col21:
        st.markdown('<div class="metric-card group-a">', unsafe_allow_html=True)
        st.metric(label="🅰️ Grupo A", value=f"€{group_a_sum:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col22:
        st.markdown('<div class="metric-card group-b">', unsafe_allow_html=True)
        st.metric(label="🅱️ Grupo B", value=f"€{group_b_sum:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
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

# Adicionar gráfico de barras simples usando Streamlit nativo
st.subheader("Comparação Visual dos Valores")
if total > 0:  # Só mostrar gráfico se houver valores
    st.bar_chart(df.set_index('Plataforma')['Valor'])

# Informações adicionais
st.info("💡 Dica: Os nomes e valores são automaticamente salvos e persistem entre execuções.")
