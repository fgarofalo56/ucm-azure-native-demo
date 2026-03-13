import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const nodeModules = path.resolve(__dirname, "node_modules");

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
    alias: [
      {
        find: /^@testing-library\/(.*)$/,
        replacement: path.join(nodeModules, "@testing-library/$1"),
      },
      {
        find: /^@tanstack\/(.*)$/,
        replacement: path.join(nodeModules, "@tanstack/$1"),
      },
      { find: /^react-router(.*)$/, replacement: path.join(nodeModules, "react-router$1") },
      { find: /^react-dom(.*)$/, replacement: path.join(nodeModules, "react-dom$1") },
      { find: /^react$/, replacement: path.join(nodeModules, "react") },
    ],
  },
});
