import { type ComponentProps, type Ref } from 'react';
import { type VariantProps, cva } from 'class-variance-authority';
import { type MotionProps, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';

const motionAnimationProps = {
  variants: {
    hidden: {
      opacity: 0,
      scale: 0.1,
      transition: {
        duration: 0.15,
        ease: 'linear' as const,
      },
    },
    visible: {
      opacity: [0.4, 1],
      scale: [1, 1.25],
      transition: {
        type: 'spring' as const,
        bounce: 0,
        duration: 0.7,
        repeat: Infinity,
        repeatType: 'mirror' as const,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

const agentChatIndicatorVariants = cva(
  'inline-block rounded-full',
  {
    variants: {
      size: {
        sm: 'size-2.5',
        md: 'size-4',
        lg: 'size-6',
      },
      role: {
        // Blue dot — agent is speaking/thinking
        agent: 'bg-blue-500',
        // Green dot — user is being heard
        user: 'bg-emerald-500',
        // Neutral fallback
        default: 'bg-slate-400',
      },
    },
    defaultVariants: {
      size: 'md',
      role: 'agent',
    },
  }
);

export interface AgentChatIndicatorProps extends MotionProps {
  /**
   * The size of the indicator dot.
   * @defaultValue 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Who the indicator represents.
   * 'agent' = blue (speaking/thinking), 'user' = green (listening), 'default' = neutral
   * @defaultValue 'agent'
   */
  role?: 'agent' | 'user' | 'default';

  /**
   * Additional CSS class names.
   */
  className?: string;

  ref?: Ref<HTMLSpanElement>;
}

/**
 * An animated pulsing dot that shows speaking or listening state.
 *
 * Blue = agent is speaking or thinking.
 * Green = agent is listening to the user.
 *
 * @example
 * ```tsx
 * {agentState === 'speaking' && <AgentChatIndicator role="agent" size="md" />}
 * {agentState === 'listening' && <AgentChatIndicator role="user" size="md" />}
 * ```
 */
export function AgentChatIndicator({
  size = 'md',
  role = 'agent',
  className,
  ...props
}: AgentChatIndicatorProps &
  ComponentProps<'span'> &
  VariantProps<typeof agentChatIndicatorVariants>) {
  return (
    <div className="flex items-center gap-2">
      <motion.span
        {...motionAnimationProps}
        className={cn(agentChatIndicatorVariants({ size, role }), className)}
        {...props}
      />
      <span className="text-xs font-medium tracking-wide text-slate-500 select-none">
        {role === 'agent' && 'Assistant is speaking…'}
        {role === 'user' && 'Listening to you…'}
        {role === 'default' && 'Connected'}
      </span>
    </div>
  );
}