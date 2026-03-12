/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ENTRA_TENANT_ID: string;
  readonly VITE_ENTRA_CLIENT_ID: string;
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_SCOPE: string;
  readonly VITE_REDIRECT_URI: string;
  readonly VITE_AUTHORITY_HOST: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
