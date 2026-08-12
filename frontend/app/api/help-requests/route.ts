import { readFile } from 'fs/promises';
import { NextResponse } from 'next/server';
import path from 'path';

export const revalidate = 0;

export async function GET() {
  const exportPath = path.resolve(process.cwd(), '..', 'backend', 'human_help_requests.json');

  try {
    const raw = await readFile(exportPath, 'utf8');
    const requests = JSON.parse(raw);
    return NextResponse.json({ requests });
  } catch {
    return NextResponse.json({ requests: [] });
  }
}
