import React from "react";
import { Composition } from "remotion";
import { Reel } from "./reel/Reel";
import { STORIES } from "./reel/stories";

/** one composition per built story: id "reel-<slug>", 1080x1920 @ 30 fps, as long as the narration */
export const Root: React.FC = () => (
  <>
    {Object.keys(STORIES).map((slug) => (
      <Composition key={slug} id={`reel-${slug}`} component={Reel as any} defaultProps={{ slug }} fps={30} width={1080} height={1920}
        durationInFrames={Math.ceil(STORIES[slug].duration * 30)} />
    ))}
  </>
);
