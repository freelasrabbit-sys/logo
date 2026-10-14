# Colégio Athena — Logo Motion

`video/colegio_athena_logo_motion.mp4` — 10 s, 1080x1920 (9:16), 60 fps, H.264 + AAC, trilha original.

Para regenerar:

```bash
mkdir -p build video
python3 music.py build/trilha.wav
python3 render.py build/video_sem_audio.mp4
ffmpeg -i build/video_sem_audio.mp4 -i build/trilha.wav -c:v copy -c:a aac -b:a 256k -shortest video/colegio_athena_logo_motion.mp4
```

# Capítulo I 30 anos — Abertura "depoimentos"

`capitulo1/video/capitulo1_abertura_depoimentos.mp4` — 4.8 s, 1080x1920 (9:16), 60 fps, H.264, sem áudio.

A cena fica em `capitulo1/abertura.html` (canvas, abre direto no navegador para ver em loop
via servidor local) e é renderizada quadro a quadro com Playwright:

```bash
cd capitulo1
NODE_PATH=$(npm root -g) node render.js video/capitulo1_abertura_depoimentos.mp4
# quadros soltos para conferência:
NODE_PATH=$(npm root -g) node render.js build/st --stills 1.0,2.4,4.8
```
