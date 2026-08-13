import { readFile } from 'fs/promises';
import Link from 'next/link';
import path from 'path';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

type CallRecord = {
  call_id: string;
  started_at: string;
  ended_at: string;
  duration_seconds: number;
  status: 'successful' | 'failed' | string;
  channel: string;
  success_reason: string;
  outcome_reason: string;
};

type CallAnalyticsPayload = {
  stats: {
    total_calls: number;
    successful_calls: number;
    failed_calls: number;
  };
  recent_calls: CallRecord[];
};

async function getAnalytics(): Promise<CallAnalyticsPayload> {
  const exportPath = path.resolve(process.cwd(), '..', 'backend', 'call_analytics.json');

  try {
    const raw = await readFile(exportPath, 'utf8');
    return JSON.parse(raw) as CallAnalyticsPayload;
  } catch {
    return {
      stats: {
        total_calls: 0,
        successful_calls: 0,
        failed_calls: 0,
      },
      recent_calls: [],
    };
  }
}

function formatTime(iso: string): string {
  const value = new Date(iso);
  return Number.isNaN(value.getTime()) ? 'Unknown' : value.toLocaleString();
}

function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) {
    return '0s';
  }

  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remaining = Math.round(seconds % 60);
  return `${minutes}m ${remaining}s`;
}

export default async function CallAnalyticsPage() {
  const analytics = await getAnalytics();
  const { stats, recent_calls: recentCalls } = analytics;

  const tiles = [
    { label: 'Total calls', value: stats.total_calls },
    { label: 'Successful calls', value: stats.successful_calls },
    { label: 'Failed calls', value: stats.failed_calls },
  ];

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(236,72,153,0.12),_transparent_26%),radial-gradient(circle_at_80%_20%,_rgba(168,85,247,0.12),_transparent_22%),linear-gradient(135deg,_#050816_0%,_#090417_45%,_#14081f_100%)] px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-200/80">Call Analytics</p>
          <h1 className="mt-3 text-3xl font-semibold text-white">Voice agent performance</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-300">
            Real browser and SIP call outcomes from the local analytics export. No transcripts or
            private caller details are shown here.
          </p>
          <div className="mt-4 flex flex-wrap gap-4 text-sm">
            <Link href="/" className="text-fuchsia-200 underline-offset-4 hover:underline">
              Back to the voice agent
            </Link>
            <Link href="/help-requests" className="text-fuchsia-200 underline-offset-4 hover:underline">
              Human-help requests
            </Link>
          </div>
        </div>

        <section className="grid gap-4 md:grid-cols-3">
          {tiles.map((tile) => (
            <div
              key={tile.label}
              className="border border-fuchsia-500/15 bg-white/5 px-5 py-4 backdrop-blur"
            >
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{tile.label}</p>
              <p className="mt-3 text-4xl font-semibold text-white">{tile.value}</p>
            </div>
          ))}
        </section>

        <section className="mt-8 border border-fuchsia-500/15 bg-white/5 backdrop-blur">
          <div className="border-b border-fuchsia-500/10 px-5 py-4">
            <h2 className="text-lg font-semibold text-white">Recent calls</h2>
            <p className="mt-1 text-sm text-slate-300">
              The latest outcomes are stored locally and refreshed when the backend exports the
              analytics file.
            </p>
          </div>

          {recentCalls.length === 0 ? (
            <div className="px-5 py-10 text-sm text-slate-400">No call records yet.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-fuchsia-500/10 text-left text-sm">
                <thead className="bg-white/5 text-xs uppercase tracking-[0.18em] text-slate-400">
                  <tr>
                    <th className="px-5 py-3 font-medium">Started</th>
                    <th className="px-5 py-3 font-medium">Status</th>
                    <th className="px-5 py-3 font-medium">Channel</th>
                    <th className="px-5 py-3 font-medium">Duration</th>
                    <th className="px-5 py-3 font-medium">Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-fuchsia-500/10">
                  {recentCalls.map((call) => (
                    <tr key={call.call_id}>
                      <td className="px-5 py-4 text-slate-200">{formatTime(call.started_at)}</td>
                      <td className="px-5 py-4">
                        <span
                          className={
                            call.status === 'successful'
                              ? 'inline-flex border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-300'
                              : 'inline-flex border border-rose-500/30 bg-rose-500/10 px-2 py-1 text-xs font-medium text-rose-300'
                          }
                        >
                          {call.status}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-slate-200">{call.channel}</td>
                      <td className="px-5 py-4 text-slate-200">
                        {formatDuration(call.duration_seconds)}
                      </td>
                      <td className="px-5 py-4 text-slate-300">
                        {call.success_reason || call.outcome_reason || 'No outcome recorded'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
