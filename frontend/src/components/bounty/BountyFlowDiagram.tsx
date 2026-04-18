import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { BountyStatus } from '../../types/bounty';

interface FlowStage {
  id: string;
  label: string;
  description: string;
  status: BountyStatus | 'claimable' | 'active' | 'submitted' | 'review' | 'paid';
}

const FLOW_STAGES: FlowStage[] = [
  {
    id: 'open',
    label: 'Open',
    description: 'Bounty is listed and available for contributors to claim.',
    status: 'open',
  },
  {
    id: 'claimed',
    label: 'Claimed',
    description: 'A contributor has claimed this bounty and is working on it.',
    status: 'claimable',
  },
  {
    id: 'in_progress',
    label: 'In Progress',
    description: 'The contributor is actively implementing the solution.',
    status: 'active',
  },
  {
    id: 'submitted',
    label: 'Submitted',
    description: 'PR submitted for review. Awaiting AI code review.',
    status: 'submitted',
  },
  {
    id: 'in_review',
    label: 'In Review',
    description: 'AI review in progress (3-LLM pipeline, threshold 7.0/10).',
    status: 'in_review',
  },
  {
    id: 'paid',
    label: 'Paid',
    description: 'Approved and reward transferred to the contributor.',
    status: 'paid',
  },
];

// Map BountyStatus to flow stage index (0-based)
const STATUS_TO_INDEX: Partial<Record<BountyStatus, number>> = {
  open: 0,
  funded: 1,
  in_review: 4,
  completed: 5,
  cancelled: -1, // special — not shown in flow
};

interface BountyFlowDiagramProps {
  /** Current bounty status */
  status: BountyStatus;
  /** Optional compact mode for sidebar use */
  compact?: boolean;
  className?: string;
}

interface TooltipState {
  visible: boolean;
  stageIndex: number;
  x: number;
  y: number;
}

export function BountyFlowDiagram({ status, compact = false, className = '' }: BountyFlowDiagramProps) {
  const currentIndex = STATUS_TO_INDEX[status] ?? 0;
  const isCancelled = status === 'cancelled';

  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false,
    stageIndex: 0,
    x: 0,
    y: 0,
  });

  const handleMouseEnter = (index: number, e: React.MouseEvent<SVGGElement>) => {
    const rect = (e.currentTarget as SVGGElement).getBoundingClientRect();
    setTooltip({ visible: true, stageIndex: index, x: rect.left + rect.width / 2, y: rect.top });
  };

  const handleMouseLeave = () => {
    setTooltip((t) => ({ ...t, visible: false }));
  };

  // Node dimensions
  const nodeW = compact ? 72 : 96;
  const nodeH = compact ? 36 : 48;
  const nodeSpacing = compact ? 100 : 130;
  const totalW = nodeSpacing * (FLOW_STAGES.length - 1);
  const startX = 0;
  const centerY = compact ? 40 : 60;

  // Arrow path between nodes
  const arrowX = (i: number) => startX + i * nodeSpacing + nodeW;

  return (
    <div className={`relative ${className}`}>
      <svg
        viewBox={`0 0 ${totalW + nodeW} ${centerY * 2}`}
        className={`w-full overflow-visible ${compact ? 'h-20' : 'h-32'}`}
        style={{ maxWidth: '100%' }}
      >
        <defs>
          {/* Arrowhead marker */}
          <marker
            id="arrowhead"
            markerWidth="8"
            markerHeight="6"
            refX="7"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 8 3, 0 6" fill="#3E3E56" />
          </marker>
          <marker
            id="arrowhead-active"
            markerWidth="8"
            markerHeight="6"
            refX="7"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 8 3, 0 6" fill="#00E676" />
          </marker>
          <marker
            id="arrowhead-done"
            markerWidth="8"
            markerHeight="6"
            refX="7"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 8 3, 0 6" fill="#00E676" />
          </marker>

          {/* Glow filter for active node */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Connection lines */}
        {FLOW_STAGES.slice(0, -1).map((_, i) => {
          const isDone = i < currentIndex;
          const isActive = i === currentIndex - 1 || (currentIndex === 0 && i === 0 && !isCancelled);
          const lineColor = isDone || isActive ? '#00E676' : '#3E3E56';

          return (
            <line
              key={i}
              x1={arrowX(i) - 8}
              y1={centerY}
              x2={startX + (i + 1) * nodeSpacing - 8}
              y2={centerY}
              stroke={lineColor}
              strokeWidth={isActive || isDone ? 2 : 1.5}
              strokeDasharray={isActive && !isDone ? '4 3' : undefined}
              markerEnd={`url(#${isDone || isActive ? 'arrowhead-active' : 'arrowhead'})`}
              className={isActive && !isDone ? 'animate-dash' : ''}
            />
          );
        })}

        {/* Nodes */}
        {FLOW_STAGES.map((stage, i) => {
          const isDone = i < currentIndex;
          const isActive = i === currentIndex;
          const isFuture = i > currentIndex;
          const isCancelledNode = isCancelled;

          let fillColor = '#16161F';
          let strokeColor = '#3E3E56';
          let textColor = '#5C5C78';
          let labelBg = '#16161F';

          if (isDone) {
            fillColor = 'rgba(0,230,118,0.1)';
            strokeColor = '#00E676';
            textColor = '#00E676';
            labelBg = 'rgba(0,230,118,0.1)';
          } else if (isActive) {
            fillColor = 'rgba(0,230,118,0.15)';
            strokeColor = '#00E676';
            textColor = '#00E676';
            labelBg = 'rgba(0,230,118,0.15)';
          }

          if (isCancelledNode) {
            fillColor = 'rgba(255,82,82,0.1)';
            strokeColor = '#FF5252';
            textColor = '#FF5252';
            labelBg = 'rgba(255,82,82,0.1)';
          }

          const x = startX + i * nodeSpacing;
          const iconSize = compact ? 14 : 18;
          const nodeRx = compact ? 6 : 8;

          return (
            <g
              key={stage.id}
              transform={`translate(${x}, ${centerY - nodeH / 2})`}
              onMouseEnter={(e) => handleMouseEnter(i, e)}
              onMouseLeave={handleMouseLeave}
              style={{ cursor: 'pointer' }}
            >
              {/* Glow effect for active */}
              {isActive && !compact && (
                <rect
                  x={-4}
                  y={-4}
                  width={nodeW + 8}
                  height={nodeH + 8}
                  rx={nodeRx + 2}
                  fill="none"
                  stroke="#00E676"
                  strokeWidth={1}
                  opacity={0.3}
                  filter="url(#glow)"
                />
              )}

              {/* Node background */}
              <rect
                width={nodeW}
                height={nodeH}
                rx={nodeRx}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth={isActive ? 2 : 1.5}
              />

              {/* Step indicator dot */}
              <circle
                cx={compact ? 12 : 16}
                cy={nodeH / 2}
                r={compact ? 3 : 4}
                fill={isDone || isActive ? '#00E676' : '#3E3E56'}
              />

              {/* Stage label */}
              <text
                x={nodeW / 2 + (compact ? 0 : 4)}
                y={nodeH / 2 + 1}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={textColor}
                fontSize={compact ? 10 : 12}
                fontFamily="Inter, system-ui, sans-serif"
                fontWeight={isActive ? 700 : 500}
              >
                {compact ? stage.label : stage.label}
              </text>

              {/* Invisible hit area */}
              <rect
                width={nodeW}
                height={nodeH}
                fill="transparent"
                rx={nodeRx}
              />
            </g>
          );
        })}
      </svg>

      {/* Tooltip overlay */}
      <AnimatePresence>
        {tooltip.visible && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 pointer-events-none"
            style={{
              left: tooltip.x,
              top: tooltip.y - 8,
              transform: 'translate(-50%, -100%)',
            }}
          >
            <div className="bg-forge-700 border border-border rounded-lg px-3 py-2 shadow-xl max-w-[200px]">
              <p className="text-xs font-semibold text-text-primary mb-0.5">
                {FLOW_STAGES[tooltip.stageIndex].label}
              </p>
              <p className="text-xs text-text-secondary leading-relaxed">
                {FLOW_STAGES[tooltip.stageIndex].description}
              </p>
            </div>
            {/* Arrow */}
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-border" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cancelled overlay banner */}
      {isCancelled && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="bg-status-error/20 border border-status-error/30 text-status-error text-xs font-mono px-3 py-1 rounded-full">
            Cancelled
          </span>
        </div>
      )}
    </div>
  );
}
