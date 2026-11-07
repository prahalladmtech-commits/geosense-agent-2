
export function initializeSiteAnalysis() {
  const sidebar = document.querySelector('.sidebar');

  if (!sidebar) {
    console.error('GeoSense sidebar not found.');
    return;
  }

  // Create Phase 5 analysis panel
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
      Backend: Not connected yet.
    </p>

    <div id="analysis-result" hidden>
      <p>Study area: <strong id="result-area"></strong></p>

      <div id="kolkata-results" hidden>
        <p>Opportunity score: <strong id="result-opportunity"></strong></p>
        <p>Risk score: <strong id="result-risk"></strong></p>
        <p>Distance to road: <strong id="result-road"></strong></p>
        <p>Distance to hospital: <strong id="result-hospital"></strong></p>
        <p>Flood risk: <strong id="result-flood"></strong></p>
        <p>Verdict: <strong id="result-verdict"></strong></p>

        <p class="analysis-note">SHAP explanation</p>
        <p>Road: <strong id="shap-road"></strong></p>
        <p>Hospital: <strong id="shap-hospital"></strong></p>
        <p>Flood: <strong id="shap-flood"></strong></p>
      </div>

      <div id="bhopal-results" hidden>
        <p>Ground elevation: <strong id="result-elevation"></strong></p>
        <p>Nearest ground point: <strong id="result-distance"></strong></p>
        <p>Ground points used: <strong id="result-ground-points"></strong></p>
        <p>CRS: <strong id="result-crs"></strong></p>
        <p>Data source: <strong id="result-source"></strong></p>
        <p>Confidence: <strong id="result-confidence"></strong></p>

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

  // Get interface elements
  const areaSelect = panel.querySelector('#analysis-area');
  const latitudeInput = panel.querySelector('#analysis-latitude');
  const longitudeInput = panel.querySelector('#analysis-longitude');
  const description = panel.querySelector('#analysis-description');
  const button = panel.querySelector('#analyse-location');
  const status = panel.querySelector('#analysis-status');
  const resultPanel = panel.querySelector('#analysis-result');

  const kolkataResults = panel.querySelector('#kolkata-results');
  const bhopalResults = panel.querySelector('#bhopal-results');

  // Backend configuration:
  // Local development: http://localhost:8003
  // Public deployment: configure VITE_API_BASE_URL in .env.production
  const configuredApiUrl = import.meta.env.VITE_API_BASE_URL;

  const apiBaseUrl = (
    configuredApiUrl || 'http://localhost:8003'
  ).replace(/\/+$/, '');

  const isPublicWebsite =
    window.location.hostname.endsWith('github.io');

  const formatNumber = (value, decimals = 3) => {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return 'Not available';
    }

    return number.toFixed(decimals);
  };

  // Update selected study area
  areaSelect.addEventListener('change', () => {
    resultPanel.hidden = true;

    if (areaSelect.value === 'bhopal') {
      latitudeInput.value = '23.25499';
      longitudeInput.value = '77.45750';

      description.textContent =
        'Bhopal: Ground elevation from your drone survey point cloud.';
    } else {
      latitudeInput.value = '22.5535';
      longitudeInput.value = '88.3520';

      description.textContent =
        'Kolkata: ML-based site suitability using road, hospital and flood-risk features.';
    }

    status.textContent = 'Study area changed. Ready to analyse.';
  });

  // Analyse selected location
  button.addEventListener('click', async () => {
    const latitude = Number(latitudeInput.value);
    const longitude = Number(longitudeInput.value);
    const area = areaSelect.value;

    // Validate coordinates
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

    // Validate Bhopal survey coverage
    if (
      area === 'bhopal' &&
      (
        latitude < 23.2539 ||
        latitude > 23.2561 ||
        longitude < 77.4563 ||
        longitude > 77.4587
      )
    ) {
      status.textContent =
        'Coordinates are outside the Bhopal drone survey coverage.';

      resultPanel.hidden = true;
      return;
    }

    // Prevent repeated requests
    button.disabled = true;
    resultPanel.hidden = true;
    status.textContent = 'Analysing location...';

    try {
      // Do not attempt localhost from the public website
      if (
        isPublicWebsite &&
        !configuredApiUrl
      ) {
        throw new Error(
          'Public GeoSense API is not configured yet. The analysis backend is currently available locally only.'
        );
      }

      // Select API endpoint
      const endpoint = area === 'bhopal'
        ? `${apiBaseUrl}/api/bhopal/terrain`
        : `${apiBaseUrl}/api/score-location`;

      // Send request
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude,
          longitude,
        }),
      });

      // Read response safely
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail || `API error: ${response.status}`
        );
      }

      if (!data || !data.result) {
        throw new Error(
          'The backend returned an invalid response.'
        );
      }

      const result = data.result;

      // Display study area
      panel.querySelector('#result-area').textContent =
        data.study_area || area;

      // Kolkata ML site suitability
      if (area === 'kolkata') {
        const features = result.features;
        const shap = result.shap_explanation;

        if (!features || !shap) {
          throw new Error(
            'Kolkata response is missing features or SHAP explanation.'
          );
        }

        kolkataResults.hidden = false;
        bhopalResults.hidden = true;

        panel.querySelector('#result-opportunity').textContent =
          result.opportunity_score ?? 'Not available';

        panel.querySelector('#result-risk').textContent =
          result.risk_score ?? 'Not available';

        panel.querySelector('#result-road').textContent =
          `${formatNumber(features.dist_road_m)} m`;

        panel.querySelector('#result-hospital').textContent =
          `${formatNumber(features.dist_hospital_m)} m`;

        panel.querySelector('#result-flood').textContent =
          features.flood_risk ?? 'Not available';

        panel.querySelector('#result-verdict').textContent =
          result.verdict ?? 'Not available';

        panel.querySelector('#shap-road').textContent =
          shap.dist_road_m ?? 'Not available';

        panel.querySelector('#shap-hospital').textContent =
          shap.dist_hospital_m ?? 'Not available';

        panel.querySelector('#shap-flood').textContent =
          shap.flood_risk ?? 'Not available';

      } else {
        // Bhopal drone terrain analysis
        kolkataResults.hidden = true;
        bhopalResults.hidden = false;

        panel.querySelector('#result-elevation').textContent =
          `${formatNumber(result.ground_elevation_m)} m`;

        panel.querySelector('#result-distance').textContent =
          `${formatNumber(result.nearest_ground_point_distance_m)} m`;

        panel.querySelector('#result-ground-points').textContent =
          Number(result.ground_points_used).toLocaleString();

        panel.querySelector('#result-crs').textContent =
          result.crs ?? 'Not available';

        panel.querySelector('#result-source').textContent =
          result.data_source ?? 'Not available';

        panel.querySelector('#result-confidence').textContent =
          result.confidence_warning ||
          'Nearest ground point within 10 m.';
      }

      resultPanel.hidden = false;

      status.textContent =
        'Analysis completed successfully.';

    } catch (error) {
      console.error('GeoSense site analysis failed:', error);

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
    'GeoSense API endpoint:',
    apiBaseUrl
  );
}
