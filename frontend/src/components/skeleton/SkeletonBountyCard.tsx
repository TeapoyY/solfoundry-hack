/**
 * Shimmer skeleton component that mimics BountyCard layout.
 * Used during data loading states.
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

export function SkeletonBountyCard() {
  return (
    <div className="rounded-xl border border-border bg-forge-900 p-5 space-y-3">
      {/* Row 1: Repo + Tier badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Skeleton className="w-5 h-5 rounded-full" />
          <Skeleton className="w-24 h-3 rounded" />
        </div>
        <Skeleton className="w-8 h-5 rounded-full" />
      </div>

      {/* Row 2: Title */}
      <div className="space-y-2">
        <Skeleton className="w-full h-4 rounded" />
        <Skeleton className="w-3/4 h-4 rounded" />
      </div>

      {/* Row 3: Language dots */}
      <div className="flex items-center gap-3">
        <Skeleton className="w-16 h-3 rounded" />
        <Skeleton className="w-12 h-3 rounded" />
        <Skeleton className="w-14 h-3 rounded" />
      </div>

      {/* Separator */}
      <div className="border-t border-border/50 pt-3" />

      {/* Row 4: Reward + Meta */}
      <div className="flex items-center justify-between">
        <Skeleton className="w-24 h-6 rounded" />
        <div className="flex items-center gap-3">
          <Skeleton className="w-12 h-3 rounded" />
          <Skeleton className="w-14 h-3 rounded" />
        </div>
      </div>
    </div>
  );
}
