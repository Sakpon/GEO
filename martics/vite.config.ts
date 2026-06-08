import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Frontend-only build. The Cloudflare Worker (src/worker) is bundled separately
// by wrangler; Vite just emits the SPA into dist/client, which the Worker serves
// via the ASSETS binding.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist/client",
    emptyOutDir: true,
  },
  server: {
    // `npm run dev:ui` proxies API calls to a locally-running `wrangler dev`.
    proxy: {
      "/api": "http://localhost:8787",
    },
  },
});
