import { defineConfig } from 'vite'

export default defineConfig({
  // Server configuration
  server: {
    port: 3000,
    open: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://192.168.0.245:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },

  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: './index.html'
      },
      output: {
        manualChunks: undefined
      }
    },
    // Ensure public assets are copied to dist
    copyPublicDir: true
  },

  // Public directory for static assets
  publicDir: 'public',

  // Environment variable prefix (already using VITE_)
  envPrefix: 'VITE_',

  // Root directory
  root: '.',

  // Base public path
  base: './'
})
