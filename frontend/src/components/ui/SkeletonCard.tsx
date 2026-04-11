import React from 'react';

/** Shimmer base - apply animate-shimmer to a child div */
function SkeletonLine({ className = '' }: { className?: string }) {
  return (
    <div
      className={`rounded bg-forge-700/60 overflow-hidden ${className}`}
    >
      <div
        className="h-full bg-gradient-to-r from-transparent via-forge-600/30 to-transparent bg-[length:200%_100%] animate-shimmer"
        style={{ width: '100%' }}
      />
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-forge-900 p-5 overflow-hidden">
      {/* Row 1: Repo + Tier */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SkeletonLine className="w-5 h-5 rounded-full" />
          <SkeletonLine className="w-24 h-3" />
        </div>
        <SkeletonLine className="w-10 h-5 rounded-full" />
      </div>

      {/* Row 2: Title */}
      <div className="mt-3 space-y-2">
        <SkeletonLine className="w-full h-4" />
        <SkeletonLine className="w-3/4 h-4" />
      </div>

      {/* Row 3: Language dots */}
      <div className="flex items-center gap-3 mt-3">
        <SkeletonLine className="w-16 h-3 rounded" />
        <SkeletonLine className="w-12 h-3 rounded" />
        <SkeletonLine className="w-14 h-3 rounded" />
      </div>

      {/* Separator */}
      <div className="mt-4 border-t border-border/50" />

      {/* Row 4: Reward + Meta */}
      <div className="flex items-center justify-between mt-3">
        <SkeletonLine className="w-24 h-6 rounded" />
        <div className="flex items-center gap-3">
          <SkeletonLine className="w-12 h-3 rounded" />
          <SkeletonLine className="w-14 h-3 rounded" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonLeaderboardRow() {
  return (
    <div className="flex items-center gap-4 px-4 py-3 border-b border-border/50">
      <SkeletonLine className="w-6 h-4 rounded" />
      <SkeletonLine className="w-8 h-8 rounded-full" />
      <div className="flex-1 space-y-1">
        <SkeletonLine className="w-32 h-3" />
      </div>
      <SkeletonLine className="w-16 h-3 rounded" />
      <SkeletonLine className="w-12 h-3 rounded" />
    </div>
  );
}

export function SkeletonBountyDetail() {
  return (
    <div className="space-y-6">
      {/* Title + meta */}
      <div className="rounded-xl border border-border bg-forge-900 p-6 space-y-4">
        <div className="flex items-center gap-2">
          <SkeletonLine className="w-5 h-5 rounded-full" />
          <SkeletonLine className="w-32 h-3" />
        </div>
        <SkeletonLine className="w-full h-7" />
        <SkeletonLine className="w-2/3 h-7" />
        <div className="flex gap-3">
          <SkeletonLine className="w-16 h-3 rounded" />
          <SkeletonLine className="w-14 h-3 rounded" />
          <SkeletonLine className="w-20 h-3 rounded" />
        </div>
        <div className="space-y-2">
          <SkeletonLine className="w-full h-3" />
          <SkeletonLine className="w-full h-3" />
          <SkeletonLine className="w-3/4 h-3" />
        </div>
      </div>

      {/* Requirements */}
      <div className="rounded-xl border border-border bg-forge-900 p-6 space-y-3">
        <SkeletonLine className="w-32 h-5" />
        <SkeletonLine className="w-full h-3" />
        <SkeletonLine className="w-5/6 h-3" />
      </div>
    </div>
  );
}

export function SkeletonLeaderboard() {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-border bg-forge-900 overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-4 px-4 py-3 border-b border-border/50 bg-forge-850">
          <SkeletonLine className="w-6 h-3" />
          <SkeletonLine className="w-8 h-8 rounded-full" />
          <SkeletonLine className="flex-1 w-32 h-3" />
          <SkeletonLine className="w-16 h-3" />
          <SkeletonLine className="w-12 h-3" />
        </div>
        {/* Rows */}
        {Array.from({ length: 8 }).map((_, i) => (
          <SkeletonLeaderboardRow key={i} />
        ))}
      </div>
    </div>
  );
}

export function SkeletonProfile() {
  return (
    <div className="space-y-6">
      {/* Profile header */}
      <div className="rounded-xl border border-border bg-forge-900 p-6">
        <div className="flex items-center gap-4">
          <SkeletonLine className="w-16 h-16 rounded-full" />
          <div className="flex-1 space-y-2">
            <SkeletonLine className="w-40 h-5" />
            <SkeletonLine className="w-24 h-3" />
          </div>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="rounded-lg bg-forge-800 p-3 space-y-1">
            <SkeletonLine className="w-12 h-3" />
            <SkeletonLine className="w-16 h-6" />
          </div>
          <div className="rounded-lg bg-forge-800 p-3 space-y-1">
            <SkeletonLine className="w-12 h-3" />
            <SkeletonLine className="w-16 h-6" />
          </div>
          <div className="rounded-lg bg-forge-800 p-3 space-y-1">
            <SkeletonLine className="w-12 h-3" />
            <SkeletonLine className="w-16 h-6" />
          </div>
        </div>
      </div>
    </div>
  );
}
