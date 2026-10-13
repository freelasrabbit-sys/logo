import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import type { Caption } from "@remotion/captions";
import { Cover } from "./scenes/Cover";
import { EndCard } from "./scenes/EndCard";
import { Clip } from "./scenes/Clip";
import edl from "./data/edl.json";

export type Segment = {
  src: string;
  srcWidth: number;
  srcHeight: number;
  trimBefore: number;
  durationInFrames: number;
  zoom: number;
  label: string | null;
  // true quando o trecho começa um novo depoimento (deslize em vez de esmaecer)
  newSpeaker: boolean;
  captions: Caption[];
};

export type Edl = {
  cover: { title: string; subtitle: string; durationInFrames: number };
  end: { title: string; message: string; durationInFrames: number };
  transitionFrames: number;
  segments: Segment[];
};

export const EDL = edl as Edl;

export const totalDuration = (e: Edl) => {
  const transitions = e.segments.length + 1;
  return (
    e.cover.durationInFrames +
    e.end.durationInFrames +
    e.segments.reduce((a, s) => a + s.durationInFrames, 0) -
    transitions * e.transitionFrames
  );
};

/**
 * Vídeo completo: capa → depoimentos (lista de cortes em data/edl.json) → encerramento.
 * Para mudar um corte, edite trimBefore/durationInFrames no edl.json.
 */
export const Main: React.FC = () => {
  const t = linearTiming({ durationInFrames: EDL.transitionFrames });
  return (
    <AbsoluteFill style={{ backgroundColor: "#5E9479" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="Capa"
          durationInFrames={EDL.cover.durationInFrames}
        >
          <Cover title={EDL.cover.title} subtitle={EDL.cover.subtitle} />
        </TransitionSeries.Sequence>
        {EDL.segments.flatMap((seg, i) => [
          // Todo corte esmaece; troca de depoimento desliza
          <TransitionSeries.Transition
            key={`t${i}`}
            presentation={
              seg.newSpeaker && i > 0 ? slide({ direction: "from-right" }) : fade()
            }
            timing={t}
          />,
          <TransitionSeries.Sequence
            key={`s${i}`}
            name={`${seg.label ?? seg.src} #${i + 1}`}
            durationInFrames={seg.durationInFrames}
          >
            <Clip
              src={seg.src}
              srcWidth={seg.srcWidth}
              srcHeight={seg.srcHeight}
              trimBefore={seg.trimBefore}
              durationInFrames={seg.durationInFrames}
              zoom={seg.zoom}
              label={seg.newSpeaker ? seg.label : null}
              captions={seg.captions}
            />
          </TransitionSeries.Sequence>,
        ])}
        <TransitionSeries.Transition presentation={fade()} timing={t} />
        <TransitionSeries.Sequence
          name="Encerramento"
          durationInFrames={EDL.end.durationInFrames}
        >
          <EndCard title={EDL.end.title} message={EDL.end.message} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
