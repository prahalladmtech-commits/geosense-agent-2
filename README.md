\# GeoSense Agent 2.0



\### AI-Powered Geospatial Intelligence and Drone-Based Digital Twin Platform



<p align="center">

&#x20; <a href="https://prahalladmtech-commits.github.io/geosense-agent-2/">

&#x20;   <strong>🌐 Live Demo</strong>

&#x20; </a>

&#x20; \&nbsp; | \&nbsp;

&#x20; <a href="https://github.com/prahalladmtech-commits/geosense-agent-2">

&#x20;   <strong>💻 GitHub Repository</strong>

&#x20; </a>

&#x20; \&nbsp; | \&nbsp;

&#x20; <a href="https://linkedin.com/in/prahalladmtech">

&#x20;   <strong>LinkedIn</strong>

&#x20; </a>

</p>



\---



\## Overview



\*\*GeoSense Agent 2.0\*\* is an integrated geospatial intelligence platform combining Geographic Information Systems (GIS), Remote Sensing, Machine Learning, UAV photogrammetry, LiDAR point-cloud processing, spatial databases, and 3D visualization.



The project brings together two geospatial applications:



\- \*\*Kolkata:\*\* Machine Learning-based site suitability assessment using spatial features.

\- \*\*Bhopal:\*\* Drone-based Digital Twin with interactive 3D point-cloud visualization and terrain elevation analysis.



The objective is to demonstrate how geospatial technologies, machine learning, and UAV-derived data can support spatial analysis and decision-making.



\## Project Screenshots



\### Bhopal Drone Digital Twin



Interactive 3D visualization of the drone-derived point cloud from the Bhopal survey.



!\[Bhopal Drone Digital Twin](docs/screenshots/bhopal-digital-twin.png)



\*Drone survey visualization using CesiumJS and 3D Tiles.\*



\## Key Features



\### 1. Bhopal Drone Digital Twin



\- Interactive 3D visualization of drone-derived point-cloud data.

\- 3D Tiles integration for point-cloud exploration.

\- UAV survey data processing and visualization.

\- Browser-based terrain analysis using classified ground points.

\- Ground elevation estimation from the drone survey dataset.

\- Survey coverage validation to prevent analysis outside the actual survey area.



\### 2. Kolkata GeoAI Site Assessment



\- GIS-based location analysis.

\- Road and hospital proximity analysis.

\- Machine Learning-based site suitability scoring.

\- SHAP-based model explainability.

\- FastAPI backend for location-based analysis.

\- PostgreSQL and PostGIS spatial database integration.



\### 3. Geospatial Data Processing



\- OpenStreetMap data integration.

\- Spatial database management.

\- Coordinate reference system transformations.

\- Geospatial feature engineering.

\- LiDAR and point-cloud processing.

\- Classified ground-point extraction.



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

&#x20;                GEOSPATIAL DATA SOURCES

&#x20;                          |

&#x20;                          v

&#x20;            GIS / REMOTE SENSING / UAV DATA

&#x20;                          |

&#x20;                          v

&#x20;               GEOSPATIAL PROCESSING

&#x20;                          |

&#x20;              +-----------+-----------+

&#x20;              |                       |

&#x20;              v                       v

&#x20;       KOLKATA APPLICATION      BHOPAL APPLICATION

&#x20;              |                       |

&#x20;              v                       v

&#x20;      Spatial Feature          Drone Point Cloud

&#x20;        Engineering              Processing

&#x20;              |                       |

&#x20;              v                       v

&#x20;      Machine Learning          Ground Point

&#x20;       Site Assessment           Extraction

&#x20;              |                       |

&#x20;              v                       v

&#x20;       SHAP Explainability      Terrain Analysis

&#x20;              |                       |

&#x20;              v                       v

&#x20;         FastAPI Backend       CesiumJS / 3D Tiles

&#x20;              |                       |

&#x20;              +-----------+-----------+

&#x20;                          |

&#x20;                          v

&#x20;                GEOSENSE AGENT 2.0

```



\## Live Demo



\*\*Public application:\*\*



https://prahalladmtech-commits.github.io/geosense-agent-2/



\*\*Bhopal 3D Tiles dataset:\*\*



https://prahalladmtech-commits.github.io/geosense-agent-2/tiles/drone\_fixed/tileset.json



The public GitHub Pages application provides the Bhopal Digital Twin and browser-based terrain analysis.



\*\*Backend deployment status:\*\* The Kolkata FastAPI backend has been tested locally. Public deployment is still pending.



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

│   └── screenshots/

│       └── bhopal-digital-twin.png

│

├── README.md

└── .gitignore

```



\## Local Installation and Setup



\### Requirements



\- Python 3.11

\- Node.js and npm

\- PostgreSQL with PostGIS

\- Git

\- Conda (recommended)



\### 1. Clone the Repository



```bash

git clone https://github.com/prahalladmtech-commits/geosense-agent-2.git

cd geosense-agent-2

```



\### 2. Activate the Python Environment



```bash

conda activate geosense

```



Create the environment and install dependencies if setting up on a new machine.



\### 3. Install Backend Dependencies



```bash

pip install -r backend/requirements.txt

```



Configure your local `.env` file with your own database connection settings. Never publish database credentials or API keys.



\### 4. Start the Backend



From the project root:



```bash

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8010

```



API documentation:



http://127.0.0.1:8010/docs



\### 5. Start the Frontend



Open another terminal:



```bash

cd frontend/digital\_twin/digital\_twin\_app

```



Install frontend dependencies:



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

\- Drone-derived 3D Tiles datasets.



Large datasets, model files, database credentials, and private configuration files are not included in the public repository unless explicitly provided for public distribution.



\## Development Status



\- \[x] GIS and spatial database integration

\- \[x] Machine Learning site assessment

\- \[x] SHAP-based model explainability

\- \[x] UAV point-cloud processing

\- \[x] Bhopal Drone Digital Twin

\- \[x] Browser-based Bhopal terrain analysis

\- \[x] Public Bhopal 3D Tiles deployment

\- \[x] Public GitHub Pages deployment

\- \[x] GitHub Actions Pages deployment workflow

\- \[x] Local FastAPI backend testing

\-

\## Author



\*\*Prahallad Barman\*\*



M.Tech. Geoinformatics  

University of Madras



\*\*Areas of Interest:\*\* GIS, Remote Sensing, Geospatial Artificial Intelligence, UAV Photogrammetry, LiDAR, Spatial Analysis, and Environmental Applications.



\*\*LinkedIn:\*\* https://linkedin.com/in/prahalladmtech



\*\*GitHub:\*\* https://github.com/prahalladmtech-commits

\---



\*GeoSense Agent 2.0 — Integrating geospatial intelligence, machine learning, and drone-based Digital Twin technology.\*

