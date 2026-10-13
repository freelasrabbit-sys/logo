import React from "react";
import { Img, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

/** Logo Capítulo I (adesivo com borda branca), com entrada em mola. */
export const Logo: React.FC<{ width: number; delay?: number }> = ({
  width,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 12 } });
  return (
    <Img
      src={staticFile("brand/logo-capitulo-i.png")}
      style={{
        width,
        scale: String(s),
        rotate: `${(1 - s) * -12}deg`,
        filter: "drop-shadow(0 10px 24px rgba(0,0,0,0.25))",
      }}
    />
  );
};
