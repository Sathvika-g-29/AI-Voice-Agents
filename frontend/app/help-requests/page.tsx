import { readFile } from 'fs/promises';
import Link from 'next/link';
import path from 'path';

type HumanHelpRequest = {
  request_id: string;
  created_at: string;
  status: string;
  requester_name: string;
  issue: string;
  what_checked: string;
  urgency: string;
  language: string;
  follow_up_method: string;
  summary: string;
};

async function getRequests(): Promise<HumanHelpRequest[]> {
  const exportPath = path.resolve(process.cwd(), '..', 'backend', 'human_help_requests.json');

  try {
    const raw = await readFile(exportPath, 'utf8');
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export default async function HelpRequestsPage() {
  const requests = await getRequests();

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Human Help</p>
          <h1 className="mt-3 text-3xl font-semibold text-white">Open requests</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Requests created by the voice agent when a learner needs a human follow-up.
          </p>
          <Link href="/" className="mt-4 inline-block text-sm text-sky-300 underline-offset-4 hover:underline">
            Back to the voice agent
          </Link>
        </div>

        <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <div className="grid grid-cols-12 gap-3 border-b border-slate-800 px-4 py-3 text-xs uppercase tracking-[0.2em] text-slate-400">
            <div className="col-span-2">ID</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-2">Urgency</div>
            <div className="col-span-2">Requester</div>
            <div className="col-span-4">Summary</div>
          </div>

          {requests.length === 0 ? (
            <div className="px-4 py-10 text-sm text-slate-400">No open requests yet.</div>
          ) : (
            <div className="divide-y divide-slate-800">
              {requests.map((request) => (
                <div key={request.request_id} className="grid grid-cols-12 gap-3 px-4 py-4 text-sm">
                  <div className="col-span-2 font-mono text-xs text-sky-300">
                    {request.request_id}
                  </div>
                  <div className="col-span-2 text-slate-200">{request.status}</div>
                  <div className="col-span-2 text-slate-200">{request.urgency}</div>
                  <div className="col-span-2 text-slate-200">{request.requester_name}</div>
                  <div className="col-span-4 text-slate-300">{request.summary}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
