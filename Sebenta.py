import streamlit as st
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt

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
        minutos = int(tempo_decorrido // 60)
        segundos = int(tempo_decorrido % 60)
        st.metric("Tempo Ativo", f"{minutos}min {segundos}s")
    else:
        st.metric("Tempo Ativo", "0min 0s")
with col3:
    st.metric("Último Reset", st.session_state.ultimo_reset.strftime("%H:%M"))

# Controles principais
st.subheader("Contador de Passos")
col1, col2 = st.columns(2)

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

# Iniciar/Parar temporizador
col1, col2 = st.columns(2)
with col1:
    if st.session_state.inicio_tempo is None:
        if st.button("▶️ Iniciar Temporizador", use_container_width=True):
            st.session_state.inicio_tempo = time.time()
            st.rerun()
    else:
        if st.button("⏹️ Parar Temporizador", use_container_width=True):
            st.session_state.inicio_tempo = None
            st.rerun()

# Modo automático
with col2:
    st.markdown("**Modo Simulação**")
    if st.button("🎯 Simular 10 passos", use_container_width=True):
        for _ in range(10):
            st.session_state.passos += 1
            st.session_state.historico.append({
                'timestamp': datetime.now(),
                'passos': st.session_state.passos
            })
        st.rerun()

# Visualização de dados
st.markdown("---")
st.subheader("Estatísticas e Visualização")

if st.session_state.historico:
    # Criar DataFrame do histórico
    df = pd.DataFrame(st.session_state.historico)
    df['hora'] = df['timestamp'].dt.strftime('%H:%M:%S')
    
    # Mostrar dados em tabela
    st.write("**Histórico de Passos:**")
    st.dataframe(df[['hora', 'passos']].tail(10), height=200)
    
    # Gráfico simples com matplotlib
    if len(df) > 1:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['hora'], df['passos'], marker='o', linewidth=2, markersize=4)
        ax.set_title('Progresso de Passos')
        ax.set_xlabel('Hora')
        ax.set_ylabel('Total de Passos')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Estatísticas
        tempo_total = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds() / 60
        passos_por_minuto = st.session_state.passos / tempo_total if tempo_total > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📈 **Taxa média:** {passos_por_minuto:.1f} passos/min")
        with col2:
            st.info(f"⏱️ **Tempo monitorado:** {tempo_total:.1f} min")
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
with st.expander("💡 Dicas para Uso Preciso"):
    st.markdown("""
    - **Mantenha o dispositivo estável** enquanto caminha
    - **Calibre o comprimento do seu passo** para medições precisas
    - **Use o botão de simulação** para testar diferentes cenários
    - **Reinicie o contador** a cada nova caminhada
    - **Meta sugerida:** 10.000 passos por dia para saúde ideal
    """)

# Rodapé
st.markdown("---")
st.caption("Pedômetro Digital © 2024 | Desenvolvido com Streamlit")

# Instruções de instalação
with st.sidebar:
    st.header("ℹ️ Instruções")
    st.markdown("""
    ### Como usar:
    1. Clique em **Adicionar Passo** para cada passo
    2. Use **Reset** para começar nova contagem
    3. Ajuste suas métricas pessoais
    4. Acompanhe seu progresso no gráfico
    
    ### Métricas calculadas:
    - 📊 Total de passos
    - 🚶 Distância percorrida
    - 🔥 Calorias queimadas
    - ⏱️ Tempo de atividade
    """)
