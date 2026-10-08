# Escola São José de Vila Matilde — Logo Motion

`video/escola_sao_jose_logo_motion.mp4` — 10 s, 1080x1920 (9:16), 60 fps, H.264 + AAC, trilha original.

Roteiro: wipe diagonal (navy/laranja/branco) → coração desenhado em traço → caixa laranja com pop,
aba "ESCOLA", letras de "São José" subindo, "DE VILA MATILDE" revelado, "Instituto" com tracking →
brilho e batida do coração (lub-dub) → transição com zoom no coração, flash e ondas → logo em tela
cheia com raios de luz, partículas e push-in. A trilha (Mi maior, 120 BPM) acompanha cada evento.

O logo é recriado em vetor (`logo.html`, fontes Antonio e PT Serif, licença OFL) e renderizado
quadro a quadro com Playwright. Para regenerar:

```bash
mkdir -p build video
python3 music.py build/trilha.wav
node render.js build/video_sem_audio.mp4
ffmpeg -i build/video_sem_audio.mp4 -i build/trilha.wav -c:v copy -c:a aac -b:a 256k -shortest video/escola_sao_jose_logo_motion.mp4
```
