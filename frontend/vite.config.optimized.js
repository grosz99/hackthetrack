import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Optimized Vite configuration for production deployment
// This configuration improves bundle size and performance
export default defineConfig({
  plugins: [react({
    jsxRuntime: 'automatic'
  })],
  base: '/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Disable sourcemaps in production for smaller bundle
    sourcemap: false,
    rollupOptions: {
      output: {
        // Code splitting for better caching and parallel loading
        manualChunks: {
          // Core React libraries
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Heavy charting libraries
          'vendor-charts': ['plotly.js', 'react-plotly.js', 'recharts'],
          // Markdown rendering
          'vendor-markdown': ['react-markdown']
        }
      }
    },
    // Increase warning limit since we're using heavy charting libraries
    chunkSizeWarningLimit: 1000
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom']
  }
})
