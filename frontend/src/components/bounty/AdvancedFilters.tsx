import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, SlidersHorizontal, Bookmark, BookmarkCheck } from 'lucide-react';

interface MultiSelectOption {
  value: string;
  label: string;
  color?: string;
}

interface FilterState {
  skills: string[];
  tiers: string[];
  domains: string[];
  rewardMin: number;
  rewardMax: number;
}

const ALL_SKILLS: MultiSelectOption[] = [
  { value: 'TypeScript', label: 'TypeScript', color: '#3178C6' },
  { value: 'JavaScript', label: 'JavaScript', color: '#F7DF1E' },
  { value: 'Python', label: 'Python', color: '#3776AB' },
  { value: 'Rust', label: 'Rust', color: '#CE422B' },
  { value: 'Solidity', label: 'Solidity', color: '#36396B' },
  { value: 'Go', label: 'Go', color: '#00ADD8' },
  { value: 'React', label: 'React', color: '#61DAFB' },
  { value: 'Node', label: 'Node.js', color: '#339933' },
];

const ALL_TIERS: MultiSelectOption[] = [
  { value: 'T1', label: 'T1 — Open Race', color: '#00E676' },
  { value: 'T2', label: 'T2 — Requires T1', color: '#40C4FF' },
  { value: 'T3', label: 'T3 — Requires T2', color: '#7C3AED' },
];

const ALL_DOMAINS: MultiSelectOption[] = [
  { value: 'frontend', label: 'Frontend', color: '#40C4FF' },
  { value: 'backend', label: 'Backend', color: '#7C3AED' },
  { value: 'integration', label: 'Integration', color: '#FFB300' },
  { value: 'agent', label: 'AI Agent', color: '#FF5252' },
  { value: 'contracts', label: 'Contracts', color: '#00E676' },
  { value: 'security', label: 'Security', color: '#F7DF1E' },
  { value: 'devops', label: 'DevOps', color: '#FA7343' },
  { value: 'docs', label: 'Documentation', color: '#A78BFA' },
];

const REWARD_PRESETS = [
  { label: 'Any', min: 0, max: Infinity },
  { label: '< 50K', min: 0, max: 50000 },
  { label: '50K–200K', min: 50000, max: 200000 },
  { label: '200K–500K', min: 200000, max: 500000 },
  { label: '500K+', min: 500000, max: Infinity },
];

const STORAGE_KEY = 'solfoundry-advanced-filters';

function loadSavedFilters(): FilterState {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return { skills: [], tiers: [], domains: [], rewardMin: 0, rewardMax: Infinity };
}

function saveFiltersToStorage(filters: FilterState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  } catch {}
}

interface MultiSelectDropdownProps {
  label: string;
  options: MultiSelectOption[];
  selected: string[];
  onChange: (values: string[]) => void;
}

function MultiSelectDropdown({ label, options, selected, onChange }: MultiSelectDropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const toggle = (val: string) => {
    if (selected.includes(val)) {
      onChange(selected.filter((v) => v !== val));
    } else {
      onChange([...selected, val]);
    }
  };

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors duration-150 border ${
          selected.length > 0
            ? 'bg-forge-700 text-text-primary border-border-active'
            : 'bg-forge-800 text-text-muted border-border hover:border-border-hover hover:text-text-secondary'
        }`}
      >
        {label}
        {selected.length > 0 && (
          <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-emerald text-forge-950 text-xs font-bold">
            {selected.length}
          </span>
        )}
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="absolute top-full left-0 mt-1 z-50 bg-forge-800 border border-border rounded-xl shadow-2xl shadow-black/60 p-2 min-w-[180px]">
          {options.map((opt) => {
            const checked = selected.includes(opt.value);
            return (
              <button
                key={opt.value}
                onClick={() => toggle(opt.value)}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm text-text-secondary hover:bg-forge-700 hover:text-text-primary transition-colors text-left"
              >
                <span
                  className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 transition-colors ${
                    checked ? 'bg-emerald border-emerald' : 'border-border'
                  }`}
                >
                  {checked && <svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L3.5 6.5L9 1" stroke="#050505" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                </span>
                {opt.color && (
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: opt.color }} />
                )}
                <span className="truncate">{opt.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface AdvancedFiltersProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

export function AdvancedFilters({ filters, onChange }: AdvancedFiltersProps) {
  const [showSaveInput, setShowSaveInput] = useState(false);
  const [savedSets, setSavedSets] = useState<Record<string, FilterState>>({});

  useEffect(() => {
    try {
      const all = localStorage.getItem('solfoundry-filter-sets');
      if (all) setSavedSets(JSON.parse(all));
    } catch {}
  }, []);

  const update = (patch: Partial<FilterState>) => onChange({ ...filters, ...patch });

  const rewardPreset = REWARD_PRESETS.find(
    (p) => p.min === filters.rewardMin && p.max === filters.rewardMax,
  );

  const hasActiveFilters =
    filters.skills.length > 0 ||
    filters.tiers.length > 0 ||
    filters.domains.length > 0 ||
    filters.rewardMin > 0 ||
    filters.rewardMax < Infinity;

  const clearAll = () =>
    onChange({ skills: [], tiers: [], domains: [], rewardMin: 0, rewardMax: Infinity });

  const savePreset = (name: string) => {
    const updated = { ...savedSets, [name]: { ...filters } };
    setSavedSets(updated);
    try { localStorage.setItem('solfoundry-filter-sets', JSON.stringify(updated)); } catch {}
    setShowSaveInput(false);
  };

  const loadPreset = (name: string) => {
    const preset = savedSets[name];
    if (preset) onChange(preset);
  };

  const deletePreset = (name: string) => {
    const updated = { ...savedSets };
    delete updated[name];
    setSavedSets(updated);
    try { localStorage.setItem('solfoundry-filter-sets', JSON.stringify(updated)); } catch {}
  };

  return (
    <div className="space-y-3">
      {/* Filter row */}
      <div className="flex flex-wrap items-center gap-2">
        <MultiSelectDropdown
          label="Language"
          options={ALL_SKILLS}
          selected={filters.skills}
          onChange={(v) => update({ skills: v })}
        />
        <MultiSelectDropdown
          label="Tier"
          options={ALL_TIERS}
          selected={filters.tiers}
          onChange={(v) => update({ tiers: v })}
        />
        <MultiSelectDropdown
          label="Domain"
          options={ALL_DOMAINS}
          selected={filters.domains}
          onChange={(v) => update({ domains: v })}
        />

        {/* Reward preset buttons */}
        <div className="flex items-center gap-1">
          <SlidersHorizontal className="w-3.5 h-3.5 text-text-muted" />
          {REWARD_PRESETS.map((preset) => (
            <button
              key={preset.label}
              onClick={() =>
                update({ rewardMin: preset.min, rewardMax: preset.max })
              }
              className={`px-2 py-1 rounded-md text-xs font-medium transition-colors ${
                rewardPreset?.label === preset.label
                  ? 'bg-purple text-white'
                  : 'bg-forge-800 text-text-muted border border-border hover:border-border-hover hover:text-text-secondary'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {hasActiveFilters && (
          <button
            onClick={clearAll}
            className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium text-status-error border border-status-error/30 hover:bg-status-error/10 transition-colors"
          >
            <X className="w-3 h-3" /> Clear
          </button>
        )}

        {/* Save/Load presets */}
        <div className="relative ml-auto">
          <button
            onClick={() => setShowSaveInput((s) => !s)}
            className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium text-text-muted border border-border hover:border-border-hover hover:text-text-secondary transition-colors"
          >
            <Bookmark className="w-3 h-3" /> Save
          </button>
          {showSaveInput && (
            <div className="absolute right-0 top-full mt-1 z-50 bg-forge-800 border border-border rounded-xl shadow-2xl shadow-black/60 p-3 w-56">
              <p className="text-xs text-text-muted mb-2 font-medium">Saved Filter Sets</p>
              {Object.keys(savedSets).length === 0 && (
                <p className="text-xs text-text-muted mb-2">No saved sets yet.</p>
              )}
              {Object.entries(savedSets).map(([name]) => (
                <div key={name} className="flex items-center gap-1 mb-1">
                  <button
                    onClick={() => loadPreset(name)}
                    className="flex-1 text-left px-2 py-1 rounded text-xs text-text-secondary hover:bg-forge-700 hover:text-text-primary transition-colors truncate"
                  >
                    {name}
                  </button>
                  <button
                    onClick={() => deletePreset(name)}
                    className="text-text-muted hover:text-status-error transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
              <div className="mt-2 flex gap-1">
                <input
                  id="filter-set-name"
                  type="text"
                  placeholder="Preset name..."
                  className="flex-1 bg-forge-900 border border-border rounded px-2 py-1 text-xs text-text-primary placeholder:text-text-muted focus:border-emerald outline-none"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const val = (e.target as HTMLInputElement).value.trim();
                      if (val) savePreset(val);
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const input = document.getElementById('filter-set-name') as HTMLInputElement;
                    const val = input.value.trim();
                    if (val) savePreset(val);
                  }}
                  className="px-2 py-1 rounded bg-emerald text-forge-950 text-xs font-semibold hover:bg-emerald/90 transition-colors"
                >
                  Save
                </button>
              </div>
            </div>
          )}
        </div>

        {Object.keys(savedSets).length > 0 && (
          <div className="flex items-center gap-1">
            <BookmarkCheck className="w-3.5 h-3.5 text-emerald" />
            <span className="text-xs text-text-muted">{Object.keys(savedSets).length} saved</span>
          </div>
        )}
      </div>

      {/* Active filter chips */}
      {(filters.skills.length > 0 || filters.tiers.length > 0 || filters.domains.length > 0) && (
        <div className="flex flex-wrap items-center gap-1.5">
          {filters.skills.map((s) => (
            <span key={s} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-forge-700 text-xs text-text-secondary border border-border">
              {ALL_SKILLS.find((o) => o.value === s)?.color && (
                <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: ALL_SKILLS.find((o) => o.value === s)?.color }} />
              )}
              {s}
              <button onClick={() => update({ skills: filters.skills.filter((v) => v !== s) })} className="text-text-muted hover:text-text-primary ml-0.5">
                <X className="w-2.5 h-2.5" />
              </button>
            </span>
          ))}
          {filters.tiers.map((t) => (
            <span key={t} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-forge-700 text-xs text-text-secondary border border-border">
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: ALL_TIERS.find((o) => o.value === t)?.color }} />
              {t}
              <button onClick={() => update({ tiers: filters.tiers.filter((v) => v !== t) })} className="text-text-muted hover:text-text-primary ml-0.5">
                <X className="w-2.5 h-2.5" />
              </button>
            </span>
          ))}
          {filters.domains.map((d) => (
            <span key={d} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-forge-700 text-xs text-text-secondary border border-border">
              {d}
              <button onClick={() => update({ domains: filters.domains.filter((v) => v !== d) })} className="text-text-muted hover:text-text-primary ml-0.5">
                <X className="w-2.5 h-2.5" />
              </button>
            </span>
          ))}
          {rewardPreset && rewardPreset.label !== 'Any' && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-purple/20 text-xs text-purple-light border border-purple/30">
              Reward: {rewardPreset.label}
              <button onClick={() => update({ rewardMin: 0, rewardMax: Infinity })} className="text-text-muted hover:text-text-primary ml-0.5">
                <X className="w-2.5 h-2.5" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export { loadSavedFilters, saveFiltersToStorage };
export type { FilterState };
