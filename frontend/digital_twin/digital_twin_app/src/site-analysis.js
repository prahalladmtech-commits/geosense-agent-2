
export function initializeSiteAnalysis() {
  const sidebar = document.querySelector('.sidebar');

  if (!sidebar) {
    console.error('GeoSense sidebar not found.');
    return;
  }

  // ==========================================================
  // PHASE 5 — GEOAI ANALYSIS INTERFACE
  // ==========================================================

  const panel = document.createElement('section');
  panel.className = 'info-card site-analysis-card';

  panel.innerHTML = `
    <p class="eyebrow">PHASE 5 · GEOAI ANALYSIS</p>
    <h3>Geospatial Analysis</h3>

    <label for="analysis-area">Select Study Area</label>

    <select id="analysis-area">
      <option value="kolkata">Kolkata — ML Site Suitability</option>
      <option value="bhopal">Bhopal — Drone Terrain Analysis</option>
    </select>

    <p class="analysis-note" id="analysis-description">
      Kolkata: ML-based site suitability using road, hospital
      and flood-risk features.
    </p>

    <label for="analysis-latitude">Latitude</label>

    <input
      id="analysis-latitude"
      type="number"
      step="any"
      value="22.5535"
      min="-90"
      max="90"
    >

    <label for="analysis-longitude">Longitude</label>

    <input
      id="analysis-longitude"
      type="number"
      step="any"
      value="88.3520"
      min="-180"
      max="180"
    >

    <button id="analyse-location" type="button">
      Analyse Location
    </button>

    <p id="analysis-status" aria-live="polite">
      Ready to analyse.
    </p>

    <div id="analysis-result" hidden>
      <p>Study area: <strong id="result-area"></strong></p>

      <div id="kolkata-results" hidden>
        <p>Opportunity score:
          <strong id="result-opportunity"></strong>
        </p>

        <p>Risk score:
          <strong id="result-risk"></strong>
        </p>

        <p>Distance to road:
          <strong id="result-road"></strong>
        </p>

        <p>Distance to hospital:
          <strong id="result-hospital"></strong>
        </p>

        <p>Flood risk:
          <strong id="result-flood"></strong>
        </p>

        <p>Verdict:
          <strong id="result-verdict"></strong>
        </p>

        <p class="analysis-note">SHAP explanation</p>

        <p>Road: <strong id="shap-road"></strong></p>
        <p>Hospital: <strong id="shap-hospital"></strong></p>
        <p>Flood: <strong id="shap-flood"></strong></p>
      </div>

      <div id="bhopal-results" hidden>
        <p>Ground elevation:
          <strong id="result-elevation"></strong>
        </p>

        <p>Nearest ground point:
          <strong id="result-distance"></strong>
        </p>

        <p>Ground points used:
          <strong id="result-ground-points"></strong>
        </p>

        <p>CRS:
          <strong id="result-crs"></strong>
        </p>

        <p>Data source:
          <strong id="result-source"></strong>
        </p>

        <p>Confidence:
          <strong id="result-confidence"></strong>
        </p>

        <p class="analysis-note">
          This is a nearest-ground-point elevation estimate,
          not a flood-risk prediction.
        </p>
      </div>
    </div>
  `;

  const footnote = sidebar.querySelector('.footnote');

  if (footnote) {
    footnote.before(panel);
  } else {
    sidebar.appendChild(panel);
  }

  // ==========================================================
  // INTERFACE ELEMENTS
  // ==========================================================

  const areaSelect = panel.querySelector('#analysis-area');

  const latitudeInput =
    panel.querySelector('#analysis-latitude');

  const longitudeInput =
    panel.querySelector('#analysis-longitude');

  const description =
    panel.querySelector('#analysis-description');

  const button =
    panel.querySelector('#analyse-location');

  const status =
    panel.querySelector('#analysis-status');

  const resultPanel =
    panel.querySelector('#analysis-result');

  const kolkataResults =
    panel.querySelector('#kolkata-results');

  const bhopalResults =
    panel.querySelector('#bhopal-results');

  // ==========================================================
  // API CONFIGURATION — KOLKATA ONLY
  // ==========================================================

  const configuredApiUrl =
    import.meta.env.VITE_API_BASE_URL;

  const apiBaseUrl = (
    configuredApiUrl || 'http://localhost:8003'
  ).replace(/\/+$/, '');

  const isPublicWebsite =
    window.location.hostname.endsWith('github.io');

  // ==========================================================
  // BHOPAL PUBLIC DATASET CONFIGURATION
  // ==========================================================

  const dataBaseUrl =
    `${import.meta.env.BASE_URL}data/`;

  const binaryUrl =
    `${dataBaseUrl}bhopal_ground_points.bin`;

  const metadataUrl =
    `${dataBaseUrl}bhopal_ground_metadata.json`;

  let bhopalDatasetPromise = null;

  // ==========================================================
  // UTILITY FUNCTIONS
  // ==========================================================

  const formatNumber = (value, decimals = 3) => {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return 'Not available';
    }

    return number.toFixed(decimals);
  };

  // ==========================================================
  // LOAD BHOPAL DATASET
  // ==========================================================

  async function loadBhopalDataset() {
    if (bhopalDatasetPromise) {
      return bhopalDatasetPromise;
    }

    bhopalDatasetPromise = (async () => {
      status.textContent =
        'Loading Bhopal drone terrain dataset...';

      const [binaryResponse, metadataResponse] =
        await Promise.all([
          fetch(binaryUrl),
          fetch(metadataUrl)
        ]);

      if (!binaryResponse.ok) {
        throw new Error(
          `Could not load terrain data: ${binaryResponse.status}`
        );
      }

      if (!metadataResponse.ok) {
        throw new Error(
          `Could not load terrain metadata: ${metadataResponse.status}`
        );
      }

      const [buffer, metadata] = await Promise.all([
        binaryResponse.arrayBuffer(),
        metadataResponse.json()
      ]);

      const pointCount = Number(metadata.point_count);

      if (
        !Number.isSafeInteger(pointCount) ||
        pointCount < 10
      ) {
        throw new Error(
          'Invalid Bhopal terrain metadata.'
        );
      }

      const expectedBytes = pointCount * 12;

      if (buffer.byteLength !== expectedBytes) {
        throw new Error(
          'Terrain dataset size does not match its metadata.'
        );
      }

      // Binary layout:
      // float32 latitude
      // float32 longitude
      // float32 elevation
      //
      // All values are little-endian.

      const view = new DataView(buffer);

      const points = new Float32Array(
        pointCount * 3
      );

      for (let i = 0; i < pointCount * 3; i++) {
        points[i] = view.getFloat32(
          i * 4,
          true
        );
      }

      if (!points.every(Number.isFinite)) {
        throw new Error(
          'Terrain dataset contains invalid values.'
        );
      }

      console.log(
        'Bhopal terrain dataset loaded:',
        pointCount,
        'ground points'
      );

      return {
        points,
        pointCount,
        metadata
      };
    })();

    try {
      return await bhopalDatasetPromise;
    } catch (error) {
      bhopalDatasetPromise = null;
      throw error;
    }
  }

  // ==========================================================
  // BHOPAL NEAREST GROUND POINT ANALYSIS
  // ==========================================================

  async function analyzeBhopal(latitude, longitude) {
    const dataset = await loadBhopalDataset();

    const metadata = dataset.metadata;
    const points = dataset.points;

    // Check actual survey bounding box.
    if (
      latitude < metadata.latitude_min ||
      latitude > metadata.latitude_max ||
      longitude < metadata.longitude_min ||
      longitude > metadata.longitude_max
    ) {
      throw new Error(
        'Location is outside the actual Bhopal drone survey coverage.'
      );
    }

    // Convert small-area geographic coordinate differences
    // into approximate local distances in metres.
    //
    // The study area is approximately 223 m × 233 m.
    // This local distance approximation is suitable for
    // nearest-point selection within this small survey area.

    const meanLatitude =
      (latitude + metadata.latitude_min +
        metadata.latitude_max) / 3;

    const metresPerDegreeLatitude = 110540;

    const metresPerDegreeLongitude =
      111320 * Math.cos(
        meanLatitude * Math.PI / 180
      );

    let minimumDistanceSquared = Infinity;
    let nearestIndex = -1;

    for (let i = 0; i < dataset.pointCount; i++) {
      const offset = i * 3;

      const pointLatitude = points[offset];
      const pointLongitude = points[offset + 1];

      const dx =
        (pointLongitude - longitude) *
        metresPerDegreeLongitude;

      const dy =
        (pointLatitude - latitude) *
        metresPerDegreeLatitude;

      const distanceSquared = dx * dx + dy * dy;

      if (distanceSquared < minimumDistanceSquared) {
        minimumDistanceSquared = distanceSquared;
        nearestIndex = i;
      }
    }

    if (nearestIndex < 0) {
      throw new Error(
        'No valid ground point was found.'
      );
    }

    const elevation =
      points[nearestIndex * 3 + 2];

    const distance =
      Math.sqrt(minimumDistanceSquared);

    return {
      latitude,
      longitude,

      ground_elevation_m:
        elevation,

      nearest_ground_point_distance_m:
        distance,

      ground_points_used:
        dataset.pointCount,

      crs:
        'EPSG:4326 coordinates; source elevations from EPSG:32643',

      data_source:
        'Bhopal drone survey LAS, LAS classification 2',

      confidence_warning:
        distance <= 10
          ? 'Nearest ground point within 10 m.'
          : 'Nearest ground point is more than 10 m away. Interpret with caution.'
    };
  }

  // ==========================================================
  // STUDY AREA SELECTION
  // ==========================================================

  areaSelect.addEventListener('change', () => {
    resultPanel.hidden = true;

    if (areaSelect.value === 'bhopal') {
      latitudeInput.value = '23.25499';
      longitudeInput.value = '77.45750';

      description.textContent =
        'Bhopal: Browser-based ground elevation analysis using your drone survey point cloud.';

      status.textContent =
        'Bhopal terrain analysis ready.';

    } else {
      latitudeInput.value = '22.5535';
      longitudeInput.value = '88.3520';

      description.textContent =
        'Kolkata: ML-based site suitability using road, hospital and flood-risk features.';

      status.textContent =
        'Kolkata ML analysis selected.';
    }
  });

  // ==========================================================
  // ANALYSE LOCATION
  // ==========================================================

  button.addEventListener('click', async () => {
    const latitude =
      Number(latitudeInput.value);

    const longitude =
      Number(longitudeInput.value);

    const area = areaSelect.value;

    // Validate geographic coordinates.

    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      status.textContent =
        'Enter valid latitude and longitude.';

      resultPanel.hidden = true;
      return;
    }

    button.disabled = true;
    resultPanel.hidden = true;

    status.textContent =
      'Analysing location...';

    try {
      let result;
      let studyArea;

      // ======================================================
      // BHOPAL — PUBLIC BROWSER-BASED TERRAIN ANALYSIS
      // ======================================================

      if (area === 'bhopal') {
        result = await analyzeBhopal(
          latitude,
          longitude
        );

        studyArea =
          'Bhopal Drone Terrain Analysis';

        kolkataResults.hidden = true;
        bhopalResults.hidden = false;

        panel.querySelector(
          '#result-elevation'
        ).textContent =
          `${formatNumber(result.ground_elevation_m)} m`;

        panel.querySelector(
          '#result-distance'
        ).textContent =
          `${formatNumber(result.nearest_ground_point_distance_m)} m`;

        panel.querySelector(
          '#result-ground-points'
        ).textContent =
          result.ground_points_used.toLocaleString();

        panel.querySelector(
          '#result-crs'
        ).textContent =
          result.crs;

        panel.querySelector(
          '#result-source'
        ).textContent =
          result.data_source;

        panel.querySelector(
          '#result-confidence'
        ).textContent =
          result.confidence_warning;

      } else {
        // ====================================================
        // KOLKATA — EXISTING ML BACKEND
        // ====================================================

        if (
          isPublicWebsite &&
          !configuredApiUrl
        ) {
          throw new Error(
            'Kolkata public ML API is not configured. Bhopal terrain analysis is available directly from the public dataset.'
          );
        }

        const endpoint =
          `${apiBaseUrl}/api/score-location`;

        const response = await fetch(endpoint, {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json'
          },

          body: JSON.stringify({
            latitude,
            longitude
          })
        });

        const data =
          await response.json().catch(() => null);

        if (!response.ok) {
          throw new Error(
            data?.detail ||
            `Kolkata API error: ${response.status}`
          );
        }

        if (!data || !data.result) {
          throw new Error(
            'Invalid Kolkata backend response.'
          );
        }

        result = data.result;

        const features = result.features;
        const shap = result.shap_explanation;

        if (!features || !shap) {
          throw new Error(
            'Kolkata response is missing features or SHAP explanation.'
          );
        }

        studyArea =
          data.study_area || 'Kolkata';

        kolkataResults.hidden = false;
        bhopalResults.hidden = true;

        panel.querySelector(
          '#result-opportunity'
        ).textContent =
          result.opportunity_score ?? 'Not available';

        panel.querySelector(
          '#result-risk'
        ).textContent =
          result.risk_score ?? 'Not available';

        panel.querySelector(
          '#result-road'
        ).textContent =
          `${formatNumber(features.dist_road_m)} m`;

        panel.querySelector(
          '#result-hospital'
        ).textContent =
          `${formatNumber(features.dist_hospital_m)} m`;

        panel.querySelector(
          '#result-flood'
        ).textContent =
          features.flood_risk ?? 'Not available';

        panel.querySelector(
          '#result-verdict'
        ).textContent =
          result.verdict ?? 'Not available';

        panel.querySelector(
          '#shap-road'
        ).textContent =
          shap.dist_road_m ?? 'Not available';

        panel.querySelector(
          '#shap-hospital'
        ).textContent =
          shap.dist_hospital_m ?? 'Not available';

        panel.querySelector(
          '#shap-flood'
        ).textContent =
          shap.flood_risk ?? 'Not available';
      }

      // ======================================================
      // DISPLAY RESULTS
      // ======================================================

      panel.querySelector(
        '#result-area'
      ).textContent = studyArea;

      resultPanel.hidden = false;

      status.textContent =
        'Analysis completed successfully.';

    } catch (error) {
      console.error(
        'GeoSense Phase 5 analysis error:',
        error
      );

      status.textContent =
        `Analysis failed: ${error.message}`;

    } finally {
      button.disabled = false;
    }
  });

  console.log(
    'GeoSense Phase 5 site-analysis module initialized.'
  );

  console.log(
    'Bhopal terrain source:',
    binaryUrl
  );

  console.log(
    'Kolkata API:',
    apiBaseUrl
  );
}
