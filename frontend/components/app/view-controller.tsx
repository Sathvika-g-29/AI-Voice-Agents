'use client';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionView_01 } from '@/components/agents-ui/blocks/agent-session-view-01';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(AgentSessionView_01);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      y: 0,
    },
    hidden: {
      opacity: 0,
      y: 16,
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.4,
    ease: 'easeOut',
  },
};

interface ViewControllerProps {
  appConfig: AppConfig;
}

export function ViewController({ appConfig }: ViewControllerProps) {
  const { isConnected, start, connectionState } = useSessionContext();
  const { resolvedTheme } = useTheme();

  const isConnecting = connectionState === 'connecting';

  return (
    <div className="relative min-h-screen w-full bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      <AnimatePresence mode="wait">

        {/* Welcome view — Ready state */}
        {!isConnected && !isConnecting && (
          <MotionWelcomeView
            key="welcome"
            {...VIEW_MOTION_PROPS}
            startButtonText={appConfig.startButtonText}
            onStartCall={start}
          />
        )}

        {/* Connecting state */}
        {isConnecting && (
          <motion.div
            key="connecting"
            {...VIEW_MOTION_PROPS}
            className="min-h-screen w-full flex flex-col items-center justify-center gap-5 text-center px-4"
          >
            {/* Animated dots */}
            <div className="flex gap-2 items-center">
              {[0, 1, 2].map((i) => (
                <motion.span
                  key={i}
                  className="w-3 h-3 rounded-full bg-blue-500"
                  animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.2,
                    ease: 'easeInOut',
                  }}
                />
              ))}
            </div>
            <p className="text-blue-800 font-semibold text-lg">
              Connecting to your learning assistant…
            </p>
            <p className="text-slate-400 text-sm">
              Please wait a moment
            </p>
          </motion.div>
        )}

        {/* Session view — Listening / Speaking states */}
        {isConnected && (
          <MotionSessionView
            key="session-view"
            {...VIEW_MOTION_PROPS}
            supportsChatInput={appConfig.supportsChatInput}
            supportsVideoInput={appConfig.supportsVideoInput}
            supportsScreenShare={appConfig.supportsScreenShare}
            isPreConnectBufferEnabled={appConfig.isPreConnectBufferEnabled}
            audioVisualizerType={appConfig.audioVisualizerType}
            audioVisualizerColor={
              resolvedTheme === 'dark'
                ? appConfig.audioVisualizerColorDark
                : appConfig.audioVisualizerColor
            }
            audioVisualizerColorShift={appConfig.audioVisualizerColorShift}
            audioVisualizerBarCount={appConfig.audioVisualizerBarCount}
            audioVisualizerGridRowCount={appConfig.audioVisualizerGridRowCount}
            audioVisualizerGridColumnCount={appConfig.audioVisualizerGridColumnCount}
            audioVisualizerRadialBarCount={appConfig.audioVisualizerRadialBarCount}
            audioVisualizerRadialRadius={appConfig.audioVisualizerRadialRadius}
            audioVisualizerWaveLineWidth={appConfig.audioVisualizerWaveLineWidth}
            className="fixed inset-0 bg-gradient-to-br from-blue-50 via-white to-emerald-50"
          />
        )}

      </AnimatePresence>
    </div>
  );
}