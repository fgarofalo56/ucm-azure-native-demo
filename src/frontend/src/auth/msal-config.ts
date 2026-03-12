import { Configuration, LogLevel } from "@azure/msal-browser";

// Configuration loaded from environment variables (set at build time)
const TENANT_ID = import.meta.env.VITE_ENTRA_TENANT_ID ?? "";
const CLIENT_ID = import.meta.env.VITE_ENTRA_CLIENT_ID ?? "";
const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI ?? window.location.origin;
const AUTHORITY_HOST =
  import.meta.env.VITE_AUTHORITY_HOST ?? "https://login.microsoftonline.com";
const API_SCOPE =
  import.meta.env.VITE_API_SCOPE ?? "api://assurancenet-api/Documents.ReadWrite";

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
