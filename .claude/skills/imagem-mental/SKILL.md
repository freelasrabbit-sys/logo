---
name: imagem-mental
description: Cria imagens mentais (infográficos institucionais) para escolas a partir do logo da escola e da lista de pontos importantes (diferenciais, valores, pilares). Analisa o logo e a quantidade de tópicos para propor 3 formatos que combinem, gera PNG para aprovação e, depois de aprovado, PDF vetorial e SVG em camadas, prontos para CorelDRAW, Illustrator ou Inkscape. Use sempre que pedirem "imagem mental", "mapa mental da escola", "infográfico de diferenciais", "pilares da escola com o logo no centro", ou enviarem um logo de escola com uma lista de itens para montar uma arte, mesmo sem dizer "imagem mental".
---

# Imagem mental para escolas

Uma imagem mental é uma arte com **o logo da escola em destaque** (de preferência no
centro) e os **pontos importantes da escola** organizados em volta, cada um com um ícone,
um título curto e, às vezes, uma descrição.

Os modelos enviados pela usuária estão em `references/modelos/` e são descritos em
`references/modelos.md`. Eles são a **referência de qualidade e de estilo**, não um
cardápio fechado. A skill deve ter discernimento para montar o formato que melhor
combina com cada logo e com cada quantidade de tópicos.

## Preferências da usuária (definidas em entrevista)

- **Entrada**: logo + tópicos. Os tópicos podem ter só título ou título e descrição.
  Normalmente são de 4 a 8.
- **Entrega**: gerar direto **3 opções bem diferentes** entre si, cada uma com **uma
  linha** explicando por que combina. Depois, refinar a escolhida.
- **Liberdade**: é esperado que crie formatos novos (hexágonos, escada, quebra-cabeça,
  colunas, raios...), sem nada muito diferente ou inusitado. Formatos ousados só
  quando ela pedir. Ela não quer ver sempre os mesmos modelos de exemplo.
- **Combinar com o logo**: usar as **cores** do logo e o **estilo** dele. Logo infantil
  e arredondado pede formas suaves, fonte arredondada e ícones preenchidos. Logo clássico
  e sóbrio pede linhas mais retas, Poppins e ícones de linha.
- **Fundo**: branco e limpo, sem elementos decorativos. Outra cor só quando ela pedir.
- **Sem assinatura** (não colocar "rabbit" nem crédito).
- **Formato padrão**: quadrado 1080×1080. As imagens são usadas em redes sociais,
  impressão, site e apresentações.
- **Arquivos finais** (depois da aprovação): PDF, SVG em camadas e PNG. O CDR sai pelo
  CorelDRAW (veja abaixo).

## Fluxo

### 1. Analise antes de desenhar
Abra o logo (Read) e anote:
- **Estilo**: `infantil` (traços arredondados, mascote, cores vivas) ou `classico`
  (brasão, serifa, formas retas, poucas cores).
- **Proporção**: logo horizontal largo, quadrado/redondo, ou vertical.
- **Cores**: o script tira a paleta sozinho. Confira se faz sentido e, se não fizer,
  passe `"cores"` à mão.
- **Tópicos**: a quantidade, se têm descrição, e se algum é longo demais. Se for,
  sugira uma versão mais curta e não invente conteúdo.

### 2. Crie 3 formatos diferentes (com criatividade)
**Regra principal: pelo menos 2 das 3 opções devem ser formatos novos**, pensados para
aquela escola, e não tirados do catálogo dos modelos. O catálogo serve de base de
qualidade e pode entrar como **no máximo 1** das 3 opções. Repetir os modelos de
exemplo foi apontado pela usuária como falta de criatividade.

Como chegar a um formato novo:
1. **Parta do conceito da escola**. Qual metáfora visual combina com o logo e com os
   tópicos? Exemplos:
   - pilares que sustentam a escola (escola clássica);
   - degraus ou crescimento (desempenho, aprovações);
   - árvore ou raízes (valores, tradição);
   - quebra-cabeça (formação integral);
   - engrenagens (método);
   - livro aberto (projeto pedagógico);
   - casa (acolhimento);
   - caminho ou trilha (jornada do aluno);
   - colmeia de hexágonos (comunidade);
   - constelação (protagonismo);
   - mapa ramificado (mapa mental clássico).
2. **Parta da forma do logo**: as letras, o símbolo ou o mascote podem virar a
   estrutura. Por exemplo, um logo com "C" grande pede um anel em C.
3. **Ajuste à quantidade de tópicos**: 3 pedem tríade ou trevo; 4, quadrantes ou cruz;
   5, estrela ou templo; 6, hexágono ou colmeia; 7 e 8, anel ou duas colunas.
4. **Fique dentro do bom senso**: o formato precisa ser claro e legível, sem nada
   inusitado demais (formatos ousados só a pedido). O logo continua sendo o destaque.

Os formatos novos ganham uma função em `scripts/layouts.py` (veja "Como criar um
layout novo"). Quando a usuária aprovar um, registre-o na tabela abaixo para reaproveitar.

**Catálogo** (modelos de referência e formatos já criados):

| layout | origem | combina com | tópicos | descrição |
|---|---|---|---|---|
| `arco` | modelo Athena | clássico, logo quadrado/redondo, 1 cor | 5–8 | ótima (texto fora) |
| `anel` | modelo Koala | clássico ou infantil, logo redondo | 4–8 | só curtas |
| `leque` | modelo Criança Feliz | infantil, logo horizontal | 4–6 | só curtas |
| `petalas` | modelo Estela Maris | infantil/colorido, logo compacto | 5–8 | boa (texto fora) |
| `arvore` | modelo Infan Gardeno | infantil, crescimento, com slogan | 4–8 | só curtas |
| `baloes` | modelo Pistori | qualquer, post com slogan | 5–8 | razoável |
| `orbita` | modelo Koala 2 | clássico, logo horizontal | 4–8 | só curtas |
| `onda` | modelo Sagaz | logo bem horizontal, poucos tópicos | 3–6 | boa (texto fora) |
| `pilares` | criado para o CTO | clássico/tradicional, "pilares da escola" | 3–6 | só curtas |
| `degraus` | criado para o CTO | desempenho, crescimento, logo horizontal | 3–6 | razoável |
| `mapa` | criado para o CTO | mapa mental clássico, qualquer estilo | 4–8 | boa |

### 3. Monte o JSON
Crie uma pasta de trabalho e use `exemplos/athena.json` como base. O logo é um caminho
relativo ao JSON.
```json
{
  "escola": "Colégio Exemplo",
  "logo": "logo.png",
  "estilo": "classico",
  "itens": [
    {"texto": "Ensino Bilíngue", "descricao": "Inglês todos os dias", "icone": "world"},
    {"texto": "Projeto Social", "icone": "heart-handshake"}
  ]
}
```
Chaves opcionais:
- `estilo` (`infantil` | `classico`): define a fonte (Fredoka ou Poppins) e o estilo dos
  ícones (preenchido ou linha).
- `fonte` (`Poppins` | `Fredoka`) e `estilo_icone` (`linha` | `solido`).
- `cores` (lista hex da marca), `cores_itens` (uma cor por item) e `modo_cor`
  (`marca` | `alternada` | `arco-iris`).
- `slogan`, `fundo`, `formato`, `sombra`, `layout` e `nome_arquivo`.

**Ícones**: escolha um por item, com sentido ligado ao texto e sem repetir. Use
`references/icones.md` e a busca:
```bash
python3 scripts/icones.py "Alimentação Saudável" "Corpo Docente"
```
Com estilo `infantil`, prefira ícones que tenham versão preenchida. Se algum não tiver,
todos saem em traço grosso, para manter o conjunto coerente.

### 4. Gere as 3 opções
```bash
python3 scripts/gerar.py trabalho/config.json --opcoes arco,petalas,baloes
```
O comando gera um PNG por opção e uma folha comparativa. **Abra e revise cada PNG**
antes de mostrar. Verifique:
- texto cortado, apertado ou pequeno demais;
- ícone que não combina com o tópico;
- logo pequeno ou encostando em outros elementos;
- cores sem contraste;
- tamanho de letra: o gerador já iguala todos os tópicos pelo menor que coube; se ficou
  pequeno, encurte o tópico que está limitando ou use um layout com mais espaço;
- composição desequilibrada.

Corrija e gere de novo. Para quebrar uma linha num ponto específico, use `\n` no texto.
Depois mostre as 3 opções à usuária, com uma linha de justificativa para cada.

### 5. Refine e entregue
Antes dos arquivos finais, **vetorize o logo** se ele veio em PNG/JPG de cores chapadas.
Assim ele entra no CorelDRAW como curvas editáveis, e não como foto:
```bash
python3 scripts/vetorizar_logo.py trabalho/logo.jpg --cores "#012650,#830006" -o trabalho/logo_vetor.svg
```
Confira o resultado (renderize e abra) e aponte `"logo": "logo_vetor.svg"` no JSON. Logos
com degradê, foto ou detalhes muito finos não vetorizam bem: nesse caso, mantenha o raster
e peça à escola o logo em vetor (.cdr, .ai, .pdf ou .svg).

Ajuste a opção escolhida conforme os pedidos dela. Depois da aprovação:
```bash
python3 scripts/gerar.py trabalho/config.json --layout <escolhido> --formatos png,pdf,svg
```
- `*.pdf`: vetorial, com textos em curvas. Serve para gráfica e abre no CorelDRAW.
- `*_curvas.svg`: camadas nomeadas e textos em curvas. É o melhor para levar ao CorelDRAW.
- `*_editavel.svg`: as mesmas camadas, com textos editáveis. Precisa das fontes de
  `assets/fontes/` instaladas.
- `*.png`: alta resolução (2× para redes; 300 dpi em A4 e A3).

Camadas: **Fundo, Decoração, Formas, Ícones, Textos, Logo**. Os ids são legíveis
(`segmento-3`, `icone-3`, `texto-3`, `logo-escola`...).

Outro fundo: use `--fundo "#0b2a4a"`. Os textos de fora passam para claro ou escuro
sozinhos, e o logo ganha um disco branco quando precisa.

**CDR**: o formato é fechado e não dá para gerá-lo diretamente. Entregue o
`_curvas.svg` e o PDF, e explique: no CorelDRAW, use **Arquivo › Importar** e depois
**Salvar como .cdr**. As camadas e os nomes dos objetos são mantidos.

## Como criar um layout novo

Quando um formato novo for a melhor escolha, adicione uma função em
`scripts/layouts.py`, seguindo o padrão das que já existem:

1. Use a assinatura `def nome(ctx: Ctx) -> Desenho`. Desenhe num espaço de ~1000×1000
   com o centro em (500, 500).
2. Distribua os itens por `ctx.n`. O layout precisa funcionar de 4 a 8 itens, ajustando
   os tamanhos pela quantidade.
3. Use os auxiliares:
   - `ctx.rotulo(i, x, y, tamanho=, max_larg=, ...)` para o título e a descrição;
   - `ctx.icone(i, cx, cy, tam, cor)`;
   - `ctx.logo(...)` ou `ctx.logo_no_circulo(...)`;
   - `ctx.cores_itens[i]`, `ctx.principal`, `ctx.texto_fora`;
   - `C.texto_sobre(cor)` e `C.legivel_em(cor, fundo)` para o contraste;
   - `setor`, `polar`, `ancora` e `sombra`.
4. Ponha cada elemento na camada certa com `D.add("Formas" | "Ícones" | "Textos" |
   "Logo" | "Decoração", svg)` e dê um id a ele (`forma-3`...).
5. Defina `D.caixa` com a área aproximada das formas. Os textos são somados
   automaticamente no enquadramento.
6. Registre o layout em `LAYOUTS` com o modo de cor padrão e uma descrição curta.
7. Teste com 4, 6 e 8 itens, com e sem descrição, e revise os PNGs.
8. Se a usuária aprovar, acrescente a linha na tabela de layouts deste arquivo
   (modelo = "criado para <escola>").

Mantenha o padrão visual dos modelos: logo como maior elemento, composição simétrica,
espaço em branco generoso, ícones simples, tipografia sem serifa e cores da marca.

## Dependências

Python 3 com `cairosvg`, `fonttools`, `Pillow`, `numpy` e `potracer`
(`pip install cairosvg fonttools pillow numpy potracer`). As fontes (Poppins e Fredoka, licença OFL) e
os ícones (Tabler Icons de linha e preenchidos, licença MIT) já vêm em `assets/`.
