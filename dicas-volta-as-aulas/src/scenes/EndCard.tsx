import React from "react";
import { AbsoluteFill } from "remotion";
import { Background } from "../components/Background";
import { Logo } from "../components/Logo";
import { StickerTitle, Subtitle } from "../components/Title";

/** Encerramento com o logo da instituição. */
export const EndCard: React.FC<{ title: string; message: string }> = ({
  title,
  message,
}) => {
  return (
    <AbsoluteFill>
      <Background />
      <AbsoluteFill
        style={{ alignItems: "center", justifyContent: "center", gap: 70 }}
      >
        <Logo width={560} delay={2} />
        <Subtitle text={message} size={78} delay={16} />
        <div style={{ scale: "0.55" }}>
          <StickerTitle text={title} size={150} delay={24} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
