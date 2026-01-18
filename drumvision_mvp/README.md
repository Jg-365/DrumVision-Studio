# DrumVision MVP

DrumVision MVP é um protótipo funcional de Air Drums por visão computacional com baixa latência, calibração guiada e saída MIDI/Áudio.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como rodar

```bash
python run.py
```

## Calibração (wizard)

1. Pressione `c` para iniciar a calibração.
2. **Passo 1: Layout**
   - Aponte para a posição da peça solicitada e pressione `1` para definir.
   - Ajuste o raio com `+` ou `-`.
   - Pressione `n` para pular a peça atual.
   - Pressione `r` e clique em dois pontos para definir ROI (modo objeto).
3. **Passo 2: Thresholds**
   - Toque 3 vezes em cada peça para calibrar a velocidade mínima.
4. Ao finalizar, pressione `s` para salvar a configuração.

## Controles

- `c` iniciar calibração
- `s` salvar configuração
- `l` carregar configuração
- `m` alternar MIDI on/off
- `o` alternar modo Air/Object
- `d` debug overlay
- `q` sair

## Conectar MIDI no seu DAW

- O app tenta criar uma porta virtual chamada **"DrumVision MIDI"**.
- Se a porta virtual não estiver disponível, o app tenta usar a primeira porta MIDI disponível no sistema.
- No seu DAW (Ableton/Logic/FL), selecione a porta MIDI como entrada para um instrumento de bateria.

## Dicas de iluminação e posicionamento

- Use uma iluminação frontal suave e homogênea.
- Evite fundos muito complexos.
- Posicione a câmera de frente para as mãos/baquetas, com o kit visível.

## Estrutura do projeto

```
./
  run.py
  drumvision/
    camera.py
    tracking.py
    hit_detection.py
    midi_out.py
    audio_out.py
    calibrator.py
    kit.py
    ui.py
    config.py
    utils.py
  configs/
    default.json
  assets/
    samples/
```
