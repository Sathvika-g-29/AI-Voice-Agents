'use client';

import { type ComponentProps } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { type AgentState, type ReceivedMessage } from '@livekit/components-react';
import { AgentChatIndicator } from '@/components/agents-ui/agent-chat-indicator';
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation';
import { Message, MessageContent, MessageResponse } from '@/components/ai-elements/message';

export interface AgentChatTranscriptProps extends ComponentProps<'div'> {
  agentState?: AgentState;
  messages?: ReceivedMessage[];
  className?: string;
}

export function AgentChatTranscript({
  agentState,
  messages = [],
  className,
  ...props
}: AgentChatTranscriptProps) {
  return (
    <Conversation
      className={[
        'rounded-2xl border border-blue-100 bg-white/80 backdrop-blur-sm shadow-sm',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {/* Transcript header */}
      <div className="flex items-center gap-2 border-b border-blue-100 px-4 py-2.5">
        <span className="text-base">📖</span>
        <span className="text-xs font-semibold text-blue-700 tracking-wide uppercase">
          Conversation
        </span>
        {messages.length > 0 && (
          <span className="ml-auto text-xs text-slate-400">
            {messages.length} message{messages.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      <ConversationContent>
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center text-slate-400">
            <span className="text-3xl">💬</span>
            <p className="text-sm">Your conversation will appear here.</p>
            <p className="text-xs text-slate-300">Start speaking to begin!</p>
          </div>
        )}

        {messages.map((receivedMessage) => {
          const { id, timestamp, from, message } = receivedMessage;
          const locale = navigator?.language ?? 'en-US';
          const messageOrigin = from?.isLocal ? 'user' : 'assistant';
          const time = new Date(timestamp);
          const title = time.toLocaleTimeString(locale, { timeStyle: 'short' });

          return (
            <motion.div
              key={id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <Message title={title} from={messageOrigin}>
                {/* Speaker label */}
                <div className="mb-1 flex items-center gap-1.5">
                  <span
                    className={[
                      'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold',
                      messageOrigin === 'assistant'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-emerald-100 text-emerald-700',
                    ].join(' ')}
                  >
                    {messageOrigin === 'assistant' ? '🤖 Assistant' : '🧑 You'}
                    <span className="ml-1 font-normal opacity-60">{title}</span>
                  </span>
                </div>

                <MessageContent>
                  <MessageResponse
                    className={[
                      'rounded-xl px-3 py-2 text-sm leading-relaxed',
                      messageOrigin === 'assistant'
                        ? 'bg-blue-50 text-blue-900'
                        : 'bg-emerald-50 text-emerald-900',
                    ].join(' ')}
                  >
                    {message}
                  </MessageResponse>
                </MessageContent>
              </Message>
            </motion.div>
          );
        })}

        {/* Thinking / listening indicator */}
        <AnimatePresence>
          {agentState === 'thinking' && (
            <motion.div
              key="thinking"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.2 }}
              className="px-2 py-1"
            >
              <AgentChatIndicator size="sm" role="agent" />
            </motion.div>
          )}
          {agentState === 'listening' && (
            <motion.div
              key="listening"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.2 }}
              className="px-2 py-1"
            >
              <AgentChatIndicator size="sm" role="user" />
            </motion.div>
          )}
        </AnimatePresence>
      </ConversationContent>

      <ConversationScrollButton />
    </Conversation>
  );
}