import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Video } from "@remotion/media";
import type { Caption } from "@remotion/captions";
import { Background } from "../components/Background";
import { Captions } from "../components/Captions";
import { COLORS, FONTS } from "../brand";
import { Img } from "remotion";

// Tamanho do vídeo para preencher a moldura sem faixas pretas (equivale a object-fit: cover)
const coverSize = (sw: number, sh: number, cw: number, ch: number) => {
  const k = Math.max(cw / sw, ch / sh);
  return { width: sw * k, height: sh * k };
};

export type ClipProps = {
  src: string;
  srcWidth: number;
  srcHeight: number;
  trimBefore: number;
  zoom: number;
  label: string | null;
  captions: Caption[];
};

const SpeakerTag: React.FC<{ label: string }> = ({ label }) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [6, 22, 100, 114], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <div
      style={{
        alignSelf: "flex-start",
        background: COLORS.orange,
        color: COLORS.white,
        fontFamily: FONTS.body,
        fontWeight: 700,
        fontSize: 46,
        padding: "12px 34px",
        borderRadius: 999,
        border: `5px solid ${COLORS.white}`,
        boxShadow: "0 8px 20px rgba(0,0,0,0.25)",
        opacity: enter,
        translate: `${(1 - enter) * -80}px 0px`,
      }}
    >
      {label}
    </div>
  );
};

/** Um trecho de depoimento dentro da moldura da identidade. */
export const Clip: React.FC<ClipProps> = ({
  src,
  srcWidth,
  srcHeight,
  trimBefore,
  zoom,
  label,
  captions,
}) => {
  const landscape = srcWidth > srcHeight;
  const card = landscape
    ? { width: 1000, height: 562, top: 560 }
    : { width: 860, height: 1490, top: 230 };

  return (
    <AbsoluteFill>
      <Background hideTopRight />
      <Img
        src={staticFile("brand/logo-capitulo-i.png")}
        style={{ position: "absolute", width: 150, right: 50, top: 40 }}
      />
      <div
        style={{
          position: "absolute",
          left: (1080 - card.width) / 2,
          top: card.top,
          width: card.width,
          height: card.height,
          borderRadius: 44,
          border: `10px solid ${COLORS.white}`,
          overflow: "hidden",
          boxShadow: "0 24px 60px rgba(0,0,0,0.3)",
          background: "#000",
        }}
      >
        <AbsoluteFill
          style={{
            alignItems: "center",
            justifyContent: "center",
            scale: String(zoom),
          }}
        >
          <Video
            src={staticFile(src)}
            trimBefore={trimBefore}
            style={{
              flexShrink: 0,
              ...coverSize(srcWidth, srcHeight, card.width - 20, card.height - 20),
            }}
          />
        </AbsoluteFill>
      </div>
      {label ? (
        <div
          style={{
            position: "absolute",
            left: (1080 - card.width) / 2 - 10,
            top: card.top - 40,
            display: "flex",
          }}
        >
          <SpeakerTag label={label} />
        </div>
      ) : null}
      <Captions
        captions={captions}
        size={landscape ? 66 : 60}
        bottom={landscape ? 470 : 300}
      />
    </AbsoluteFill>
  );
};
