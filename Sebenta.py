import streamlit as st
import time
from datetime import datetime

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
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Adicionar Passo", use_container_width=True):
        st.session_state.passos += 1
        st.session_state.historico.append({
            'timestamp': datetime.now(),
            'passos': st.session_state.passos
        })
        st.rerun()

with col2:
    if st.button("➕➕ 10 Passos", use_container_width=True):
        for _ in range(10):
            st.session_state.passos += 1
            st.session_state.historico.append({
                'timestamp': datetime.now(),
                'passos': st.session_state.passos
            })
        st.rerun()

with col3:
    if st.button("🔁 Reset", use_container_width=True, type="secondary"):
        st.session_state.passos = 0
        st.session_state.inicio_tempo = time.time()
        st.session_state.ultimo_reset = datetime.now()
        st.session_state.historico = []
        st.rerun()

# Controle do temporizador
st.subheader("Temporizador")
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

with col2:
    if st.button("⏰ Reiniciar Temporizador", use_container_width=True):
        st.session_state.inicio_tempo = time.time()
        st.rerun()

# Visualização de dados
st.markdown("---")
st.subheader("Histórico de Atividade")

if st.session_state.historico:
    # Mostrar últimas entradas do histórico
    st.write("**Últimos passos registrados:**")
    
    # Criar uma visualização simples do histórico
    for i, registro in enumerate(st.session_state.historico[-10:]):  # Mostrar últimos 10
        hora = registro['timestamp'].strftime('%H:%M:%S')
        st.write(f"🕒 {hora} - {registro['passos']} passos")
    
    # Estatísticas básicas
    if len(st.session_state.historico) > 1:
        primeiro_registro = st.session_state.historico[0]['timestamp']
        ultimo_registro = st.session_state.historico[-1]['timestamp']
        tempo_total = (ultimo_registro - primeiro_registro).total_seconds() / 60
        passos_por_minuto = st.session_state.passos / tempo_total if tempo_total > 0 else 0
        
        st.info(f"📈 **Taxa média:** {passos_por_minuto:.1f} passos por minuto")
        st.info(f"⏱️ **Tempo total:** {tempo_total:.1f} minutos")
else:
    st.info("📝 Comece a adicionar passos para ver o histórico aqui.")

# Calculadora de métricas
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
    
    st.success(f"🚶 **Distância percorrida:** {distancia:.2f} km")
    st.success(f"🔥 **Calorias queimadas:** {calorias:.1f} kcal")
    
    # Meta diária (10.000 passos)
    progresso = min(st.session_state.passos / 10000 * 100, 100)
    st.progress(progresso / 100)
    st.caption(f"📊 Progresso para meta diária (10.000 passos): {progresso:.1f}%")

# Seção de metas
st.markdown("---")
st.subheader("🎯 Metas de Saúde")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Meta Diária", "10.000")
    st.caption("Passos recomendados")

with col2:
    restantes = max(0, 10000 - st.session_state.passos)
    st.metric("Faltam", f"{restantes}")
    st.caption("Passos para meta")

with col3:
    if st.session_state.passos > 0:
        percentual = min((st.session_state.passos / 10000) * 100, 100)
        st.metric("Concluído", f"{percentual:.1f}%")
    else:
        st.metric("Concluído", "0%")

# Dicas e informações
st.markdown("---")
with st.expander("💡 Dicas e Informações"):
    st.markdown("""
    ### Como usar o pedômetro:
    - **Adicionar Passo**: Clique para cada passo dado
    - **10 Passos**: Adiciona 10 passos de uma vez
    - **Reset**: Reinicia toda a contagem
    - **Temporizador**: Controla o tempo da atividade
    
    ### Benefícios de caminhar:
    - ✅ Melhora a saúde cardiovascular
    - ✅ Ajuda no controle de peso
    - ✅ Reduz o estresse
    - ✅ Fortalece músculos e ossos
    
    ### Curiosidades:
    - 10.000 passos ≈ 7-8 km
    - 1 passo ≈ 0,04-0,06 calorias
    - Caminhar 30min/dia traz benefícios significativos
    """)

# Rodapé
st.markdown("---")
st.caption("🎯 Pedômetro Digital - Mantenha-se ativo e saudável!")
st.caption("💪 Desenvolvido com Streamlit - Sem dependências externas")

# Modo de uso responsivo
with st.sidebar:
    st.header("📱 Como Usar")
    st.markdown("""
    1. **Inicie o temporizador** quando começar a caminhar
    2. **Clique em 'Adicionar Passo'** a cada passo
    3. **Ajuste suas métricas** pessoais ao lado
    4. **Acompanhe seu progresso** nas estatísticas
    5. **Reinicie** para nova sessão de exercícios
    
    **Dica:** Use o botão "10 Passos" para grupos de passos!
    """)
    
    # Quick actions
    st.header("⚡ Ações Rápidas")
    if st.button("🔄 Reiniciar Tudo", type="secondary"):
        st.session_state.passos = 0
        st.session_state.historico = []
        st.session_state.inicio_tempo = None
        st.session_state.ultimo_reset = datetime.now()
        st.rerun()
