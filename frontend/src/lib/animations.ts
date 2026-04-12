import { Variants } from 'framer-motion';

// Card hover animation — scale up slightly on hover
export const cardHover: Variants = {
  rest: { scale: 1, y: 0, boxShadow: '0 0 0 0 transparent' },
  hover: { scale: 1.01, y: -2, boxShadow: '0 8px 30px rgba(0,0,0,0.3)' },
};

// Fade-in animation for page content
export const fadeIn: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
};

// Page transition — used with initial/animate/exit on motion.div
export const pageTransition: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2, ease: 'easeIn' } },
};

// Stagger container for list animations — wrap with {staggerChildren: 0.07}
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: { staggerChildren: 0.07 },
  },
};

// Stagger item — child of staggerContainer; fade + slide up
export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
};

// Slide in from right — for activity feeds, notifications
export const slideInRight: Variants = {
  initial: { opacity: 0, x: 40 },
  animate: { opacity: 1, x: 0, transition: { duration: 0.3, ease: 'easeOut' } },
  exit: { opacity: 0, x: -20, transition: { duration: 0.2 } },
};

// Button hover — scale + shadow lift
export const buttonHover: Variants = {
  rest: { scale: 1, boxShadow: '0 0 0 0 transparent' },
  hover: { scale: 1.03, boxShadow: '0 6px 20px rgba(0,0,0,0.25)' },
  tap: { scale: 0.97 },
};

// Slide-up fade-in for list items
export const slideUpFade: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
};
