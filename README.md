# Colégio Athena — Logo Motion

`video/colegio_athena_logo_motion.mp4` — 10 s, 1080x1920 (9:16), 60 fps, H.264 + AAC, trilha original.

Para regenerar:

```bash
mkdir -p build video
python3 music.py build/trilha.wav
python3 render.py build/video_sem_audio.mp4
ffmpeg -i build/video_sem_audio.mp4 -i build/trilha.wav -c:v copy -c:a aac -b:a 256k -shortest video/colegio_athena_logo_motion.mp4
```
