import React from "react";
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, FONTS, stickerStroke } from "../brand";

// Mesma sequência de cores do título "DICAS" da capa original
const PALETTE = [COLORS.white, COLORS.yellow, COLORS.orange, COLORS.white, COLORS.yellow];

/** Título em letras "adesivo" saltando uma a uma, no estilo da capa. */
export const StickerTitle: React.FC<{
  text: string;
  size: number;
  delay?: number;
}> = ({ text, size, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div
      style={{
        display: "flex",
        fontFamily: FONTS.title,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: size * 0.02,
        filter: `drop-shadow(0 ${size * 0.06}px 0 ${COLORS.outline})`,
      }}
    >
      {text.split("").map((ch, i) => {
        const colorIndex = text.slice(0, i).replace(/ /g, "").length;
        if (ch === " ") {
          return <span key={i} style={{ width: size * 0.3 }} />;
        }
        const s = spring({
          frame: frame - delay - i * 4,
          fps,
          config: { damping: 9, stiffness: 160 },
        });
        return (
          <span
            key={i}
            style={{
              color: PALETTE[colorIndex % PALETTE.length],
              ...stickerStroke(size * 0.16),
              display: "inline-block",
              scale: String(s),
              rotate: `${(i % 2 === 0 ? -1 : 1) * 4}deg`,
            }}
          >
            {ch}
          </span>
        );
      })}
    </div>
  );
};

export const Subtitle: React.FC<{
  text: string;
  size: number;
  delay?: number;
}> = ({ text, size, delay = 0 }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        fontFamily: FONTS.body,
        fontWeight: 600,
        fontSize: size,
        color: COLORS.white,
        textShadow: "0 3px 12px rgba(0,0,0,0.25)",
        opacity: interpolate(frame, [delay, delay + 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
        translate: interpolate(frame, [delay, delay + 18], ["0px 30px", "0px 0px"], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
      }}
    >
      {text}
    </div>
  );
};
