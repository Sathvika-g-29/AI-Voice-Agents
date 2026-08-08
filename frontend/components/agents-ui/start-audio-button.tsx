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

  // useStartAudio sets mergedProps.style.display = 'none' when audio is already running.
  // We only render when the button is actually needed.
  const isHidden =
    (mergedProps as React.HTMLAttributes<HTMLButtonElement>).style?.display === 'none';

  if (isHidden) return null;

  return (
    // Fixed overlay so it always appears above the session view
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-blue-950/40 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4 rounded-2xl border border-blue-100 bg-white px-8 py-7 shadow-xl text-center max-w-sm mx-4">
        {/* Icon */}
        <span className="text-4xl">🔊</span>

        {/* Heading */}
        <p className="text-base font-semibold text-blue-900">
          Audio needs your permission
        </p>

        {/* Explanation */}
        <p className="text-sm text-slate-500 leading-relaxed">
          Your browser blocked audio playback automatically. Tap the button
          below to allow your learning assistant to speak.
        </p>

        {/* The actual start-audio button */}
        <Button
          size="lg"
          {...props}
          {...mergedProps}
          className="w-full rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm tracking-wide shadow-md transition-all duration-150 hover:scale-105 active:scale-95"
        >
          🎙️ {label}
        </Button>

        <p className="text-xs text-slate-400">
          You only need to do this once per session.
        </p>
      </div>
    </div>
  );
}