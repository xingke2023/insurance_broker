import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
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
  }
})
