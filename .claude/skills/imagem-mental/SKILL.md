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
- **Liberdade**: pode criar formatos novos (hexágonos, escada, quebra-cabeça, colunas,
  raios...), desde que nada fique muito diferente ou inusitado. Formatos ousados só
  quando ela pedir.
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

### 2. Escolha 3 formatos diferentes
Use os critérios abaixo. As três opções devem ser realmente distintas: por exemplo, uma
circular de uma cor, uma colorida e uma com outra estrutura.

| layout | modelo | combina com | tópicos | descrição |
|---|---|---|---|---|
| `arco` | Athena | clássico, logo quadrado/redondo, 1 cor | 5–8 | ótima (texto fora) |
| `anel` | Koala | clássico ou infantil, logo redondo | 4–8 | só curtas |
| `leque` | Criança Feliz | infantil, logo horizontal | 4–6 | só curtas |
| `petalas` | Estela Maris | infantil/colorido, logo compacto | 5–8 | boa (texto fora) |
| `arvore` | Infan Gardeno | infantil, ideia de crescimento, com slogan | 4–8 | só curtas |
| `baloes` | Pistori | qualquer estilo, post com slogan | 5–8 | razoável |
| `orbita` | Koala 2 | clássico, logo horizontal, número par | 4–8 | só curtas |
| `onda` | Sagaz | logo bem horizontal, poucos tópicos | 3–6 | boa (texto fora) |

**Quando nenhum desses servir bem** (por quantidade de tópicos, proporção do logo,
excesso de texto, ou porque um formato novo ficaria claramente melhor), **crie um
layout novo** seguindo "Como criar um layout novo" abaixo. Os layouts novos não são
criados antecipadamente: eles nascem conforme cada imagem pede.

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
- composição desequilibrada.

Corrija e gere de novo. Para quebrar uma linha num ponto específico, use `\n` no texto.
Depois mostre as 3 opções à usuária, com uma linha de justificativa para cada.

### 5. Refine e entregue
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

Python 3 com `cairosvg`, `fonttools` e `Pillow`
(`pip install cairosvg fonttools pillow`). As fontes (Poppins e Fredoka, licença OFL) e
os ícones (Tabler Icons de linha e preenchidos, licença MIT) já vêm em `assets/`.
