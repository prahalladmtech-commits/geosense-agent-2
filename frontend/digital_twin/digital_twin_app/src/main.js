
import './style.css';
import { initializeSiteAnalysis } from './site-analysis.js';

import {
  Viewer,
  Cartesian3,
  Cesium3DTileset,
} from 'cesium';

import 'cesium/Build/Cesium/Widgets/widgets.css';

const app = document.querySelector('#app');

app.innerHTML = `
  <header class="topbar">
    <div class="brand">
      <span class="brand-mark">G</span>
      <div>
        <h1>GeoSense</h1>
        <p>GEOSPATIAL DIGITAL TWIN</p>
      </div>
    </div>
    <div class="status"><span></span> 3D VIEWER</div>
  </header>

  <main class="workspace">
    <aside class="sidebar">
      <p class="eyebrow">WORKSPACE</p>
      <h2>Madhya Pradesh Drone Twin</h2>
      <p class="description">
        Explore the drone point cloud survey near Bhopal,
        Madhya Pradesh, India.
      </p>

      <label for="location">Fly to a location</label>
      <select id="location">
        <option value="bhopal">
          Drone Survey — Bhopal, Madhya Pradesh
        </option>
        <option value="kolkata">Kolkata, India</option>
        <option value="chennai">Chennai, India</option>
        <option value="delhi">New Delhi, India</option>
        <option value="mumbai">Mumbai, India</option>
        <option value="autzen">Autzen, Oregon, USA</option>
      </select>

      <button id="fly-button" type="button">
        Go to location ↗
      </button>

      <div class="info-card">
        <p class="eyebrow">CURRENT VIEW</p>
        <h3 id="place-name">
          Drone Survey — Bhopal, Madhya Pradesh
        </h3>
        <p id="coordinates">
          23.25499296° N, 77.45749779° E
        </p>
        <p class="footnote">
          Coordinates represent the approximate centre of the
          point-cloud bounding box.
        </p>
      </div>

      <div class="info-card">
        <p class="eyebrow">DRONE POINT CLOUD</p>
        <p>Preview: approximately 100,354 points</p>
        <p>Full dataset: 10,035,331 points</p>
        <p>Source format: LAZ</p>
        <p>Source CRS: EPSG:32643</p>
        <p>Tiles format: 3D Tiles</p>
        <button id="load-drone" type="button">
          Load full drone point cloud
        </button>
        <p id="drone-status">Drone layer not loaded.</p>
      </div>

      <div class="info-card">
        <p class="eyebrow">POINT CLOUD DISPLAY</p>
        <button id="toggle-drone" type="button" disabled>
          Hide point cloud
        </button>
        <p id="visibility-status">Load the point cloud first.</p>
      </div>

      <div class="info-card">
        <p class="eyebrow">SURVEY STATISTICS</p>
        <p>Total points: <strong>10,035,331</strong></p>
        <p>Survey width: <strong>223 m</strong></p>
        <p>Survey length: <strong>233 m</strong></p>
        <p>Elevation range: <strong>56 m</strong></p>
      </div>

      <div class="info-card">
        <p class="eyebrow">PHASE 4 MODULES</p>
        <ul>
          <li>3D Digital Twin</li>
          <li>Drone point-cloud integration</li>
          <li>GeoAI agent connection</li>
          <li>Geospatial risk analysis</li>
        </ul>
      </div>

      <p class="footnote">GeoSense_Agent · Phase 5</p>
    </aside>

    <section class="map-panel">
      <div id="cesiumContainer"></div>
      <div class="map-label">EARTH · 3D GLOBE</div>
      <div id="map-message" class="map-message">
        Initializing 3D globe...
      </div>
    </section>
  </main>
`;

const locations = {
  bhopal: {
    name: 'Drone Survey — Bhopal, Madhya Pradesh',
    lon: 77.45749779,
    lat: 23.25499296,
    height: 2500,
    coordinates: '23.25499296° N, 77.45749779° E',
  },

  kolkata: {
    name: 'Kolkata, India',
    lon: 88.3639,
    lat: 22.5726,
    height: 18000,
    coordinates: '22.5726° N, 88.3639° E',
  },

  chennai: {
    name: 'Chennai, India',
    lon: 80.2707,
    lat: 13.0827,
    height: 18000,
    coordinates: '13.0827° N, 80.2707° E',
  },

  delhi: {
    name: 'New Delhi, India',
    lon: 77.2090,
    lat: 28.6139,
    height: 22000,
    coordinates: '28.6139° N, 77.2090° E',
  },

  mumbai: {
    name: 'Mumbai, India',
    lon: 72.8777,
    lat: 19.0760,
    height: 20000,
    coordinates: '19.0760° N, 72.8777° E',
  },

  autzen: {
    name: 'Autzen, Oregon, USA',
    lon: -123.07,
    lat: 44.06,
    height: 12000,
    coordinates: '44.06° N, 123.07° W',
  },
};

let viewer;
let droneTileset;

async function initializeGlobe() {
  const message = document.querySelector('#map-message');

  try {
    viewer = new Viewer('cesiumContainer', {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: true,
      sceneModePicker: true,
      navigationHelpButton: false,
      infoBox: false,
      selectionIndicator: false,
    });

    viewer.camera.flyTo({
      destination: Cartesian3.fromDegrees(
        locations.bhopal.lon,
        locations.bhopal.lat,
        locations.bhopal.height,
      ),
    });

    message.textContent =
      'Globe ready. Study area set to the approximate drone point-cloud centre.';

  } catch (error) {
    console.error('Cesium initialization failed:', error);

    message.textContent =
      'Globe initialization failed. Check the browser console.';
  }
}

// Location navigation
document
  .querySelector('#fly-button')
  .addEventListener('click', () => {
    const selected = locations[
      document.querySelector('#location').value
    ];

    if (!viewer || !selected) return;

    document.querySelector('#place-name').textContent =
      selected.name;

    document.querySelector('#coordinates').textContent =
      selected.coordinates;

    viewer.camera.flyTo({
      destination: Cartesian3.fromDegrees(
        selected.lon,
        selected.lat,
        selected.height,
      ),
      duration: 2,
    });
  });

// Point cloud visibility
document
  .querySelector('#toggle-drone')
  .addEventListener('click', () => {
    if (!droneTileset) return;

    droneTileset.show = !droneTileset.show;

    const visible = droneTileset.show;

    document.querySelector('#toggle-drone').textContent =
      visible ? 'Hide point cloud' : 'Show point cloud';

    document.querySelector('#visibility-status').textContent =
      visible
        ? 'Point cloud is visible.'
        : 'Point cloud is hidden.';
  });

// Load full drone point cloud
document
  .querySelector('#load-drone')
  .addEventListener('click', async () => {
    const status = document.querySelector('#drone-status');
    const message = document.querySelector('#map-message');
    const button = document.querySelector('#load-drone');

    if (!viewer || button.disabled) return;

    button.disabled = true;

    status.textContent = 'Loading drone tiles...';
    message.textContent = 'Loading drone point cloud...';

    try {
      if (!droneTileset) {
        droneTileset = await Cesium3DTileset.fromUrl(
          '/tiles/drone_fixed/tileset.json',
        );

        viewer.scene.primitives.add(droneTileset);
      }

      status.textContent =
        'Tileset loaded. Zooming to point cloud...';

      message.textContent = 'Drone tiles loaded.';

      await viewer.zoomTo(droneTileset);

      status.textContent =
        'Full drone point cloud loaded successfully.';

      message.textContent =
        'Full drone point cloud visible. Use the globe controls to explore.';

    } catch (error) {
      console.error('Drone tiles failed to load:', error);

      status.textContent =
        'Could not load tiles. Check the browser console and tileset URL.';

      message.textContent =
        'Drone tiles failed to load.';

    } finally {
      button.disabled = false;
    }
  });

// Initialize Phase 4 Cesium globe
initializeGlobe();

// Initialize Phase 5 GeoAI site analysis
initializeSiteAnalysis();
