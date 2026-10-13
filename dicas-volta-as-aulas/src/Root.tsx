import { Composition } from "remotion";
import { Cover } from "./scenes/Cover";
import { EndCard } from "./scenes/EndCard";
import { EDL, Main, totalDuration } from "./Main";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Video30Anos"
        component={Main}
        durationInFrames={totalDuration(EDL)}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="Capa"
        component={Cover}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ title: "30 ANOS", subtitle: "Escola Capítulo I" }}
      />
      <Composition
        id="Encerramento"
        component={EndCard}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ title: "30 ANOS", message: "Você pode confiar!" }}
      />
    </>
  );
};
