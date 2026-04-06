import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const frontendNodeModules = path.resolve(__dirname, "node_modules");

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    fs: {
      allow: ["../.."],
    },
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    include: ["../../tests/frontend/**/*.test.{ts,tsx}"],
    exclude: ["../../tests/frontend/e2e/**"],
    setupFiles: ["../../tests/frontend/setup.ts"],
    alias: {
      "@testing-library/react": path.join(frontendNodeModules, "@testing-library/react"),
      "@testing-library/user-event": path.join(frontendNodeModules, "@testing-library/user-event"),
      "@testing-library/jest-dom": path.join(frontendNodeModules, "@testing-library/jest-dom"),
      "@tanstack/react-query": path.join(frontendNodeModules, "@tanstack/react-query"),
      "react-router-dom": path.join(frontendNodeModules, "react-router-dom"),
      react: path.join(frontendNodeModules, "react"),
      "react-dom": path.join(frontendNodeModules, "react-dom"),
    },
  },
});
