import { Configuration, LogLevel } from "@azure/msal-browser";

// Configuration loaded from environment variables (set at build time)
// Defaults match the dev Entra ID app registrations (public client-side values)
const TENANT_ID =
  import.meta.env.VITE_ENTRA_TENANT_ID ?? "d1fc0498-f208-4b49-8376-beb9293acdf6";
const CLIENT_ID =
  import.meta.env.VITE_ENTRA_CLIENT_ID ?? "68cc0c43-121a-4272-a9f5-45c819a6f296";
const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI ?? window.location.origin;
const AUTHORITY_HOST =
  import.meta.env.VITE_AUTHORITY_HOST ?? "https://login.microsoftonline.com";
const API_SCOPE =
  import.meta.env.VITE_API_SCOPE ??
  "api://4eb00bab-f560-4af0-8116-917abb571891/access_as_user";

export const msalConfig: Configuration = {
  auth: {
    clientId: CLIENT_ID,
    authority: `${AUTHORITY_HOST}/${TENANT_ID}`,
    redirectUri: REDIRECT_URI,
    postLogoutRedirectUri: REDIRECT_URI,
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
      piiLoggingEnabled: false,
    },
  },
};

export const loginRequest = {
  scopes: [API_SCOPE],
};

export const apiScopes = [API_SCOPE];
