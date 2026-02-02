import { defineConfig, type PluginOption } from "vite";
import { resolve } from "path";

// Plugin to watch public/levels directory and trigger full reload
function watchPublicLevels(): PluginOption {
  return {
    name: "watch-public-levels",
    configureServer(server) {
      const levelsDir = resolve(__dirname, "public/levels");
      server.watcher.add(levelsDir);
      server.watcher.on("change", (path) => {
        if (path.startsWith(levelsDir)) {
          console.log(`[watch-public-levels] Detected change: ${path}`);
          server.ws.send({ type: "full-reload" });
        }
      });
      server.watcher.on("add", (path) => {
        if (path.startsWith(levelsDir)) {
          console.log(`[watch-public-levels] Detected new file: ${path}`);
          server.ws.send({ type: "full-reload" });
        }
      });
    },
  };
}

export default defineConfig({
  root: ".",
  publicDir: "public",
  plugins: [watchPublicLevels()],
  server: {
    port: 3000,
    open: true,
    watch: {
      // Watch for asset changes from Blender exports
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
