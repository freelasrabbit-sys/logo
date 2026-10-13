import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS } from "../brand";

const stroke = {
  fill: "none",
  stroke: "rgba(255,255,255,0.22)",
  strokeWidth: 6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

const Atom: React.FC = () => (
  <g {...stroke}>
    <ellipse cx="0" cy="0" rx="70" ry="26" />
    <ellipse cx="0" cy="0" rx="70" ry="26" transform="rotate(60)" />
    <ellipse cx="0" cy="0" rx="70" ry="26" transform="rotate(-60)" />
    <circle cx="0" cy="0" r="8" fill="rgba(255,255,255,0.22)" />
  </g>
);

const Dna: React.FC = () => (
  <g {...stroke}>
    <path d="M0 0 C 40 30, 80 30, 120 0 S 200 -30, 240 0 S 320 30, 360 0" />
    <path d="M0 0 C 40 -30, 80 -30, 120 0 S 200 30, 240 0 S 320 -30, 360 0" />
    {[30, 60, 90, 150, 180, 210, 270, 300, 330].map((x) => (
      <line key={x} x1={x} y1={-14} x2={x} y2={14} />
    ))}
  </g>
);

const Leaf: React.FC = () => (
  <g {...stroke}>
    <path d="M0 0 C 40 -120, 160 -140, 200 -150 C 190 -60, 120 20, 0 0 Z" />
    <path d="M0 0 C 60 -50, 120 -90, 200 -150" />
  </g>
);

const Pencil: React.FC = () => (
  <g {...stroke}>
    <rect x="0" y="-18" width="200" height="36" rx="4" />
    <path d="M200 -18 L 250 0 L 200 18" />
    <line x1="30" y1="-18" x2="30" y2="18" />
  </g>
);

const Flask: React.FC = () => (
  <g {...stroke}>
    <path d="M-25 -110 L -25 60 A 25 25 0 0 0 25 60 L 25 -110" />
    <line x1="-38" y1="-110" x2="38" y2="-110" />
    <line x1="-25" y1="10" x2="25" y2="10" />
  </g>
);

/** Fundo da identidade: degradê verde, retícula e ícones de ciência em traço. */
export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 600], [0, 30], {
    extrapolateRight: "extend",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(160deg, ${COLORS.greenTop} 0%, #7FA77A 50%, ${COLORS.greenBottom} 100%)`,
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage:
            "radial-gradient(rgba(255,255,255,0.13) 2.2px, transparent 2.6px)",
          backgroundSize: "18px 18px",
          maskImage:
            "radial-gradient(ellipse at 50% 45%, transparent 20%, black 85%)",
        }}
      />
      <svg
        width="1080"
        height="1920"
        viewBox="0 0 1080 1920"
        style={{ position: "absolute", translate: `0px ${-drift % 60}px` }}
      >
        <g transform="translate(250 330) scale(1.2)">
          <Atom />
        </g>
        <g transform="translate(-60 120) rotate(15) scale(1.3)">
          <Leaf />
        </g>
        <g transform="translate(560 140) rotate(-40)">
          <Pencil />
        </g>
        <g transform="translate(60 1150) rotate(-25) scale(1.1)">
          <Dna />
        </g>
        <g transform="translate(980 1230) rotate(20)">
          <Leaf />
        </g>
        <g transform="translate(890 1700) rotate(25) scale(1.2)">
          <Flask />
        </g>
        <g transform="translate(980 900) scale(1.4)">
          <Atom />
        </g>
      </svg>
      {/* Formas laranja nos cantos, como na capa */}
      <div
        style={{
          position: "absolute",
          right: -140,
          top: -150,
          width: 360,
          height: 360,
          borderRadius: "50%",
          border: `70px solid ${COLORS.orangeDeep}`,
          borderLeftColor: "transparent",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: -170,
          bottom: -170,
          width: 380,
          height: 380,
          borderRadius: "50%",
          border: `80px solid ${COLORS.orangeDeep}`,
          borderRightColor: "transparent",
          rotate: "20deg",
        }}
      />
    </AbsoluteFill>
  );
};
