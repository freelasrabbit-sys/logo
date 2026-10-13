import React from "react";
import { AbsoluteFill } from "remotion";
import { Background } from "../components/Background";
import { Logo } from "../components/Logo";
import { StickerTitle, Subtitle } from "../components/Title";

/** Capa animada no estilo da arte "Dicas · Volta às Aulas" da instituição. */
export const Cover: React.FC<{ title: string; subtitle: string }> = ({
  title,
  subtitle,
}) => {
  return (
    <AbsoluteFill>
      <Background />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          gap: 30,
          paddingBottom: 260,
        }}
      >
        <StickerTitle text={title} size={210} delay={4} />
        <Subtitle text={subtitle} size={84} delay={30} />
      </AbsoluteFill>
      <AbsoluteFill
        style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 230 }}
      >
        <Logo width={330} delay={36} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
