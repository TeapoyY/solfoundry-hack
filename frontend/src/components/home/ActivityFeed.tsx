import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { slideInRight } from '../../lib/animations';
import { timeAgo } from '../../lib/utils';

interface ActivityEvent {
  id: string;
  type: 'completed' | 'submitted' | 'posted' | 'review' | 'paid';
  username: string;
  avatar_url?: string | null;
  detail: string;
  timestamp: string;
}

// Mock events for when API doesn't return activity
const MOCK_EVENTS: ActivityEvent[] = [
  {
    id: '1',
    type: 'completed',
    username: 'devbuilder',
    detail: '$500 USDC from Bounty #42',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    type: 'submitted',
    username: 'KodeSage',
    detail: 'PR to Bounty #38',
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
  },
  {
    id: '3',
    type: 'posted',
    username: 'SolanaLabs',
    detail: 'Bounty #145 — $3,500 USDC',
    timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
  },
  {
    id: '4',
    type: 'review',
    username: 'AI Review',
    detail: 'Bounty #42 — 8.5/10',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
];

function getActionText(type: ActivityEvent['type']) {
  switch (type) {
    case 'completed': return 'earned';
    case 'submitted': return 'submitted';
    case 'posted': return 'posted';
    case 'review': return 'AI Review passed for';
    case 'paid': return 'paid out';
    default: return 'updated';
  }
}

function EventItem({ event }: { event: ActivityEvent }) {
  const isMagenta = event.type === 'review';
  return (
    <div className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-forge-850 transition-colors duration-150">
      {event.avatar_url ? (
        <img src={event.avatar_url} className="w-6 h-6 rounded-full flex-shrink-0" alt="" />
      ) : (
        <div className="w-6 h-6 rounded-full bg-forge-700 flex-shrink-0 flex items-center justify-center">
          <span className="font-mono text-xs text-text-muted">{event.username[0]?.toUpperCase()}</span>
        </div>
      )}
      <p className="text-sm text-text-secondary flex-1 truncate">
        <span className="font-medium text-text-primary">{event.username}</span>
        {' '}{getActionText(event.type)}{' '}
        <span className={`font-mono ${isMagenta ? 'text-magenta' : 'text-emerald'}`}>{event.detail}</span>
      </p>
      <span className="font-mono text-xs text-text-muted flex-shrink-0">{timeAgo(event.timestamp)}</span>
    </div>
  );
}

export function ActivityFeed({ events, isLoading }: { events?: ActivityEvent[]; isLoading?: boolean }) {
  // Show real events when available and non-empty.
  // While loading (API not yet responded), show mock data as placeholder.
  // When API returns an empty array, show "No recent activity".
  const isEmpty = !isLoading && events !== undefined && events.length === 0;
  const displayEvents = isEmpty ? [] : ((events && events.length > 0) ? events : MOCK_EVENTS).slice(0, 4);
  const [visibleEvents, setVisibleEvents] = useState<ActivityEvent[]>(displayEvents.slice(0, 4));

  useEffect(() => {
    setVisibleEvents(displayEvents.slice(0, 4));
  }, [events, isLoading]);

  return (
    <section className="w-full border-y border-border bg-forge-900/50 py-4 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center gap-3 mb-3">
          <span className="w-2 h-2 rounded-full bg-emerald animate-pulse-glow" />
          <span className="font-mono text-xs text-text-muted uppercase tracking-wider">Recent Activity</span>
        </div>
        <div className="space-y-1">
          {isEmpty ? (
            <p className="text-sm text-text-muted px-3 py-2">No recent activity</p>
          ) : (
            <AnimatePresence mode="popLayout">
              {visibleEvents.map((event) => (
                <motion.div
                  key={event.id}
                  variants={slideInRight}
                  initial="initial"
                  animate="animate"
                  exit={{ opacity: 0, x: -20, transition: { duration: 0.2 } }}
                  layout
                >
                  <EventItem event={event} />
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </div>
      </div>
    </section>
  );
}
