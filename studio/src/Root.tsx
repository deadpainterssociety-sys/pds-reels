import React from "react";
import { Composition } from "remotion";
import { Reel } from "./reel/Reel";
import { Long } from "./long/Long";
import { STORIES } from "./reel/stories";

/** one composition per built story: "reel-<slug>" (1080x1920, 30 fps) or, for "format": "long" stories, "long-<slug>" (1920x1080, 24 fps) */
export const Root: React.FC = () => (
  <>
    {Object.keys(STORIES).map((slug) => STORIES[slug].format === "long"
      ? <Composition key={slug} id={`long-${slug}`} component={Long as any} defaultProps={{ slug }} fps={24} width={1920} height={1080}
          durationInFrames={Math.ceil(STORIES[slug].duration * 24)} />
      : <Composition key={slug} id={`reel-${slug}`} component={Reel as any} defaultProps={{ slug }} fps={30} width={1080} height={1920}
          durationInFrames={Math.ceil(STORIES[slug].duration * 30)} />
    )}
  </>
);
