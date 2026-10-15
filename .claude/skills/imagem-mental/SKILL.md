---
name: imagem-mental
description: Cria imagens mentais (infográficos institucionais) para escolas a partir do logo da escola e da lista de pontos importantes (diferenciais, valores, pilares). Gera PNG para aprovação e, depois de aprovado, PDF vetorial e SVG organizados em camadas, prontos para abrir no CorelDRAW, Illustrator ou Inkscape. Use sempre que pedirem "imagem mental", "mapa mental da escola", "infográfico de diferenciais", "pilares da escola com o logo no centro", ou enviarem um logo de escola com uma lista de itens para montar uma arte, mesmo sem dizer "imagem mental".
---

# Imagem mental para escolas

Uma imagem mental é uma arte com **o logo da escola em destaque, no centro**, e os
**pontos importantes da escola** em volta. Cada ponto tem um ícone e um texto curto.
Os modelos de referência estão em `references/modelos/` e são descritos em
`references/modelos.md`.

## O que pedir ao usuário

Obrigatório:
1. **Logo da escola** (PNG com transparência, SVG, ou JPG com fundo branco).
2. **Itens** (os pontos importantes). O ideal é entre 4 e 8, com no máximo umas 6 palavras cada.

Opcional (use o padrão se não vier):
- **Layout**: veja a tabela abaixo. Sem pedido, gere a prévia com todos e sugira 2 ou 3.
- **Fundo**: branco (`#ffffff`) por padrão. Troque só se o usuário pedir.
- **Slogan**: frase curta. Alguns layouts colocam no centro (balões) ou na nuvem (árvore); os outros, abaixo.
- **Cores**: por padrão saem do próprio logo. Aceita uma lista hex.
- **Formato**: `quadrado` (padrão, 1080×1080), `retrato` (1080×1350), `stories`, `paisagem`, `a4`, `a4-paisagem`, `a3`.

Não invente itens. Se o usuário mandar só o logo, peça os itens.

## Layouts disponíveis

| layout    | modelo de origem | quando usar | itens |
|-----------|------------------|-------------|-------|
| `arco`    | Colégio Athena   | sóbrio e institucional, uma cor da marca | 5–8 |
| `anel`    | Koala (CDR)      | anel fechado com texto dentro das fatias | 4–8 |
| `leque`   | Espaço Criança Feliz | educação infantil, colorido | 4–6 |
| `petalas` | Estela Maris     | colorido e dinâmico, textos curtos | 5–8 |
| `arvore`  | Infan Gardeno    | ideia de crescimento; ótimo com slogan | 4–8 |
| `baloes`  | Instituto Pistori | post de rede social, com slogan no centro | 5–8 |
| `orbita`  | Koala (CDR, pág. 2) | itens dos dois lados do logo | 4–8 |
| `onda`    | Colégio Sagaz (CDR) | faixa horizontal com o logo embaixo | 3–6 |

## Fluxo

1. **Monte o JSON** em uma pasta de trabalho (copie `exemplos/athena.json` e adapte).
   O logo é um caminho relativo ao JSON.
   ```json
   {
     "escola": "Colégio Exemplo",
     "logo": "logo.png",
     "layout": "arco",
     "fundo": "#ffffff",
     "slogan": "",
     "itens": [
       {"texto": "Ensino Bilíngue", "icone": "world"},
       {"texto": "Projeto Social", "icone": "heart-handshake"}
     ]
   }
   ```
   Chaves opcionais: `cores` (lista hex da marca), `cores_itens` (uma cor por item),
   `modo_cor` (`marca` | `alternada` | `arco-iris`), `fonte` (`Poppins` | `Fredoka`),
   `formato`, `sombra` (true/false), `nome_arquivo`.

2. **Escolha os ícones.** Cada item precisa de um ícone que combine com o sentido do texto.
   Consulte `references/icones.md` e use a busca:
   ```bash
   python3 scripts/icones.py "Alimentação Saudável" "Corpo Docente"
   ```
   Se o ícone faltar ou não existir, o gerador escolhe sozinho, mas prefira escolher
   você mesmo. Evite repetir o mesmo ícone em dois itens.

3. **Prévia, se o layout não foi definido:**
   ```bash
   python3 scripts/gerar.py trabalho/config.json --previa
   ```
   Abra a folha gerada, confira e mostre ao usuário recomendando 2 ou 3 layouts.

4. **Gere o PNG para aprovação:**
   ```bash
   python3 scripts/gerar.py trabalho/config.json
   ```
   **Sempre abra o PNG gerado e revise** antes de entregar: texto cortado ou
   encostando, ícone que não combina, logo pequeno, contraste ruim. Ajuste o JSON
   (texto mais curto, `\n` para forçar quebra, outro ícone, outro layout) e gere de novo.

5. **Depois da aprovação**, gere os arquivos finais:
   ```bash
   python3 scripts/gerar.py trabalho/config.json --formatos png,pdf,svg
   ```
   - `*.pdf`: vetorial, textos em curvas. Serve para gráfica e abre no CorelDRAW.
   - `*_curvas.svg`: camadas nomeadas, textos em curvas. É o melhor para o CorelDRAW
     (Arquivo › Importar) e para salvar como `.cdr`.
   - `*_editavel.svg`: as mesmas camadas, com textos editáveis. Precisa das fontes de
     `assets/fontes/` instaladas no computador.
   - `*.png`: alta resolução (2× para redes; 300 dpi nos formatos A4/A3).

   Camadas do SVG: **Fundo, Decoração, Formas, Ícones, Textos, Logo**. Os objetos têm
   ids legíveis (`segmento-3`, `icone-3`, `texto-3`, `logo-escola`...).

6. **Trocar só o fundo:** `--fundo "#0b2a4a"`. Os textos que ficam fora das formas
   mudam para claro ou escuro sozinhos, e o logo ganha um disco branco quando precisa.

## Sobre CDR

O formato `.cdr` é fechado e não dá para gerá-lo diretamente. Entregue o
`_curvas.svg` (ou o PDF) e explique: no CorelDRAW, use **Arquivo › Importar**
(ou Abrir) e depois **Salvar como .cdr**. Os grupos e camadas nomeados continuam lá.

## Dicas de qualidade

- Textos longos deixam a fonte menor. Sugira encurtar ("Desenvolvimento de
  Competências e Habilidades" → "Competências e Habilidades").
- Logos muito horizontais ficam pequenos em layouts circulares. Nesse caso prefira
  `onda`, `leque` ou `baloes` com slogan.
- Para educação infantil combinam `leque`, `petalas`, `arvore` e `baloes`, com
  `"fonte": "Fredoka"`. Para fundamental, médio e escolas tradicionais, `arco`, `anel` e `orbita`.
- Se o logo for JPG com fundo branco, o fundo é removido sozinho. Ainda assim, peça PNG
  ou SVG quando possível.

## Dependências

Python 3 com `cairosvg`, `fonttools` e `Pillow`
(`pip install cairosvg fonttools pillow`). As fontes (Poppins e Fredoka, licença OFL) e
os ícones (Tabler Icons, licença MIT) já vêm em `assets/`.
