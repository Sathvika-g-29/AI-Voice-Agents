import { Button } from '@/components/ui/button';

function WelcomeImage() {
  return (
    <svg
      width="72"
      height="72"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-5"
    >
      <path
        d="M32 12C32 12 18 8 8 14V52C18 46 32 50 32 50C32 50 46 46 56 52V14C46 8 32 12 32 12Z"
        fill="#A855F7"
        opacity="0.18"
      />
      <path
        d="M32 12V50"
        stroke="#F472B6"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M8 14C18 8 32 12 32 12V50C32 50 18 46 8 52V14Z"
        stroke="#A855F7"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="#1E1634"
        opacity="0.88"
      />
      <path
        d="M56 14C46 8 32 12 32 12V50C32 50 46 46 56 52V14Z"
        stroke="#F472B6"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="#24112A"
        opacity="0.88"
      />
      <path
        d="M38 28C39.5 29.5 39.5 34.5 38 36"
        stroke="#F472B6"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M42 25C45 27.5 45 36.5 42 39"
        stroke="#C084FC"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="min-h-screen w-full flex flex-col items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(236,72,153,0.15),_transparent_28%),radial-gradient(circle_at_70%_20%,_rgba(168,85,247,0.15),_transparent_22%),linear-gradient(135deg,_#050816_0%,_#090417_45%,_#14081f_100%)] px-4"
    >
      <section className="flex max-w-md flex-col items-center justify-center text-center">
        <span className="mb-4 inline-flex items-center gap-1.5 rounded-full border border-fuchsia-500/20 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-fuchsia-100 backdrop-blur">
          Learning Assistant
        </span>

        <WelcomeImage />

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white">
          Your Reading & Literacy Buddy
        </h1>

        <p className="mt-3 max-w-sm text-base leading-relaxed text-slate-300">
          Ask questions about books, get help with comprehension, improve your writing, all through
          conversation.
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 rounded-full border border-fuchsia-400/30 bg-gradient-to-r from-fuchsia-500 to-violet-500 text-sm font-semibold tracking-wide text-white shadow-lg shadow-fuchsia-950/40 transition-all duration-200 hover:scale-105 hover:from-fuchsia-400 hover:to-violet-400"
        >
          🎙️ {startButtonText}
        </Button>

        <p className="mt-4 text-xs text-slate-400">Microphone access required · Speak clearly for best results</p>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-center text-xs text-slate-500">
          Powered by voice AI · Built for learners aged 15-18
        </p>
      </div>
    </div>
  );
};
