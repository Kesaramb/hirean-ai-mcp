import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const FONT =
  "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif";
const ORANGE = '#eb6834';
const BLUE = '#2a78d6';

const resolveSrc = (src: string): string =>
  src.startsWith('http') ? src : staticFile(src);

// Fade the whole overlay out over the last `tailFrames` frames.
const useFadeOut = (tailFrames = 12): number => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  return interpolate(
    frame,
    [durationInFrames - tailFrames, durationInFrames - 1],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
};

const SourceTag: React.FC<{source: string}> = ({source}) => (
  <div
    style={{
      fontFamily: FONT,
      fontSize: 26,
      fontWeight: 600,
      letterSpacing: 0.5,
      color: 'rgba(255,255,255,0.92)',
      background: 'rgba(0,0,0,0.62)',
      borderRadius: 8,
      padding: '10px 22px',
    }}
  >
    {source}
  </div>
);

// ---------------------------------------------------------------- StatCallout

export type StatCalloutProps = {
  value: string;
  label: string;
  source: string;
  align?: 'center' | 'lower';
  durationSec: number;
};

export const StatCallout: React.FC<StatCalloutProps> = ({
  value,
  label,
  source,
  align = 'center',
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeOut = useFadeOut();
  const pop = spring({frame, fps, config: {damping: 13, mass: 0.7}});
  const restIn = interpolate(frame, [8, 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        justifyContent: align === 'center' ? 'center' : 'flex-end',
        alignItems: 'center',
        paddingBottom: align === 'lower' ? 120 : 0,
        opacity: fadeOut,
      }}
    >
      <div style={{transform: `scale(${pop})`}}>
        <div
          style={{
            fontFamily: FONT,
            fontSize: 190,
            fontWeight: 800,
            color: '#fff',
            lineHeight: 1,
            textAlign: 'center',
            textShadow:
              '0 6px 40px rgba(0,0,0,0.85), 0 2px 8px rgba(0,0,0,0.9)',
          }}
        >
          {value}
        </div>
      </div>
      <div
        style={{
          opacity: restIn,
          marginTop: 28,
          maxWidth: 1300,
          textAlign: 'center',
          fontFamily: FONT,
          fontSize: 48,
          fontWeight: 700,
          color: '#fff',
          textShadow: '0 2px 18px rgba(0,0,0,0.9)',
        }}
      >
        {label}
      </div>
      <div style={{opacity: restIn, marginTop: 30}}>
        <SourceTag source={source} />
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- ReceiptCard

export type ReceiptCardProps = {
  imageSrc: string;
  caption: string;
  source: string;
  stamp?: string;
  durationSec: number;
};

export const ReceiptCard: React.FC<ReceiptCardProps> = ({
  imageSrc,
  caption,
  source,
  stamp,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeOut = useFadeOut();
  const rise = spring({frame, fps, config: {damping: 16}});
  const y = interpolate(rise, [0, 1], [120, 0]);
  const stampIn = spring({
    frame: Math.max(0, frame - 18),
    fps,
    config: {damping: 10, mass: 0.6},
  });
  return (
    <AbsoluteFill
      style={{justifyContent: 'center', alignItems: 'center', opacity: fadeOut}}
    >
      <div
        style={{
          transform: `translateY(${y}px) rotate(-1.2deg)`,
          opacity: rise,
          background: '#f7f5ef',
          borderRadius: 14,
          padding: 26,
          boxShadow: '0 30px 90px rgba(0,0,0,0.6)',
          position: 'relative',
          maxWidth: 1250,
        }}
      >
        <Img
          src={resolveSrc(imageSrc)}
          style={{
            maxWidth: 1200,
            maxHeight: 640,
            borderRadius: 6,
            display: 'block',
          }}
        />
        {stamp ? (
          <div
            style={{
              position: 'absolute',
              top: 40,
              right: 48,
              transform: `rotate(-14deg) scale(${stampIn})`,
              border: '6px solid #c81e1e',
              color: '#c81e1e',
              borderRadius: 10,
              padding: '10px 26px',
              fontFamily: FONT,
              fontWeight: 800,
              fontSize: 64,
              letterSpacing: 4,
              textTransform: 'uppercase',
              background: 'rgba(255,255,255,0.82)',
            }}
          >
            {stamp}
          </div>
        ) : null}
        <div
          style={{
            marginTop: 18,
            fontFamily: FONT,
            fontSize: 34,
            fontWeight: 700,
            color: '#191919',
          }}
        >
          {caption}
        </div>
      </div>
      <div style={{marginTop: 26}}>
        <SourceTag source={source} />
      </div>
    </AbsoluteFill>
  );
};

// -------------------------------------------------------------- ColdOpenTitle

export type ColdOpenTitleProps = {
  line1: string;
  line2?: string;
  durationSec: number;
};

export const ColdOpenTitle: React.FC<ColdOpenTitleProps> = ({line1, line2}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeOut = useFadeOut();
  const enter = spring({frame, fps, config: {damping: 200}});
  const y = interpolate(enter, [0, 1], [40, 0]);
  const line2In = interpolate(
    frame,
    [Math.round(fps * 0.6), Math.round(fps * 1.0)],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  return (
    <AbsoluteFill
      style={{justifyContent: 'center', alignItems: 'center', opacity: fadeOut}}
    >
      <div
        style={{
          transform: `translateY(${y}px)`,
          opacity: enter,
          textAlign: 'center',
          maxWidth: 1500,
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            fontSize: 110,
            fontWeight: 800,
            color: '#fff',
            lineHeight: 1.08,
            textShadow:
              '0 6px 44px rgba(0,0,0,0.9), 0 2px 10px rgba(0,0,0,0.85)',
          }}
        >
          {line1}
        </div>
        {line2 ? (
          <div
            style={{
              opacity: line2In,
              marginTop: 26,
              fontFamily: FONT,
              fontSize: 52,
              fontWeight: 600,
              color: 'rgba(255,255,255,0.94)',
              textShadow: '0 2px 20px rgba(0,0,0,0.9)',
            }}
          >
            {line2}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

// ----------------------------------------------------------------- LowerThird

export type LowerThirdProps = {
  name: string;
  role: string;
  durationSec: number;
};

export const LowerThird: React.FC<LowerThirdProps> = ({name, role}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeOut = useFadeOut();
  const slide = spring({frame, fps, config: {damping: 18}});
  const x = interpolate(slide, [0, 1], [-420, 0]);
  return (
    <AbsoluteFill style={{opacity: fadeOut}}>
      <div
        style={{
          position: 'absolute',
          left: 90,
          bottom: 120,
          transform: `translateX(${x}px)`,
          display: 'flex',
          alignItems: 'stretch',
        }}
      >
        <div style={{width: 10, background: ORANGE, borderRadius: 3}} />
        <div
          style={{
            background: 'rgba(0,0,0,0.68)',
            padding: '18px 34px 20px 26px',
            borderRadius: '0 10px 10px 0',
          }}
        >
          <div
            style={{fontFamily: FONT, fontSize: 46, fontWeight: 800, color: '#fff'}}
          >
            {name}
          </div>
          <div
            style={{
              fontFamily: FONT,
              fontSize: 30,
              fontWeight: 500,
              color: 'rgba(255,255,255,0.85)',
              marginTop: 4,
            }}
          >
            {role}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ----------------------------------------------------------- EndScreenHandoff

export type EndScreenHandoffProps = {
  lesson: string;
  nextTitle: string;
  durationSec: number;
};

export const EndScreenHandoff: React.FC<EndScreenHandoffProps> = ({
  lesson,
  nextTitle,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeIn = interpolate(frame, [0, Math.round(fps * 0.5)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const nextIn = spring({
    frame: Math.max(0, frame - Math.round(fps * 0.8)),
    fps,
    config: {damping: 16},
  });
  return (
    <AbsoluteFill style={{opacity: fadeIn}}>
      {/* Left column only — the right side stays clear for YouTube end-screen elements. */}
      <div
        style={{
          position: 'absolute',
          left: 70,
          top: 120,
          bottom: 120,
          width: 760,
          background: 'rgba(0,0,0,0.58)',
          borderRadius: 18,
          padding: '54px 58px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            fontSize: 26,
            fontWeight: 700,
            letterSpacing: 3,
            color: ORANGE,
            textTransform: 'uppercase',
          }}
        >
          The lesson
        </div>
        <div
          style={{
            fontFamily: FONT,
            fontSize: 44,
            fontWeight: 700,
            color: '#fff',
            lineHeight: 1.3,
            marginTop: 14,
          }}
        >
          {lesson}
        </div>
        <div
          style={{height: 2, background: 'rgba(255,255,255,0.25)', margin: '44px 0'}}
        />
        <div
          style={{
            fontFamily: FONT,
            fontSize: 26,
            fontWeight: 700,
            letterSpacing: 3,
            color: BLUE,
            textTransform: 'uppercase',
          }}
        >
          Up next
        </div>
        <div
          style={{
            transform: `scale(${0.9 + 0.1 * nextIn})`,
            transformOrigin: 'left center',
            opacity: nextIn,
            fontFamily: FONT,
            fontSize: 52,
            fontWeight: 800,
            color: '#fff',
            lineHeight: 1.2,
            marginTop: 14,
          }}
        >
          {nextTitle} →
        </div>
      </div>
    </AbsoluteFill>
  );
};
