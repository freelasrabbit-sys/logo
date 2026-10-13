import "@fontsource/titan-one/400.css";
import "@fontsource/open-sans/400.css";
import "@fontsource/open-sans/600.css";
import "@fontsource/open-sans/700.css";

// Cores tiradas da capa "Dicas · Volta às Aulas" e do logo Capítulo I
export const COLORS = {
  greenTop: "#5E9479",
  greenBottom: "#B1BF74",
  outline: "#2D5A3D",
  orange: "#F68E31",
  orangeDeep: "#F07210",
  yellow: "#FEE915",
  white: "#FFFFFF",
  navy: "#0F4C8A",
};

export const FONTS = {
  title: "'Titan One', sans-serif",
  body: "'Open Sans', sans-serif",
};

// Contorno grosso estilo "adesivo" usado no título DICAS
export const stickerStroke = (px: number) => ({
  WebkitTextStroke: `${px}px ${COLORS.outline}`,
  paintOrder: "stroke fill" as const,
});

export const FPS = 30;
