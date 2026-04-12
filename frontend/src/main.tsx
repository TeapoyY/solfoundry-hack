import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider, useToastContext } from './contexts/ToastContext';
import { ToastContainer } from './components/ui/Toast';
import { queryClient } from './services/queryClient';
import App from './App';
import './index.css';

function Toasts() {
  const { toasts, removeToast } = useToastContext();
  return <ToastContainer toasts={toasts} onRemove={removeToast} />;
}

const root = document.getElementById('root');
if (!root) throw new Error('Root element not found');

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <AuthProvider>
            <App />
            <Toasts />
          </AuthProvider>
        </ToastProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>
);
