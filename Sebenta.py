import streamlit as st
import time
from datetime import datetime
import av
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import threading

# Configuração da página
st.set_page_config(
    page_title="Pedômetro por Câmera",
    page_icon="👣",
    layout="wide"
)

# Inicializar estado da sessão
if 'passos' not in st.session_state:
    st.session_state.passos = 0
if 'monitorando' not in st.session_state:
    st.session_state.monitorando = False
if 'ultimo_passo' not in st.session_state:
    st.session_state.ultimo_passo = 0
if 'inicio_tempo' not in st.session_state:
    st.session_state.inicio_tempo = None
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0
if 'last_frame' not in st.session_state:
    st.session_state.last_frame = None

# Título e instruções
st.title("👣 Pedômetro por Câmera - Detecção Automática")
st.markdown("---")

# Configuração do WebRTC
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# Função para processar os frames da câmera
class VideoProcessor:
    def __init__(self):
        self.passos_detectados = 0
        self.last_frame = None
        self.movement_threshold = 5000
        self.last_step_time = 0
        
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.last_frame is None:
            self.last_frame = gray
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        
        # Calcular diferença entre frames
        frame_diff = cv2.absdiff(self.last_frame, gray)
        thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        movement_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.movement_threshold:
                movement_detected = True
                break
        
        # Detectar passo baseado no movimento
        current_time = time.time()
        if (movement_detected and 
            current_time - self.last_step_time > 0.5 and  # Limite de 0.5s entre passos
            st.session_state.monitorando):
            
            self.passos_detectados += 1
            st.session_state.passos = self.passos_detectados
            self.last_step_time = current_time
            
            # Registrar no histórico
            st.session_state.historico.append({
                'timestamp': datetime.now(),
                'passos': st.session_state.passos,
                'tipo': 'camera'
            })
        
        self.last_frame = gray
        
        # Desenhar informações na imagem
        cv2.putText(img, f"Passos: {self.passos_detectados}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Status: {'Ativo' if st.session_state.monitorando else 'Pausado'}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if st.session_state.monitorando else (0, 0, 255), 2)
        
        if movement_detected:
            cv2.putText(img, "MOVIMENTO DETECTADO!", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Controles principais
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎥 Iniciar Câmera", type="primary", use_container_width=True):
        st.session_state.monitorando = True
        st.session_state.inicio_tempo = time.time()
        st.rerun()

with col2:
    if st.button("⏸️ Pausar Contagem", type="secondary", use_container_width=True):
        st.session_state.monitorando = False
        st.rerun()

with col3:
    if st.button("🔁 Reiniciar Tudo", use_container_width=True):
        st.session_state.passos = 0
        st.session_state.monitorando = False
        st.session_state.inicio_tempo = None
        st.session_state.historico = []
        st.rerun()

# Status
if st.session_state.monitorando:
    st.success("✅ Câmera ativa - Movimente-se para detectar passos!")
else:
    st.warning("⏸️ Monitoramento pausado")

# Stream de vídeo
st.markdown("---")
st.subheader("📷 Visualização da Câmera")

webrtc_ctx = webrtc_streamer(
    key="pedometer",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

# Métricas em tempo real
st.markdown("---")
st.subheader("📊 Estatísticas em Tempo Real")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Passos Detectados", st.session_state.passos, delta=None)

with col2:
    if st.session_state.inicio_tempo:
        tempo_decorrido = time.time() - st.session_state.inicio_tempo
        st.metric("Tempo", f"{int(tempo_decorrido)//60}:{int(tempo_decorrido)%60:02d}")

with col3:
    if st.session_state.passos > 0 and st.session_state.inicio_tempo:
        taxa = st.session_state.passos / (time.time() - st.session_state.inicio_tempo) * 60
        st.metric("Taxa", f"{taxa:.1f} passos/min")
    else:
        st.metric("Taxa", "0.0/min")

with col4:
    progresso = min((st.session_state.passos / 100) * 100, 100)
    st.metric("Progresso", f"{progresso:.0f}%")

# Calculadora de métricas
st.markdown("---")
st.subheader("📈 Calculadora de Performance")

col1, col2 = st.columns(2)

with col1:
    comprimento_passo = st.slider("Comprimento do seu passo (cm)", 60, 90, 75)

with col2:
    peso = st.slider("Seu peso (kg)", 50, 120, 70)

if st.session_state.passos > 0:
    distancia = (st.session_state.passos * comprimento_passo) / 100000
    calorias = st.session_state.passos * peso * 0.0004
    
    st.info(f"**🚶 Distância percorrida:** {distancia:.2f} km")
    st.info(f"**🔥 Calorias queimadas:** {calorias:.1f} kcal")

# Modo de simulação para teste
st.markdown("---")
st.subheader("🎯 Simulação para Teste")

col1, col2 = st.columns(2)

with col1:
    if st.button("👣 Simular 1 Passo", use_container_width=True):
        st.session_state.passos += 1
        st.session_state.historico.append({
            'timestamp': datetime.now(),
            'passos': st.session_state.passos,
            'tipo': 'simulado'
        })
        st.rerun()

with col2:
    if st.button("🚶 Simular 10 Passos", use_container_width=True):
        for i in range(10):
            st.session_state.passos += 1
            st.session_state.historico.append({
                'timestamp': datetime.now(),
                'passos': st.session_state.passos,
                'tipo': 'simulado'
            })
        st.rerun()

# Instruções detalhadas
st.markdown("---")
with st.expander("📋 Instruções Detalhadas de Uso"):
    st.markdown("""
    ## Como usar o pedômetro por câmera:
    
    ### 🎥 Configuração da Câmera:
    1. Clique em **"Iniciar Câmera"**
    2. Permita o acesso à câmera quando solicitado
    3. Posicione o dispositivo para enxergar sua área de movimento
    
    ### 🚶 Como funcionar:
    1. **Posicione a câmera** em um local estável
    2. **Ande em frente à câmera** (de um lado para o outro)
    3. **Movimentos grandes** são mais facilmente detectados
    4. Mantenha **iluminação adequada**
    
    ### ⚙️ Dicas para melhor detecção:
    - Use em ambiente bem iluminado
    - Posicione a câmera na altura do torso
    - Ande naturalmente em frente à câmera
    - Evite movimentos muito rápidos
    
    ### 🔧 Solução de problemas:
    - Se não detectar, aumente o movimento
    - Verifique se a câmera está focando corretamente
    - Use a simulação para testar se necessário
    """)

# Informações técnicas
with st.expander("🔧 Informações Técnicas"):
    st.markdown("""
    **Tecnologia utilizada:**
    - OpenCV para processamento de imagem
    - WebRTC para transmissão de vídeo
    - Detecção de movimento por diferença de frames
    - Filtros para evitar detecções falsas
    
    **Precisão:**
    - Melhor em ambientes controlados
    - Depende da qualidade da câmera
    - Ideal para demonstração e uso casual
    """)

# Rodapé
st.markdown("---")
st.caption("👣 Pedômetro por Câmera - Detecção automática de passos através de movimento")
st.caption("📷 Funciona com a câmera do seu dispositivo - Permita o acesso quando solicitado")

# CSS personalizado
st.markdown("""
<style>
.stButton button {
    border-radius: 10px;
    font-weight: bold;
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)
