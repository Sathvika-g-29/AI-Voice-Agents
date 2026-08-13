'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import { TokenSource } from 'livekit-client';
import { useSession } from '@livekit/components-react';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import type { AppConfig } from '@/app-config';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/ui/sonner';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { useDebugMode } from '@/hooks/useDebug';
import { getSandboxTokenSource } from '@/lib/utils';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });
  useAgentErrors();
  return null;
}

function MicPermissionBanner() {
  return (
    <div className="fixed top-0 left-0 w-full z-50 flex items-start justify-center px-4 pt-4 pointer-events-none">
      <div
        id="mic-permission-banner"
        className="hidden pointer-events-auto max-w-md w-full rounded-xl border border-red-200 bg-red-50 px-4 py-3 shadow-lg"
      >
        <div className="flex items-start gap-3">
          {/* Mic blocked icon */}
          <span className="mt-0.5 text-red-500 text-xl flex-shrink-0">🎙️🚫</span>
          <div>
            <p className="text-sm font-semibold text-red-800">
              Microphone access blocked
            </p>
            <p className="text-xs text-red-600 mt-0.5 leading-relaxed">
              Your learning assistant needs the microphone to hear you. To fix this:
            </p>
            <ol className="text-xs text-red-600 mt-1 ml-3 list-decimal leading-relaxed space-y-0.5">
              <li>Click the 🔒 lock icon in your browser's address bar</li>
              <li>Set <strong>Microphone</strong> to <strong>Allow</strong></li>
              <li>Refresh the page and try again</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const tokenSource = useMemo(() => {
    return typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string'
      ? getSandboxTokenSource(appConfig)
      : TokenSource.endpoint('/api/token');
  }, [appConfig]);

  const session = useSession(
    tokenSource,
    appConfig.agentName ? { agentName: appConfig.agentName } : undefined
  );

  // Show mic permission banner if browser denies microphone access
  if (typeof window !== 'undefined') {
    navigator.permissions
      ?.query({ name: 'microphone' as PermissionName })
      .then((result) => {
        const banner = document.getElementById('mic-permission-banner');
        if (!banner) return;
        if (result.state === 'denied') {
          banner.classList.remove('hidden');
        } else {
          banner.classList.add('hidden');
        }
        result.onchange = () => {
          if (result.state === 'denied') {
            banner.classList.remove('hidden');
          } else {
            banner.classList.add('hidden');
          }
        };
      })
      .catch(() => {
        // Permissions API not supported — silently ignore
      });
  }

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />

      {/* Microphone permission error banner */}
      <MicPermissionBanner />

      <div className="fixed right-4 top-4 z-50 hidden gap-2 md:flex">
        <Link
          href="/call-analytics"
          className="rounded-full border border-fuchsia-400/25 bg-slate-950/80 px-4 py-2 text-xs font-semibold text-fuchsia-100 shadow-lg shadow-fuchsia-950/20 backdrop-blur hover:border-fuchsia-300/40 hover:bg-slate-900"
        >
          Dashboard
        </Link>
        <Link
          href="/help-requests"
          className="rounded-full border border-fuchsia-400/25 bg-slate-950/80 px-4 py-2 text-xs font-semibold text-fuchsia-100 shadow-lg shadow-fuchsia-950/20 backdrop-blur hover:border-fuchsia-300/40 hover:bg-slate-900"
        >
          Human Help
        </Link>
      </div>

      <main className="min-h-svh w-full bg-[radial-gradient(circle_at_top,_rgba(236,72,153,0.22),_transparent_28%),radial-gradient(circle_at_80%_20%,_rgba(168,85,247,0.18),_transparent_24%),linear-gradient(135deg,_#050816_0%,_#090417_45%,_#14081f_100%)]">
        <ViewController appConfig={appConfig} />
      </main>

      <StartAudioButton label="Start Audio" />

      <Toaster
        icons={{
          warning: <WarningIcon weight="bold" />,
        }}
        position="top-center"
        className="toaster group"
        style={
          {
            '--normal-bg': 'var(--popover)',
            '--normal-text': 'var(--popover-foreground)',
            '--normal-border': 'var(--border)',
          } as React.CSSProperties
        }
        toastOptions={{
          classNames: {
            toast:
              'rounded-xl border border-fuchsia-500/20 bg-slate-950/95 text-slate-100 shadow-lg shadow-fuchsia-950/20 text-sm backdrop-blur',
            warning: 'border-amber-500/30 bg-amber-950/80 text-amber-100',
          },
        }}
      />
    </AgentSessionProvider>
  );
}
