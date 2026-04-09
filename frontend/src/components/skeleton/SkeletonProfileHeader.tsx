/**
 * Shimmer skeleton components for ProfileDashboard layout.
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

/** Skeleton for the profile header card */
export function SkeletonProfileHeader() {
  return (
    <div className="rounded-xl border border-border bg-forge-900 p-6">
      <div className="flex items-start gap-5">
        {/* Avatar */}
        <Skeleton className="w-16 h-16 rounded-full" />
        {/* Info */}
        <div className="flex-1 space-y-3">
          <Skeleton className="w-40 h-6 rounded" />
          <Skeleton className="w-64 h-4 rounded" />
          {/* Tab bar */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-forge-800 mt-4 w-fit">
            <Skeleton className="h-7 w-[60px] rounded-md" />
            <Skeleton className="h-7 w-[70px] rounded-md" />
            <Skeleton className="h-7 w-[60px] rounded-md" />
            <Skeleton className="h-7 w-[55px] rounded-md" />
          </div>
        </div>
      </div>
    </div>
  );
}

/** Skeleton for My Bounties tab list items */
export function SkeletonBountyListItem() {
  return (
    <div className="flex items-center gap-4 px-4 py-3 rounded-lg bg-forge-900 border border-border">
      <div className="flex-1 min-w-0 space-y-2">
        <Skeleton className="w-full h-4 rounded" />
        <Skeleton className="w-24 h-3 rounded" />
      </div>
      <Skeleton className="w-20 h-5 rounded" />
      <Skeleton className="w-16 h-5 rounded-full" />
      <Skeleton className="w-10 h-4 rounded" />
    </div>
  );
}

/** Skeleton for earnings stat cards */
export function SkeletonEarningsStats() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="rounded-xl border border-border bg-forge-900 p-4 space-y-2">
          <Skeleton className="w-20 h-3 rounded" />
          <Skeleton className="w-24 h-7 rounded" />
        </div>
      ))}
    </div>
  );
}
