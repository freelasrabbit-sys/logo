import React, { useMemo } from "react";
import {
  AbsoluteFill,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { createTikTokStyleCaptions } from "@remotion/captions";
import type { Caption, TikTokPage } from "@remotion/captions";
import { COLORS, FONTS, stickerStroke } from "../brand";

const SWITCH_CAPTIONS_EVERY_MS = 1100;

const CaptionPage: React.FC<{ page: TikTokPage; size: number }> = ({
  page,
  size,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const absoluteTimeMs = page.startMs + (frame / fps) * 1000;
  const pop = spring({ frame, fps, config: { damping: 14, stiffness: 220 } });

  return (
    <div
      style={{
        fontFamily: FONTS.body,
        fontWeight: 800,
        fontSize: size,
        lineHeight: 1.15,
        textAlign: "center",
        whiteSpace: "pre-wrap",
        maxWidth: "88%",
        scale: String(0.85 + 0.15 * pop),
        filter: "drop-shadow(0 4px 6px rgba(0,0,0,0.35))",
      }}
    >
      {page.tokens.map((token, i) => {
        const isActive =
          token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;
        return (
          <span
            key={`${token.fromMs}-${i}`}
            style={{
              color: isActive ? COLORS.yellow : COLORS.white,
              ...stickerStroke(size * 0.16),
            }}
          >
            {token.text}
          </span>
        );
      })}
    </div>
  );
};

/** Legendas estilo Reels, palavra ativa em amarelo. Tempos relativos ao trecho. */
export const Captions: React.FC<{
  captions: Caption[];
  size: number;
  bottom: number;
}> = ({ captions, size, bottom }) => {
  const { fps } = useVideoConfig();
  const { pages } = useMemo(
    () =>
      createTikTokStyleCaptions({
        captions,
        combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
      }),
    [captions],
  );

  return (
    <AbsoluteFill>
      {pages.map((page, index) => {
        const nextPage = pages[index + 1] ?? null;
        const startFrame = Math.round((page.startMs / 1000) * fps);
        const endFrame = Math.round(
          nextPage
            ? (nextPage.startMs / 1000) * fps
            : ((page.startMs + page.durationMs) / 1000) * fps + fps * 0.4,
        );
        const durationInFrames = endFrame - startFrame;
        if (durationInFrames <= 0) {
          return null;
        }
        return (
          <Sequence
            key={index}
            from={startFrame}
            durationInFrames={durationInFrames}
            layout="none"
          >
            <AbsoluteFill
              style={{
                justifyContent: "flex-end",
                alignItems: "center",
                paddingBottom: bottom,
              }}
            >
              <CaptionPage page={page} size={size} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
