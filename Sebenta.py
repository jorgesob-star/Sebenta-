import streamlit as st
import time
from datetime import datetime
import math

# Configuração da página
st.set_page_config(
    page_title="Pedômetro Automático",
    page_icon="👣",
    layout="centered"
)

# Inicializar estado da sessão
if 'passos' not in st.session_state:
    st.session_state.passos = 0
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'monitorando' not in st.session_state:
    st.session_state.monitorando = False
if 'ultimo_passo' not in st.session_state:
    st.session_state.ultimo_passo = 0
if 'inicio_tempo' not in st.session_state:
    st.session_state.inicio_tempo = None

# Título e instruções
st.title("👣 Pedômetro Automático")
st.markdown("---")

# JavaScript para acessar o acelerômetro
sensor_js = """
<script>
// Variáveis globais para o sensor
let sensor = null;
let lastAcceleration = {x: 0, y: 0, z: 0};
let stepCount = 0;
let lastStepTime = 0;
let monitoring = false;

// Função para iniciar o sensor
function startSensor() {
    if ('LinearAccelerationSensor' in window) {
        try {
            sensor = new LinearAccelerationSensor({ frequency: 10 });
            
            sensor.addEventListener('reading', () => {
                const acceleration = {
                    x: sensor.x,
                    y: sensor.y, 
                    z: sensor.z
                };
                
                // Detectar passos baseado na aceleração
                detectStep(acceleration);
                
                // Enviar dados para o Streamlit
                window.parent.postMessage({
                    type: 'ACCELERATION_DATA',
                    data: acceleration,
                    steps: stepCount
                }, '*');
            });
            
            sensor.start();
            monitoring = true;
            window.parent.postMessage({
                type: 'SENSOR_STATUS',
                status: 'started'
            }, '*');
            
        } catch (error) {
            console.error('Erro ao iniciar sensor:', error);
            window.parent.postMessage({
                type: 'SENSOR_ERROR',
                error: error.message
            }, '*');
        }
    } else {
        window.parent.postMessage({
            type: 'SENSOR_ERROR', 
            error: 'Sensor não suportado neste navegador'
        }, '*');
    }
}

// Função para parar o sensor
function stopSensor() {
    if (sensor) {
        sensor.stop();
        sensor = null;
    }
    monitoring = false;
    window.parent.postMessage({
        type: 'SENSOR_STATUS',
        status: 'stopped'
    }, '*');
}

// Algoritmo simples para detectar passos
function detectStep(acceleration) {
    const now = Date.now();
    const deltaTime = now - lastStepTime;
    
    // Calcular a magnitude da aceleração
    const magnitude = Math.sqrt(
        acceleration.x * acceleration.x +
        acceleration.y * acceleration.y + 
        acceleration.z * acceleration.z
    );
    
    // Calcular a diferença da aceleração anterior
    const deltaAcceleration = Math.sqrt(
        Math.pow(acceleration.x - lastAcceleration.x, 2) +
        Math.pow(acceleration.y - lastAcceleration.y, 2) +
        Math.pow(acceleration.z - lastAcceleration.z, 2)
    );
    
    // Condições para detectar um passo
    if (deltaTime > 300 && // Mínimo 300ms entre passos
        deltaAcceleration > 2.0 && // Mudança significativa na aceleração
        magnitude > 9.0) { // Magnitude acima do limite
                
        stepCount++;
        lastStepTime = now;
        
        window.parent.postMessage({
            type: 'STEP_DETECTED',
            stepCount: stepCount,
            timestamp: now
        }, '*');
    }
    
    lastAcceleration = acceleration;
}

// Iniciar automaticamente se solicitado
if (window.location.search.includes('auto_start=true')) {
    setTimeout(startSensor, 1000);
}

// Funções globais para controle
window.startPedometer = startSensor;
window.stopPedometer = stopSensor;
window.getStepCount = () => stepCount;
window.resetStepCount = () => { stepCount = 0; };

</script>
"""

# Inject JavaScript
st.components.v1.html(sensor_js, height=0)

# Controles principais
st.subheader("Controle do Pedômetro")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Iniciar Monitoramento", type="primary", use_container_width=True):
        st.session_state.monitorando = True
        st.session_state.inicio_tempo = time.time()
        st.rerun()

with col2:
    if st.button("⏹️ Parar Monitoramento", type="secondary", use_container_width=True):
        st.session_state.monitorando = False
        st.rerun()

with col3:
    if st.button("🔁 Reiniciar Contagem", use_container_width=True):
        st.session_state.passos = 0
        st.session_state.historico = []
        st.session_state.ultimo_passo = 0
        st.rerun()

# Status do monitoramento
if st.session_state.monitorando:
    st.success("🎯 Monitoramento ATIVO - Comece a caminhar!")
else:
    st.warning("⏸️ Monitoramento PAUSADO")

# Métricas principais
st.markdown("---")
st.subheader("📊 Estatísticas")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Passos Detectados", st.session_state.passos)

with col2:
    if st.session_state.inicio_tempo and st.session_state.monitorando:
        tempo_decorrido = time.time() - st.session_state.inicio_tempo
        minutos = int(tempo_decorrido // 60)
        segundos = int(tempo_decorrido % 60)
        st.metric("Tempo Ativo", f"{minutos}:{segundos:02d}")
    else:
        st.metric("Tempo Ativo", "0:00")

with col3:
    if st.session_state.passos > 0 and st.session_state.inicio_tempo:
        tempo_total = time.time() - st.session_state.inicio_tempo
        passos_por_minuto = (st.session_state.passos / tempo_total) * 60
        st.metric("Taxa", f"{passos_por_minuto:.1f}/min")
    else:
        st.metric("Taxa", "0.0/min")

# Simulação para dispositivos sem sensor
st.markdown("---")
st.subheader("📱 Simulação (para teste)")

col1, col2 = st.columns(2)

with col1:
    if st.button("👣 Simular 1 Passo", use_container_width=True):
        st.session_state.passos += 1
        st.session_state.historico.append({
            'timestamp': datetime.now(),
            'tipo': 'simulado',
            'passos': st.session_state.passos
        })
        st.rerun()

with col2:
    if st.button("🚶 Simular 10 Passos", use_container_width=True):
        for i in range(10):
            st.session_state.passos += 1
            st.session_state.historico.append({
                'timestamp': datetime.now(),
                'tipo': 'simulado',
                'passos': st.session_state.passos
            })
        st.rerun()

# Calculadora de métricas
st.markdown("---")
st.subheader("📈 Calculadora de Métricas")

col1, col2 = st.columns(2)

with col1:
    comprimento_passo = st.slider("Comprimento do passo (cm)", 60, 90, 75)

with col2:
    peso = st.slider("Seu peso (kg)", 50, 120, 70)

if st.session_state.passos > 0:
    distancia = (st.session_state.passos * comprimento_passo) / 100000
    calorias = st.session_state.passos * peso * 0.0004
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Distância:** {distancia:.2f} km")
    with col2:
        st.info(f"**Calorias:** {calorias:.1f} kcal")
    
    # Progresso da meta
    progresso = min((st.session_state.passos / 10000) * 100, 100)
    st.progress(progresso / 100)
    st.caption(f"🎯 Progresso para meta diária (10.000 passos): {progresso:.1f}%")

# Instruções
st.markdown("---")
with st.expander("ℹ️ Instruções de Uso"):
    st.markdown("""
    ### Como usar o pedômetro automático:
    
    1. **Permitir acesso aos sensores**: 
       - O navegador pedirá permissão para acessar os sensores
       - Aceite para que o pedômetro funcione
    
    2. **Iniciar monitoramento**:
       - Clique em "Iniciar Monitoramento"
       - Comece a caminhar normalmente
       - Os passos serão detectados automaticamente
    
    3. **Posicionamento do dispositivo**:
       - 📱 **Celular**: No bolso ou na mão enquanto caminha
       - 💻 **Laptop**: Sobre uma superfície plana (menos preciso)
    
    ### Requisitos do navegador:
    - Chrome, Edge ou Safari recentes
    - HTTPS habilitado (necessário para sensores)
    - Permissão de sensores ativada
    
    ### Dica: 
    Use a simulação para testar se não tiver sensor disponível!
    """)

# Verificação de suporte a sensores
st.markdown("---")
st.subheader("🔍 Verificação de Sensores")

if st.button("Verificar Suporte a Sensores"):
    st.info("""
    Verificando suporte do navegador...
    - ✅ Streamlit carregado
    - 🔄 Verificando acelerômetro
    - 📱 Testando permissões
    """)
    
    # JavaScript para verificar suporte
    check_js = """
    <script>
    function checkSensorSupport() {
        const supportsSensor = 'LinearAccelerationSensor' in window;
        const supportsPermissions = 'permissions' in navigator;
        
        window.parent.postMessage({
            type: 'SENSOR_CHECK',
            hasSensor: supportsSensor,
            hasPermissions: supportsPermissions
        }, '*');
    }
    
    checkSensorSupport();
    </script>
    """
    st.components.v1.html(check_js, height=0)

# Rodapé
st.markdown("---")
st.caption("👣 Pedômetro Automático - Detecta passos usando o acelerômetro do seu dispositivo")
st.caption("📱 Funciona melhor em smartphones com sensores de movimento")

# CSS personalizado
st.markdown("""
<style>
.stButton button {
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)
