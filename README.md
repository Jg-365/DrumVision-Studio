# DrumVision Studio

**DrumVision Studio** transforma movimentos reais de bateria em eventos musicais confiáveis (MIDI e/ou áudio) usando múltiplas câmeras e calibração inteligente. O objetivo é oferecer uma experiência profissional, com baixa latência e alta precisão, tanto para músicos quanto para criadores de conteúdo.

## Propósito

Transformar movimentos normais de bateria (mãos/baquetas, golpes, rebound, foot) em eventos musicais confiáveis (MIDI e/ou áudio), com múltiplas câmeras atribuídas a partes específicas do kit e com um modo opcional onde o usuário calibra usando objetos reais.

## Público-alvo

- Bateristas
- Criadores de conteúdo
- Estúdios caseiros
- Educação musical
- Live/stream
- VR/experimentos

## Experiência do usuário (fluxo)

### 1) Setup rápido (assistente)

O app detecta todas as câmeras disponíveis (USB, integrada, IP/NDI, captura HDMI). O usuário escolhe:

- **Modo:**
  - Air Drums (só no ar)
  - Object Drums (batendo em objetos reais)
- **Saída:**
  - Áudio interno
  - VST
  - MIDI (Ableton/Logic/FL Studio)
  - Ou ambos
- **Mapa do kit:** presets (Rock, Pop, Jazz, Lo-fi, Electronic), cada um com pads e sons

### 2) Calibração guiada (diferencial)

#### A) Calibração por “Zonas virtuais” (Air)

- O app mostra uma overlay com o kit.
- O usuário posiciona o kit na tela (arrasta e solta pads: caixa, chimbal, tons, crash, ride, bumbo).
- O app pede: “Faça 3 batidas na caixa” → aprende gesto e velocidade típica.

Ajustes automáticos:

- Sensibilidade
- Anti-doble-trigger (re-trigger)
- Thresholds por peça (caixa geralmente mais sensível que crash)

#### B) Calibração por “Objetos reais” (Object Drums)

- O usuário coloca objetos no lugar (almofada = caixa, caderno = tons, borda da mesa = chimbal, tapete = bumbo).
- O app entra em modo “marcar alvos”:
  - Enquadra o objeto e clica “definir caixa”.
  - Pode usar marcadores opcionais (fitas coloridas/QR/ArUco) para melhorar robustez.
- Depois: “Toque 5 vezes nesse objeto” → o app aprende:
  - Área de impacto
  - Padrões de oclusão
  - Tempo de contato / frame do impacto
  - Dinâmica (forte/fraco)

Resultado: o app dispara som quando e somente quando há impacto real no objeto (ou aproximação + gesto), com muito menos falsos positivos.

## Multi-câmera (coração do sistema)

### Objetivo

Cada câmera pode ser especializada:

- Cam 1 (frontal superior): mãos/baquetas + pratos
- Cam 2 (lateral): caixa + tons
- Cam 3 (baixo / pé): bumbo e hi-hat pedal
- Cam 4 (overhead): kit inteiro, fallback e correção

### Funcionalidades

- **Roteamento por peça:** “Snare usa Cam 2”, “Ride usa Cam 1”, “Kick usa Cam 3”.
- **Fusão inteligente:** cada câmera gera eventos candidatos com confiança; o módulo central valida e consolida.
- **Deduplicação:** se duas câmeras detectam o mesmo golpe, mantém 1 evento e usa a melhor intensidade.

### Sincronização

- **Auto-sync:** alinhamento por clap/padrão curto (via áudio ou correlação visual).
- **Compensação de latência:** equalização do delay por câmera.

## IA: o que exatamente ela faz

### 1) Rastreamento

- Mãos/baquetas: hand tracking com landmarks + tracking temporal.
- Detector de baqueta opcional (quando visível).
- Pé: pose/ankle tracking ou câmera dedicada.

### 2) Detecção de golpe (ponto crítico)

Um golpe válido é a combinação de:

- Trajetória descendente (velocidade + aceleração)
- Cruzamento do plano de impacto (zona virtual) OU contato com objeto (Object)
- Padrão de rebound (subida rápida após o impacto)
- Janela de bloqueio (debounce) configurável por peça
- Classificador “hit vs gesture” treinado para reduzir falsos positivos

### 3) Dinâmica musical (expressividade)

- **Velocity (MIDI 1–127):** estimado por pico de velocidade, amplitude e “sharpness”.
- **Controles avançados:**
  - Ghost notes
  - Rimshot
  - Open/closed hi-hat (posição do pé ou gesto dedicado)

## Motor de som e integração musical

### Saídas possíveis

- **MIDI virtual (principal):** notas GM Drum ou customizadas, velocity e aftertouch opcional.
- **Áudio interno:** sampler com kits prontos (WAV multi-velocity) e efeitos (compressor, reverb, EQ).
- **VST/AU bridge:** integração com plugins como Superior Drummer e Addictive Drums.

### Latência (tocável)

Pipeline em tempo real com:

- Inferência acelerada (GPU quando disponível)
- Tracking leve (priorizar modelos rápidos)
- Buffer de áudio curto
- Modo “Performance” para reduzir overlays e logs

## Interface (UI) pensada para músico

### Tela principal (Performance)

- Visual do kit com pads acendendo quando detecta hit
- Medidores de latência e confiança
- Botão “panic” (limpa stuck notes e reinicia áudio)

### Tela de Roteamento Multi-cam

- Lista de câmeras conectadas (preview pequeno)
- Seleção de câmera por peça + prioridade + fallback
- Estado: FPS, ping, drift, delay

### Tela de Calibração

- Wizard com etapas (posicionamento, teste, ajuste fino)
- “Modo aprendizado” de 30 segundos tocando livre para sugerir thresholds
- Perfis: “Meu kit na sala”, “Meu kit no quarto”, “Live”

## Recursos avançados (produto “uau”)

- Perfis por ambiente (luz baixa, fundo confuso, câmera barata)
- Modo stream: overlay + integração OBS (virtual camera)
- Gravação: export MIDI + áudio + vídeo sincronizado
- Treino: metrônomo, rudimentos, feedback de precisão
- Detecção de erros: “você está adiantando a caixa” / “chimbal inconsistente”
- Modo educativo: sticking (R/L) estimado

## Confiabilidade (100% funcional na prática)

- Calibração obrigatória por setup
- Anti-falso positivo (classificador de hit + debounce por peça)
- Multi-câmera plug-and-play
- Modo Object recomendado para maior estabilidade

## Requisitos mínimos realistas

- Webcam 60fps recomendada (30fps funciona com tuning)
- Iluminação decente ou modo “low light”
- GPU ideal, mas roda em CPU com modelos leves

## Diretrizes de produto

- Layout mobile-first, responsivo, moderno e profissional.
- Documentação 100% integrada e disponível.
- Uso de bibliotecas modernas de IA com Python e infraestrutura livre de conflitos.

