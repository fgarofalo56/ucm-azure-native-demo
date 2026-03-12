import axios from "axios";
import { msalInstance } from "../auth/msal-instance";
import { apiScopes } from "../auth/msal-config";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

/** Axios instance with base URL - auth token added automatically via interceptor. */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor that automatically acquires a token from MSAL for every request
apiClient.interceptors.request.use(async (config) => {
  const account = msalInstance.getActiveAccount() ?? msalInstance.getAllAccounts()[0];
  if (account) {
    try {
      const response = await msalInstance.acquireTokenSilent({
        scopes: apiScopes,
        account,
      });
      config.headers.Authorization = `Bearer ${response.accessToken}`;
    } catch {
      // Silent acquisition failed - token will be missing, API will return 401
      // The React component layer handles redirect for re-auth
    }
  }
  return config;
});
