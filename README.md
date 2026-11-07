\# GeoSense Agent 2.0

\### AI-Powered Geospatial Intelligence and Drone-Based Digital Twin Platform



<p align="center">

&#x20; <a href="https://prahalladmtech-commits.github.io/geosense-agent-2/">

&#x20;   <strong>🌐 View Live Demo</strong>

&#x20; </a>

&#x20; \&nbsp; | \&nbsp;

&#x20; <a href="https://github.com/prahalladmtech-commits/geosense-agent-2">

&#x20;   <strong>💻 GitHub Repository</strong>

&#x20; </a>

</p>



\## Overview



\*\*GeoSense Agent 2.0\*\* is a geospatial intelligence platform integrating Geographic Information Systems (GIS), Remote Sensing, Machine Learning, UAV photogrammetry, LiDAR point-cloud processing, and 3D visualization.



The platform combines location-based site assessment with drone-derived terrain analysis and an interactive Digital Twin environment.



\## Key Features



\### 1. Bhopal Drone Digital Twin

\- Interactive 3D visualization of drone-derived point-cloud data.

\- 3D Tiles integration for point-cloud exploration.

\- UAV survey data processing and visualization.

\- Browser-based terrain analysis using classified ground points.

\- Ground elevation estimation from the drone survey dataset.

\- Survey coverage validation.



\### 2. Kolkata GeoAI Site Assessment

\- GIS-based location analysis.

\- Road and hospital proximity analysis.

\- Machine Learning-based site suitability scoring.

\- SHAP-based model explainability.

\- FastAPI backend for location-based analysis.



\### 3. Geospatial Data Processing

\- OpenStreetMap data integration.

\- Spatial database management using PostgreSQL and PostGIS.

\- Coordinate reference system transformations.

\- Geospatial feature engineering.

\- Point-cloud processing and terrain extraction.



\## Technology Stack



| Category | Technologies |

|---|---|

| GIS | ArcGIS, ArcGIS Pro, QGIS |

| Remote Sensing | Google Earth Engine |

| Programming | Python, JavaScript |

| Machine Learning | Scikit-learn, SHAP |

| Backend | FastAPI, Uvicorn |

| Database | PostgreSQL, PostGIS |

| Point Cloud | LAS/LAZ, PDAL, Open3D |

| 3D Visualization | CesiumJS, 3D Tiles |

| Frontend | HTML, CSS, JavaScript, Vite |

| Version Control | Git, GitHub |

| Deployment | GitHub Pages, GitHub Actions |



\## System Architecture



```text

Geospatial Data Sources

&#x20;       |

&#x20;       v

GIS / Remote Sensing / UAV Data

&#x20;       |

&#x20;       v

Geospatial Processing

&#x20;       |

&#x20;       +----------------------+

&#x20;       |                      |

&#x20;       v                      v

Kolkata Site Assessment   Bhopal Drone Survey

&#x20;       |                      |

&#x20;       v                      v

Machine Learning          Point Cloud Processing

&#x20;       |                      |

&#x20;       v                      v

FastAPI Backend           Terrain Analysis

&#x20;       |                      |

&#x20;       +-----------+----------+

&#x20;                   |

&#x20;                   v

&#x20;         Geospatial Visualization

&#x20;                   |

&#x20;                   v

&#x20;             GeoSense Agent

```



\## Live Demo



\*\*Public application:\*\*  

https://prahalladmtech-commits.github.io/geosense-agent-2/



\*\*Bhopal 3D Tiles dataset:\*\*  

https://prahalladmtech-commits.github.io/geosense-agent-2/tiles/drone\_fixed/tileset.json



The public demo currently provides the Bhopal Digital Twin and browser-based terrain analysis. The Kolkata FastAPI backend has been tested locally and is not yet publicly deployed.



\## Project Structure



```text

GeoSense\_Agent/

│

├── backend/

│   └── app/

│       ├── main.py

│       └── services/

│

├── src/

│   ├── phase1\_ml/

│   ├── phase2\_dl/

│   ├── phase3\_lidar/

│   └── phase4\_agent/

│

├── frontend/

│   └── digital\_twin/

│       └── digital\_twin\_app/

│

├── data/

│   └── satellite/

│

├── models/

│   └── saved/

│

├── docs/

├── README.md

└── .gitignore

```



\## Local Setup



\### Requirements

\- Python 3.11

\- Node.js and npm

\- PostgreSQL with PostGIS

\- Git



\### Backend



Activate the project environment:



```bash

conda activate geosense

```



Install backend dependencies:



```bash

pip install -r backend/requirements.txt

```



Configure your local environment variables in `.env` using your own database credentials.



Start the backend:



```bash

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8010

```



API documentation:



```text

http://127.0.0.1:8010/docs

```



\### Frontend



Navigate to the Digital Twin application:



```bash

cd frontend/digital\_twin/digital\_twin\_app

```



Install dependencies:



```bash

npm install

```



Start the development server:



```bash

npm run dev

```



Build for production:



```bash

npm run build

```



\## Data and Research



The project works with:

\- UAV-derived LAS/LAZ point clouds.

\- Classified ground points.

\- OpenStreetMap road and point-of-interest datasets.

\- Satellite remote sensing data.

\- Spatial databases and geospatial vector data.



Large datasets, model files, database credentials, and private configuration files are not included in the public repository.



\## Development Status



\- \[x] GIS and spatial database integration

\- \[x] Machine Learning site assessment

\- \[x] SHAP-based model explainability

\- \[x] UAV point-cloud processing

\- \[x] Bhopal Drone Digital Twin

\- \[x] Browser-based Bhopal terrain analysis

\- \[x] Public GitHub Pages deployment

\- \[x] GitHub Actions Pages deployment workflow

\- \[x] Local FastAPI backend testing

\- \[ ] Public Kolkata backend deployment

\- \[ ] Complete portfolio documentation



\## Author



\*\*Prahallad Barman\*\*  

M.Tech. Geoinformatics  

University of Madras



\*\*Areas of Interest:\*\* GIS, Remote Sensing, Geospatial Artificial Intelligence, UAV Photogrammetry, LiDAR, Spatial Analysis, and Environmental Applications.



\*\*LinkedIn:\*\* https://linkedin.com/in/prahalladmtech



\---



\*GeoSense Agent 2.0 — Integrating geospatial intelligence, machine learning, and drone-based Digital Twin technology.\*

