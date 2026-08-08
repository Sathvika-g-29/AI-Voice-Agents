'use client';

import { useState, type ComponentProps } from 'react';
import { type VariantProps } from 'class-variance-authority';
import { PhoneOffIcon } from 'lucide-react';
import { useSessionContext } from '@livekit/components-react';
import { Button, buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/shadcn/utils';

export interface AgentDisconnectButtonProps
  extends ComponentProps<'button'>,
    VariantProps<typeof buttonVariants> {
  icon?: React.ReactNode;
  size?: 'default' | 'sm' | 'lg' | 'icon';
  variant?: 'default' | 'outline' | 'destructive' | 'ghost' | 'link';
  children?: React.ReactNode;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

export function AgentDisconnectButton({
  icon,
  size = 'default',
  variant = 'destructive',
  children,
  onClick,
  className,
  ...props
}: AgentDisconnectButtonProps) {
  const { end } = useSessionContext();
  const [isEnding, setIsEnding] = useState(false);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onClick?.(event);
    if (typeof end === 'function') {
      setIsEnding(true);
      end();
    }
  };

  return (
    <Button
      size={size}
      variant={variant}
      onClick={handleClick}
      disabled={isEnding}
      className={cn(
        // Base overrides — softer red, rounded pill, smooth hover
        'rounded-full border border-red-300 bg-red-50 text-red-600',
        'hover:bg-red-500 hover:text-white hover:border-red-500',
        'active:scale-95 transition-all duration-150 shadow-sm',
        'disabled:opacity-60 disabled:cursor-not-allowed',
        'font-semibold text-sm tracking-wide gap-2',
        className,
      )}
      {...props}
    >
      {/* Icon */}
      <span className="flex items-center justify-center">
        {icon ?? <PhoneOffIcon className="size-4" />}
      </span>

      {/* Label */}
      {isEnding ? (
        <span className={cn(size === 'icon' && 'sr-only')}>
          Ending session…
        </span>
      ) : (
        <span className={cn(size === 'icon' && 'sr-only')}>
          {children ?? 'End Session'}
        </span>
      )}
    </Button>
  );
}