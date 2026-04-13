import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronDown, Loader2, Plus, Search, X } from 'lucide-react';
import { BountyCard } from './BountyCard';
import { AdvancedFilters, loadSavedFilters, saveFiltersToStorage, type FilterState } from './AdvancedFilters';
import { useInfiniteBounties } from '../../hooks/useBounties';
import { staggerContainer, staggerItem } from '../../lib/animations';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
}

export function BountyGrid() {
  const [advancedFilters, setAdvancedFilters] = useState<FilterState>(() => loadSavedFilters());
  const [statusFilter, setStatusFilter] = useState<string>('open');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const debouncedSearch = useDebounce(searchQuery, 300);

  // Persist advanced filters to localStorage on change
  useEffect(() => {
    saveFiltersToStorage(advancedFilters);
  }, [advancedFilters]);

  // Derive single skill from advancedFilters.skills for API call
  const apiSkill = advancedFilters.skills.length === 1 ? advancedFilters.skills[0] : undefined;

  const params = {
    status: statusFilter,
    skill: apiSkill,
  };

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading, isError } =
    useInfiniteBounties(params);

  const allBounties = data?.pages.flatMap((p) => p.items) ?? [];

  const filteredBounties = useMemo(() => {
    let result = allBounties;

    // Text search
    if (debouncedSearch.trim()) {
      const q = debouncedSearch.toLowerCase();
      result = result.filter(
        (b) =>
          b.title.toLowerCase().includes(q) ||
          b.description.toLowerCase().includes(q) ||
          b.skills.some((s) => s.toLowerCase().includes(q)) ||
          (b.category ?? '').toLowerCase().includes(q),
      );
    }

    // Multi-skill filter (client-side when multiple selected)
    if (advancedFilters.skills.length > 1) {
      result = result.filter((b) =>
        advancedFilters.skills.some((skill) =>
          b.skills.some((s) => s.toLowerCase() === skill.toLowerCase()),
        ),
      );
    }

    // Tier filter
    if (advancedFilters.tiers.length > 0) {
      result = result.filter((b) => advancedFilters.tiers.includes(b.tier));
    }

    // Domain/category filter
    if (advancedFilters.domains.length > 0) {
      result = result.filter((b) =>
        advancedFilters.domains.some(
          (domain) =>
            (b.category ?? '').toLowerCase() === domain.toLowerCase() ||
            b.category?.toLowerCase().includes(domain.toLowerCase()),
        ),
      );
    }

    // Reward range filter
    if (advancedFilters.rewardMin > 0 || advancedFilters.rewardMax < Infinity) {
      result = result.filter(
        (b) =>
          b.reward_amount >= advancedFilters.rewardMin &&
          b.reward_amount <= advancedFilters.rewardMax,
      );
    }

    return result;
  }, [allBounties, debouncedSearch, advancedFilters]);

  return (
    <section id="bounties" className="py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header row */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h2 className="font-sans text-2xl font-semibold text-text-primary">Open Bounties</h2>
          <div className="flex items-center gap-2">
            {/* Search bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
              <input
                type="text"
                placeholder="Search bounties..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="appearance-none bg-forge-800 border border-border rounded-lg pl-9 pr-8 py-1.5 text-sm text-text-secondary font-medium placeholder:text-text-muted focus:border-emerald outline-none transition-colors duration-150 w-52 sm:w-64"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Advanced filters toggle */}
            <button
              onClick={() => setShowAdvanced((s) => !s)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors duration-150 ${
                showAdvanced
                  ? 'bg-purple/20 text-purple-light border-purple/40'
                  : 'bg-forge-800 text-text-muted border-border hover:border-border-hover hover:text-text-secondary'
              }`}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className={showAdvanced ? 'text-purple-light' : ''}>
                <path d="M1 3h12M3 7h8M5 11h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              Filters
              {(advancedFilters.skills.length > 0 ||
                advancedFilters.tiers.length > 0 ||
                advancedFilters.domains.length > 0 ||
                advancedFilters.rewardMin > 0 ||
                advancedFilters.rewardMax < Infinity) && (
                <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-purple text-white text-xs font-bold">
                  {advancedFilters.skills.length +
                    advancedFilters.tiers.length +
                    advancedFilters.domains.length +
                    (advancedFilters.rewardMin > 0 || advancedFilters.rewardMax < Infinity ? 1 : 0)}
                </span>
              )}
            </button>

            <Link
              to="/bounties/create"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald text-forge-950 font-semibold text-sm hover:bg-emerald/90 transition-colors duration-150"
            >
              <Plus className="w-4 h-4" /> Post a Bounty
            </Link>

            {/* Status filter */}
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="appearance-none bg-forge-800 border border-border rounded-lg px-3 py-1.5 pr-8 text-sm text-text-secondary font-medium focus:border-emerald outline-none transition-colors duration-150 cursor-pointer"
              >
                <option value="open">Open</option>
                <option value="funded">Funded</option>
                <option value="in_review">In Review</option>
                <option value="completed">Completed</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Advanced filters panel */}
        {showAdvanced && (
          <div className="mb-6 p-4 bg-forge-850 border border-border rounded-xl">
            <AdvancedFilters filters={advancedFilters} onChange={setAdvancedFilters} />
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="h-52 rounded-xl border border-border bg-forge-900 overflow-hidden"
              >
                <div className="h-full bg-gradient-to-r from-forge-900 via-forge-800 to-forge-900 bg-[length:200%_100%] animate-shimmer" />
              </div>
            ))}
          </div>
        )}

        {/* Error state */}
        {isError && !isLoading && (
          <div className="text-center py-16">
            <p className="text-text-muted mb-4">Could not load bounties. Backend may be offline.</p>
            <p className="text-text-muted text-sm font-mono">Running in demo mode — no bounties to display.</p>
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !isError && filteredBounties.length === 0 && (
          <div className="text-center py-16">
            <p className="text-text-muted text-lg mb-2">No bounties found</p>
            <p className="text-text-muted text-sm">
              {debouncedSearch.trim() || advancedFilters.skills.length > 0 || advancedFilters.tiers.length > 0 || advancedFilters.domains.length > 0
                ? 'Try adjusting your filters or search terms.'
                : 'Check back soon for new bounties.'}
            </p>
          </div>
        )}

        {/* Bounty grid */}
        {!isLoading && filteredBounties.length > 0 && (
          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: '-50px' }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
          >
            {filteredBounties.map((bounty) => (
              <motion.div key={bounty.id} variants={staggerItem}>
                <BountyCard bounty={bounty} />
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Load more */}
        {hasNextPage && (
          <div className="mt-10 text-center">
            <button
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg border border-border text-text-secondary text-sm font-medium hover:border-border-hover hover:text-text-primary transition-all duration-200 disabled:opacity-50"
            >
              {isFetchingNextPage && <Loader2 className="w-4 h-4 animate-spin" />}
              Load More
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
