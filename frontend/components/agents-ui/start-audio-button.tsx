import { type ComponentProps } from 'react';
import { Room } from 'livekit-client';
import { useEnsureRoom, useStartAudio } from '@livekit/components-react';
import { Button } from '@/components/ui/button';

export interface StartAudioButtonProps extends ComponentProps<'button'> {
  size?: 'default' | 'sm' | 'lg' | 'icon' | 'icon-sm' | 'icon-lg';
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  room?: Room;
  label: string;
}

export function StartAudioButton({
  size = 'default',
  variant = 'default',
  label,
  room,
  ...props
}: StartAudioButtonProps) {
  const roomEnsured = useEnsureRoom(room);
  const { mergedProps } = useStartAudio({ room: roomEnsured, props });

  const isHidden =
    (mergedProps as React.HTMLAttributes<HTMLButtonElement>).style?.display === 'none';

  if (isHidden) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-md">
      <div className="mx-4 flex max-w-sm flex-col items-center gap-4 rounded-2xl border border-fuchsia-500/20 bg-slate-950/95 px-8 py-7 text-center shadow-2xl shadow-fuchsia-950/25">
        <span className="text-4xl">🔊</span>

        <p className="text-base font-semibold text-white">Audio needs your permission</p>

        <p className="text-sm leading-relaxed text-slate-300">
          Your browser blocked audio playback automatically. Tap the button below to allow your
          learning assistant to speak.
        </p>

        <Button
          size="lg"
          {...props}
          {...mergedProps}
          className="w-full rounded-full border border-fuchsia-400/30 bg-gradient-to-r from-fuchsia-500 to-violet-500 text-sm font-semibold tracking-wide text-white shadow-lg shadow-fuchsia-950/40 transition-all duration-150 hover:scale-105 hover:from-fuchsia-400 hover:to-violet-400 active:scale-95"
        >
          🎙️ {label}
        </Button>

        <p className="text-xs text-slate-500">You only need to do this once per session.</p>
      </div>
    </div>
  );
}
