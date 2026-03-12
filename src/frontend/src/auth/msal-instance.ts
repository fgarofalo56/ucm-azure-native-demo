import { PublicClientApplication, EventType } from "@azure/msal-browser";
import { msalConfig } from "./msal-config";

/** Shared MSAL instance used by both React components and the API client. */
export const msalInstance = new PublicClientApplication(msalConfig);

/** Initialize MSAL and handle redirect. Must be awaited before rendering. */
export async function initializeMsal(): Promise<void> {
  await msalInstance.initialize();

  const response = await msalInstance.handleRedirectPromise();
  if (response?.account) {
    msalInstance.setActiveAccount(response.account);
  } else {
    const accounts = msalInstance.getAllAccounts();
    const firstAccount = accounts[0] ?? null;
    if (firstAccount) {
      msalInstance.setActiveAccount(firstAccount);
    }
  }

  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
      const payload = event.payload as {
        account: Parameters<typeof msalInstance.setActiveAccount>[0] | undefined;
      };
      if (payload.account) {
        msalInstance.setActiveAccount(payload.account);
      }
    }
  });
}
