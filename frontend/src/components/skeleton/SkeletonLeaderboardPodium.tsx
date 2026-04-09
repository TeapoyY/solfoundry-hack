/**
 * Shimmer skeleton components that mimic PodiumCards and LeaderboardTable layouts.
 */

interface SkeletonProps {
  className?: string;
}

function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`rounded-lg bg-gradient-to-r from-forge-900 via-forge-800 to-forge-900 bg-[length:200%_100%] animate-shimmer ${className}`}
    />
  );
}

/** Skeleton for the #1 podium card (gold – tallest) */
export function SkeletonPodiumGold() {
  return (
    <div className="relative flex flex-col items-center rounded-xl border border-yellow-500/30 bg-forge-900 py-8 px-6 min-w-[140px]">
      {/* Crown placeholder */}
      <Skeleton className="w-6 h-6 rounded mb-2" />
      {/* Rank */}
      <Skeleton className="w-6 h-4 rounded mb-3" />
      {/* Avatar */}
      <Skeleton className="w-14 h-14 rounded-full" />
      {/* Username */}
      <Skeleton className="w-20 h-4 rounded mt-3" />
      {/* Bounties label */}
      <Skeleton className="w-16 h-3 rounded mt-2" />
      {/* Earnings */}
      <Skeleton className="w-16 h-6 rounded mt-2" />
    </div>
  );
}

/** Skeleton for #2/#3 podium cards */
export function SkeletonPodiumSilverBronze() {
  return (
    <div className="relative flex flex-col items-center rounded-xl border border-zinc-400/30 bg-forge-900 py-6 px-6 min-w-[140px]">
      {/* Rank */}
      <Skeleton className="w-6 h-4 rounded mb-2" />
      {/* Avatar */}
      <Skeleton className="w-12 h-12 rounded-full" />
      {/* Username */}
      <Skeleton className="w-16 h-4 rounded mt-2" />
      {/* Bounties label */}
      <Skeleton className="w-14 h-3 rounded mt-1" />
      {/* Earnings */}
      <Skeleton className="w-14 h-5 rounded mt-1" />
    </div>
  );
}

/** Full podium skeleton loading state */
export function SkeletonPodiumCards() {
  return (
    <div className="flex items-end justify-center gap-4 md:gap-6">
      <SkeletonPodiumSilverBronze />
      <SkeletonPodiumGold />
      <SkeletonPodiumSilverBronze />
    </div>
  );
}

/** Skeleton for a single leaderboard table row */
export function SkeletonLeaderboardRow() {
  return (
    <div className="flex items-center px-4 py-3 border-b border-border/30">
      {/* Rank */}
      <div className="w-[60px] flex justify-center">
        <Skeleton className="w-6 h-4 rounded" />
      </div>
      {/* User */}
      <div className="flex-1 flex items-center gap-3 min-w-0">
        <Skeleton className="w-6 h-6 rounded-full flex-shrink-0" />
        <div className="min-w-0 flex-1">
          <Skeleton className="w-24 h-4 rounded mb-1" />
          <div className="flex items-center gap-1">
            <Skeleton className="w-2.5 h-2.5 rounded-full" />
            <Skeleton className="w-2.5 h-2.5 rounded-full" />
            <Skeleton className="w-2.5 h-2.5 rounded-full" />
          </div>
        </div>
      </div>
      {/* Bounties */}
      <div className="w-[100px] flex justify-center">
        <Skeleton className="w-8 h-4 rounded" />
      </div>
      {/* Earned */}
      <div className="w-[120px] flex justify-end">
        <Skeleton className="w-14 h-4 rounded" />
      </div>
      {/* Streak */}
      <div className="w-[80px] hidden sm:flex justify-center">
        <Skeleton className="w-8 h-4 rounded" />
      </div>
    </div>
  );
}

/** Table header skeleton */
export function SkeletonLeaderboardTable() {
  return (
    <div className="max-w-4xl mx-auto mt-6 rounded-xl border border-border bg-forge-900 overflow-hidden">
      {/* Header row */}
      <div className="flex items-center px-4 py-3 border-b border-border/50">
        <div className="w-[60px] flex justify-center">
          <Skeleton className="w-6 h-3 rounded" />
        </div>
        <div className="flex-1">
          <Skeleton className="w-8 h-3 rounded" />
        </div>
        <div className="w-[100px] flex justify-center">
          <Skeleton className="w-10 h-3 rounded" />
        </div>
        <div className="w-[120px] flex justify-end">
          <Skeleton className="w-10 h-3 rounded" />
        </div>
        <div className="w-[80px] hidden sm:flex justify-center">
          <Skeleton className="w-8 h-3 rounded" />
        </div>
      </div>
      {/* Rows */}
      {Array.from({ length: 5 }).map((_, i) => (
        <SkeletonLeaderboardRow key={i} />
      ))}
    </div>
  );
}
