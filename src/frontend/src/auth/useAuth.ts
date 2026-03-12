import { useMsal } from "@azure/msal-react";
import { useCallback, useState } from "react";
import { loginRequest, apiScopes } from "./msal-config";

export function useAuth() {
  const { instance, accounts } = useMsal();
  const [loginError, setLoginError] = useState<string | null>(null);

  const login = useCallback(() => {
    setLoginError(null);
    instance.loginRedirect(loginRequest).catch((err) => {
      setLoginError(
        err instanceof Error ? err.message : "Sign in failed. Please try again.",
      );
    });
  }, [instance]);

  const logout = useCallback(() => {
    instance.logoutRedirect();
  }, [instance]);

  const getAccessToken = useCallback(async (): Promise<string> => {
    const account = accounts[0];
    if (!account) {
      throw new Error("No active account");
    }

    try {
      const response = await instance.acquireTokenSilent({
        scopes: apiScopes,
        account,
      });
      return response.accessToken;
    } catch {
      // Silent token acquisition failed - use redirect
      await instance.acquireTokenRedirect({ scopes: apiScopes });
      throw new Error("Redirecting for authentication");
    }
  }, [instance, accounts]);

  const user = accounts[0]
    ? {
        id: accounts[0].localAccountId,
        name: accounts[0].name ?? "",
        email: accounts[0].username,
      }
    : null;

  return {
    login,
    logout,
    getAccessToken,
    user,
    isAuthenticated: accounts.length > 0,
    loginError,
  };
}
