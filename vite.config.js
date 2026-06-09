import { defineConfig } from 'vite';

export default defineConfig({
  appType: 'mpa',
  server: {
    port: 5173,
    proxy: {
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/events': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        bypass: (req) => {
          if (req.url === '/' || req.url === '/index.html') return req.url;
          return null;
        },
      },
    },
  },
});
