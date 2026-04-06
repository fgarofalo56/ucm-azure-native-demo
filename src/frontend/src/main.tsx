import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MsalProvider } from "@azure/msal-react";
import { msalInstance, initializeMsal } from "./auth/msal-instance";
import { ThemeProvider } from "./contexts/ThemeContext";
import { ToastProvider } from "./contexts/ToastContext";
import { App } from "./App";
import "./styles/globals.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

// MSAL v3 requires initialize() before any interaction
initializeMsal().then(() => {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>
            <ToastProvider>
              <BrowserRouter>
                <App />
              </BrowserRouter>
            </ToastProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </MsalProvider>
    </React.StrictMode>,
  );
});
