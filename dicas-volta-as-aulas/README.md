# Capítulo I — 30 anos (depoimentos)

Edição em Remotion dos depoimentos dos 30 anos da Escola Capítulo I, com a identidade visual da arte "Dicas · Volta às Aulas".
Saída: `../video/capitulo_i_30_anos.mp4`, 1080x1920 (9:16), 30 fps, cerca de 3min54s. Todo corte tem esmaecimento de imagem e áudio; a troca de depoimento desliza.

## Estrutura
- `src/data/edl.json`: lista de cortes (trechos de cada vídeo) e legendas. É gerado por `scripts/build_edl.py`.
- `src/scenes/`: capa, moldura dos depoimentos (`Clip`) e encerramento.
- `src/components/`: fundo da identidade, título estilo adesivo, logo e legendas.
- `public/brand/logo-capitulo-i.png`: logo com fundo transparente.
- `public/clips/`: vídeos brutos já padronizados. Não vão para o Git; veja abaixo.

## Refazer do zero
1. Padronize os vídeos (rotação, 30 fps, volume) para `public/clips/` com os nomes usados em `scripts/build_edl.py`:
   `ffmpeg -i ORIGINAL.mp4 -vf fps=30 -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k public/clips/NOME.mp4`
2. Transcreva com faster-whisper (modelo `medium`, `word_timestamps=True`) e salve o JSON.
3. `python3 scripts/build_edl.py transcripts.json` para regenerar os cortes e as legendas.
4. `npx remotion studio` para pré-visualizar ou `npx remotion render Video30Anos ../video/capitulo_i_30_anos.mp4 --crf=22`.

Para mudar um corte, edite a lista `CUTS` em `scripts/build_edl.py`, em segundos do vídeo original, e rode o passo 3 de novo.
