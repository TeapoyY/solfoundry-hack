import { Variants } from 'framer-motion';

export const cardHover: Variants = {
  rest: { scale: 1, borderColor: '#1E1E2E' },
  hover: { scale: 1.01, borderColor: '#2E2E42' },
};

export const fadeIn: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
};
