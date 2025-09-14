import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Pedômetro Digital",
    page_icon="👣",
    layout="centered"
)

# Inicializar estado da sessão
if 'passos' not in st.session_state:
    st.session_state.passos = 0
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'inicio_tempo' not in st.session_state:
    st.session_state.inicio_tempo = None
if 'ultimo_reset' not in st.session_state:
    st.session_state.ultimo_reset = datetime.now()

# Título e instruções
st.title("👣 Pedômetro Digital")
st.markdown("---")

# Métricas principais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Passos Hoje", st.session_state.passos)
with col2:
    if st.session_state.inicio_tempo:
        tempo_decorrido = time.time() - st.session_state.inicio_tempo
        st.metric("Tempo Ativo", f"{int(tempo_decorrido // 60)}min {int(tempo_decorrido % 60)}s")
with col3:
    st.metric("Último Reset", st.session_state.ultimo_reset.strftime("%H:%M"))

# Controles principais
st.subheader("Contador de Passos")
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("➕ Adicionar Passo", use_container_width=True):
        st.session_state.passos += 1
        st.session_state.historico.append({
            'timestamp': datetime.now(),
            'passos': st.session_state.passos
        })
        st.rerun()

with col2:
    if st.button("🔁 Reset", use_container_width=True):
        st.session_state.passos = 0
        st.session_state.inicio_tempo = time.time()
        st.session_state.ultimo_reset = datetime.now()
        st.session_state.historico = []
        st.rerun()

# Modo automático (simulação)
with col3:
    st.markdown("**Modo Automático**")
    auto_steps = st.slider("Passos por minuto", 0, 120, 60, key="auto_slider")

# Iniciar/Parar temporizador
if st.session_state.inicio_tempo is None:
    if st.button("▶️ Iniciar Temporizador", use_container_width=True):
        st.session_state.inicio_tempo = time.time()
        st.rerun()
else:
    if st.button("⏹️ Parar Temporizador", use_container_width=True):
        st.session_state.inicio_tempo = None
        st.rerun()

# Visualização de dados
st.markdown("---")
st.subheader("Estatísticas e Visualização")

if st.session_state.historico:
    # Criar DataFrame do histórico
    df = pd.DataFrame(st.session_state.historico)
    df['hora'] = df['timestamp'].dt.strftime('%H:%M:%S')
    
    # Gráfico de progresso
    fig = px.line(df, x='hora', y='passos', 
                 title='Progresso de Passos ao Longo do Tempo',
                 labels={'hora': 'Hora', 'passos': 'Total de Passos'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas
    if len(df) > 1:
        tempo_total = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds() / 60
        passos_por_minuto = st.session_state.passos / tempo_total if tempo_total > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📈 **Taxa média:** {passos_por_minuto:.1f} passos/min")
        with col2:
            st.info(f"⏱️ **Tempo monitorado:** {tempo_total:.1f} minutos")
else:
    st.info("Comece a adicionar passos para ver estatísticas e gráficos.")

# Calculadora de calorias e distância
st.markdown("---")
st.subheader("Calculadora de Métricas")

col1, col2 = st.columns(2)

with col1:
    comprimento_passo = st.slider("Comprimento do passo (cm)", 50, 100, 70)

with col2:
    peso = st.slider("Peso (kg)", 40, 150, 70)

if st.session_state.passos > 0:
    distancia = (st.session_state.passos * comprimento_passo) / 100000
    calorias = st.session_state.passos * peso * 0.0004
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🚶 **Distância:** {distancia:.2f} km")
    with col2:
        st.success(f"🔥 **Calorias:** {calorias:.1f} kcal")

# Dicas e informações
st.markdown("---")
with st.expander("💡 Dicas para Uso Precisa"):
    st.markdown("""
    - Mantenha o dispositivo estável enquanto caminha
    - Calibre o comprimento do seu passo para medições precisas
    - Use o modo automático para simular diferentes intensidades
    - Reinicie o contador a cada nova caminhada
    """)

# Rodapé
st.markdown("---")
st.caption("Pedômetro Digital © 2025 | Desenvolvido com Streamlit")
