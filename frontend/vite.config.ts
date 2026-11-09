/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_TARGET ?? 'http://localhost:8000'

  return {
    plugins: [
      react(),
      VitePWA({
        // "prompt": l'utente decide quando aggiornare (evita reload durante una lezione SCORM)
        registerType: 'prompt',
        includeAssets: ['favicon.svg', 'icons/apple-touch-icon.png'],
        manifest: {
          name: 'ValueTech LMS',
          short_name: 'VT LMS',
          description: 'Piattaforma di formazione con supporto SCORM 1.2 / 2004',
          lang: 'it',
          theme_color: '#1e3a8a',
          background_color: '#f8fafc',
          display: 'standalone',
          start_url: '/',
          scope: '/',
          icons: [
            { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
            {
              src: '/icons/icon-maskable-512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'maskable',
            },
          ],
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
          // API e contenuti SCORM non devono MAI ricadere sull'app shell
          navigateFallbackDenylist: [/^\/api\//, /^\/scorm-content\//],
          runtimeCaching: [
            {
              // Catalogo corsi consultabile anche offline (dati eventualmente non aggiornati)
              urlPattern: ({ url }) => url.pathname.startsWith('/api/courses'),
              handler: 'NetworkFirst',
              method: 'GET',
              options: {
                cacheName: 'api-courses',
                networkTimeoutSeconds: 4,
                expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 },
              },
            },
            {
              // Asset statici dei pacchetti SCORM (il tracking resta online-only: vedi OP-003)
              urlPattern: ({ url }) => url.pathname.startsWith('/scorm-content/'),
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'scorm-content',
                expiration: { maxEntries: 500, maxAgeSeconds: 60 * 60 * 24 * 7 },
              },
            },
          ],
        },
        devOptions: { enabled: false },
      }),
    ],
    server: {
      port: 5173,
      // Stesso origin per app, API e contenuti SCORM: requisito per window.parent.API
      proxy: {
        '/api': { target: apiTarget, changeOrigin: true },
        '/scorm-content': { target: apiTarget, changeOrigin: true },
      },
    },
    test: {
      environment: 'jsdom',
    },
  }
})
