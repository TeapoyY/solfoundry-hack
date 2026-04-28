import type { Variants } from 'framer-motion';

/**
 * Card hover animation: subtle lift and glow.
 * Used for bounty cards in grid listings.
 */
export const cardHover: Variants = {
  rest: { scale: 1, boxShadow: '0 0 0 0 transparent' },
  hover: {
    scale: 1.02,
    boxShadow: '0 8px 32px rgba(0, 230, 118, 0.12)',
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};

/**
 * Button hover animation with tap state.
 * Suitable for interactive button elements.
 */
export const buttonHover: Variants = {
  rest: { scale: 1 },
  hover: { scale: 1.04, transition: { duration: 0.15, ease: 'easeOut' } },
  tap: { scale: 0.97, transition: { duration: 0.1 } },
};

/**
 * Fade-in animation for page content.
 * Apply to wrapper elements for entrance animation.
 */
export const fadeIn: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

/**
 * Slide in from the right.
 * Use for sidebar or notification elements.
 */
export const slideInRight: Variants = {
  initial: { opacity: 0, x: 24 },
  animate: { opacity: 1, x: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

/**
 * Page transition animation for route changes.
 * Apply to page-level wrapper components.
 */
export const pageTransition: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2, ease: 'easeIn' } },
};

/**
 * Stagger container for list items.
 * Apply to parent motion.div — children should use staggerItem variants.
 */
export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.06,
    },
  },
};

/**
 * Stagger item animation.
 * Apply to individual list item elements within staggerContainer.
 */
export const staggerItem: Variants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
};
