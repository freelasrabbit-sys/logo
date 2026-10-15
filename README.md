# Colégio Athena — Logo Motion

`video/colegio_athena_logo_motion.mp4` — 10 s, 1080x1920 (9:16), 60 fps, H.264 + AAC, trilha original.

Para regenerar:

```bash
mkdir -p build video
python3 music.py build/trilha.wav
python3 render.py build/video_sem_audio.mp4
ffmpeg -i build/video_sem_audio.mp4 -i build/trilha.wav -c:v copy -c:a aac -b:a 256k -shortest video/colegio_athena_logo_motion.mp4
```

# Espaço Criança Feliz — legendas dinâmicas

`video/espaco_crianca_feliz_legendado.mp4` — 34 s, 1080x1920 (9:16), 30 fps, áudio original.
Legendas com tipografia cinética sincronizadas palavra por palavra (tempos em
`assets/legendas_palavras.json`, transcritos com Whisper), palavras-chave em destaque,
formas animadas, confetes, transições em faixas nas trocas de cenário e "camera punch".
Fontes: Lilita One e Fredoka (OFL, em `assets/fonts/`).

```bash
python3 legendas.py video_original.mp4 video/espaco_crianca_feliz_legendado.mp4
```
