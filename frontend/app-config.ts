export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorDark?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerBarCount?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerWaveLineWidth?: number;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  // ── Branding ────────────────────────────────────────────────────────
  companyName: 'LitBot',
  pageTitle: 'LitBot — Your Reading & Literacy Assistant',
  pageDescription:
    'A voice-powered learning assistant for teens. Ask questions, explore books, and improve your literacy — all through conversation.',

  // ── Features ────────────────────────────────────────────────────────
  // Chat input on: teens may prefer typing a question sometimes
  supportsChatInput: true,
  // Video and screen share off: not needed for a literacy/reading assistant
  supportsVideoInput: false,
  supportsScreenShare: false,
  // Pre-connect buffer on: reduces perceived latency on first response
  isPreConnectBufferEnabled: true,

  // ── Assets ──────────────────────────────────────────────────────────
  logo: '/murf-logo.svg',
  logoDark: '/murf-logo-dark.svg',

  // Blue accent — calm, focused, matches the blue-green palette
  accent: '#C084FC',
  accentDark: '#F472B6',

  // ── UI copy ─────────────────────────────────────────────────────────
  startButtonText: 'Start Learning',

  // ── Audio visualizer ────────────────────────────────────────────────
  // Wave style feels natural for a voice/speech context
  audioVisualizerType: 'wave',
  audioVisualizerColor: '#C084FC',
  audioVisualizerColorDark: '#F472B6',
  audioVisualizerColorShift: 0.25,
  audioVisualizerWaveLineWidth: 2.5,

  // ── Agent dispatch ───────────────────────────────────────────────────
  agentName: process.env.AGENT_NAME ?? undefined,

  // ── LiveKit Cloud Sandbox ────────────────────────────────────────────
  sandboxId: undefined,
};
