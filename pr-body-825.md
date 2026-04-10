## Bounty: Toast Notification System
**Reward:** 150,000 $FNDRY | **Tier:** T1 (Open Race) | **Domain:** Frontend

### What was implemented

Built a full toast notification system satisfying all acceptance criteria:

**Components:**
- `ToastProvider` — context provider wrapping the app, manages toast queue with auto-dismiss
- `ToastContainer` — fixed top-right overlay, stacks up to 5 toasts, AnimatePresence for smooth slide-in from right and fade-out on dismiss
- `useToast()` hook — exposes `toast()`, `success()`, `error()`, `warning()`, `info()` methods

**Toast Variants:**
- `success` — green (CheckCircle icon)
- `error` — rose/red (XCircle icon)
- `warning` — amber (AlertTriangle icon)
- `info` — neutral (Info icon)

**Features:**
- Auto-dismiss after 5 seconds (configurable per-toast via `duration: 0` for persistent)
- Manual close button (X icon)
- Slide-in animation from top-right (framer-motion)
- Backdrop blur for depth
- Accessible with `role="alert"`
- Stacks properly (oldest at bottom)

**Wired into existing flows:**
- `SubmissionForm` — success toast on submission received, fee verified; error toast on failure
- `BountyCreateWizard` — success toast on bounty created/funded; error toast on API failures

Closes #825
