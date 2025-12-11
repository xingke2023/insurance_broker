const { defineConfig } = require('vite');
const react = require('@vitejs/plugin-react').default;

// https://vite.dev/config/
module.exports = defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 8008,
    proxy: {
      '/api': {
        target: 'http://localhost:8017',
        changeOrigin: true,
      }
    }
  },
  build: {
    target: 'esnext',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  optimizeDeps: {
    esbuildOptions: {
      target: 'esnext'
    }
  }
});
