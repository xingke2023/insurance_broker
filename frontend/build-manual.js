import { build } from 'vite';
import react from '@vitejs/plugin-react-swc';

async function runBuild() {
  try {
    await build({
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
        minify: false,
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
    console.log('Build completed successfully!');
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

runBuild();
