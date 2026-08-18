import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Forward "/api" calls to the Flask dev server so the frontend can use a
  // relative "/api" base in both dev and production (where Flask serves both).
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
})
