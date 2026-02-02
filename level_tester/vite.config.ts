import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  root: ".",
  publicDir: "public",
  server: {
    port: 3000,
    open: true,
    watch: {
      // Watch for asset changes from Blender exports
      // Assumes exports directory is symlinked or located in public/assets
      usePolling: false,
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
  // Explicitly include asset directories for HMR
  optimizeDeps: {
    exclude: [],
  },
});
