import React from 'react';
import {Composition} from 'remotion';
import type {CalculateMetadataFunction} from 'remotion';
import {
  ColdOpenTitle,
  ColdOpenTitleProps,
  EndScreenHandoff,
  EndScreenHandoffProps,
  LowerThird,
  LowerThirdProps,
  ReceiptCard,
  ReceiptCardProps,
  StatCallout,
  StatCalloutProps,
} from './overlays';

// Match the CapCut draft. AU/PAL broadcast footage is often 25fps — change to 25 if so.
export const FPS = 30;
const W = 1920;
const H = 1080;

function durationFromProps<T extends {durationSec: number}>(): CalculateMetadataFunction<T> {
  return ({props}) => ({
    durationInFrames: Math.max(1, Math.round(props.durationSec * FPS)),
  });
}

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ColdOpenTitle"
        component={ColdOpenTitle}
        width={W}
        height={H}
        fps={FPS}
        durationInFrames={6 * FPS}
        defaultProps={
          {
            line1: 'This handshake was worth $2.5 million.',
            line2: 'Almost none of it was ever paid.',
            durationSec: 6,
          } satisfies ColdOpenTitleProps
        }
        calculateMetadata={durationFromProps<ColdOpenTitleProps>()}
      />
      <Composition
        id="StatCallout"
        component={StatCallout}
        width={W}
        height={H}
        fps={FPS}
        durationInFrames={5 * FPS}
        defaultProps={
          {
            value: '$2.5M',
            label: 'The biggest deal in Australian Shark Tank history',
            source: 'Source: Network Ten broadcast, 2017',
            align: 'center',
            durationSec: 5,
          } satisfies StatCalloutProps
        }
        calculateMetadata={durationFromProps<StatCalloutProps>()}
      />
      <Composition
        id="ReceiptCard"
        component={ReceiptCard}
        width={W}
        height={H}
        fps={FPS}
        durationInFrames={6 * FPS}
        defaultProps={
          {
            imageSrc: 'receipts/sample-filing.png',
            caption: 'Liquidation filing — iCapsulate Pty Ltd',
            source: 'Source: ASIC published notice',
            stamp: 'IN LIQUIDATION',
            durationSec: 6,
          } satisfies ReceiptCardProps
        }
        calculateMetadata={durationFromProps<ReceiptCardProps>()}
      />
      <Composition
        id="LowerThird"
        component={LowerThird}
        width={W}
        height={H}
        fps={FPS}
        durationInFrames={5 * FPS}
        defaultProps={
          {
            name: 'Kane Bodiam',
            role: 'Founder, iCapsulate',
            durationSec: 5,
          } satisfies LowerThirdProps
        }
        calculateMetadata={durationFromProps<LowerThirdProps>()}
      />
      <Composition
        id="EndScreenHandoff"
        component={EndScreenHandoff}
        width={W}
        height={H}
        fps={FPS}
        durationInFrames={20 * FPS}
        defaultProps={
          {
            lesson:
              'A deal on TV is an offer, not a wire transfer — about half quietly die in diligence.',
            nextTitle: 'Five Sharks Said Yes. The Deal Died Anyway.',
            durationSec: 20,
          } satisfies EndScreenHandoffProps
        }
        calculateMetadata={durationFromProps<EndScreenHandoffProps>()}
      />
    </>
  );
};
