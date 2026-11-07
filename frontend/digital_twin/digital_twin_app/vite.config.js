import { defineConfig } from 'vite';
import cesium from 'vite-plugin-cesium';

export default defineConfig({
  base: '/geosense-agent-2/',
  plugins: [cesium()],
});