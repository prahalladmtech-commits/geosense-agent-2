
import { defineConfig } from 'vite';
import cesium from 'vite-plugin-cesium';
import { cp } from 'node:fs/promises';
import { resolve } from 'node:path';

export default defineConfig({
  base: '/geosense-agent-2/',

  define: {
    CESIUM_BASE_URL: JSON.stringify('/geosense-agent-2/cesium/')
  },

  plugins: [
    cesium(),

    {
      name: 'fix-cesium-github-pages-assets',
      async closeBundle() {
        const source = resolve('dist/geosense-agent-2/cesium');
        const destination = resolve('dist/cesium');

        await cp(source, destination, { recursive: true });
        console.log('Cesium assets copied to dist/cesium');
      }
    }
  ]
});
