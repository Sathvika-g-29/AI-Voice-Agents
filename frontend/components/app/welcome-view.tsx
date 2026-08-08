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
      {/* Open book shape */}
      <path
        d="M32 12C32 12 18 8 8 14V52C18 46 32 50 32 50C32 50 46 46 56 52V14C46 8 32 12 32 12Z"
        fill="#3B82F6"
        opacity="0.15"
      />
      <path
        d="M32 12V50"
        stroke="#2563EB"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M8 14C18 8 32 12 32 12V50C32 50 18 46 8 52V14Z"
        stroke="#2563EB"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="#DBEAFE"
        opacity="0.6"
      />
      <path
        d="M56 14C46 8 32 12 32 12V50C32 50 46 46 56 52V14Z"
        stroke="#059669"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="#D1FAE5"
        opacity="0.6"
      />
      {/* Sound waves to show voice */}
      <path
        d="M38 28C39.5 29.5 39.5 34.5 38 36"
        stroke="#059669"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M42 25C45 27.5 45 36.5 42 39"
        stroke="#059669"
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
    <div ref={ref} className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 px-4">
      <section className="flex flex-col items-center justify-center text-center max-w-md">

        {/* Badge */}
        <span className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 tracking-wide uppercase">
           Learning Assistant
        </span>

        <WelcomeImage />

        {/* Heading */}
        <h1 className="text-3xl font-bold text-blue-900 tracking-tight mt-2">
          Your Reading & Literacy Buddy
        </h1>

        {/* Subheading */}
        <p className="mt-3 text-base text-slate-500 leading-relaxed max-w-sm">
          Ask questions about books, get help with comprehension, improve your writing — all through conversation.
        </p>

        {/* Start button */}
        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm tracking-wide shadow-md transition-all duration-200 hover:shadow-lg hover:scale-105"
        >
          🎙️ {startButtonText}
        </Button>

        {/* Hint */}
        <p className="mt-4 text-xs text-slate-400">
          Microphone access required · Speak clearly for best results
        </p>
      </section>

      {/* Footer */}
      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-slate-400 text-xs text-center">
          Powered by voice AI · Built for learners aged 15–18
        </p>
      </div>
    </div>
  );
};