import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const isElectron = mode === 'electron' || process.env.ELECTRON === 'true'

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    base: isElectron ? './' : '/',
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true,
        },
      },
    },
    build: {
      outDir: isElectron ? 'dist' : '../src/web/static/frontend',
      emptyOutDir: true,
    },
  }
})
