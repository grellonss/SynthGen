# Synthetic Data Generation Platform

This repository provides a full-stack platform to generate synthetic data from real-world sensor data using SDV models (e.g., CTGAN, GaussianCopula). The project supports real-time job processing, a YAML-based configuration system, and multiple output targets such as MongoDB, CSV files, and REST endpoints.

---

## Project Overview

This project features:
- Loading of real industrial sensor data
- Job creation via YAML configuration
- Synthetic data generation using SDV models
- Real-time progress tracking through WebSockets
- Multiple output targets (MongoDB, REST API, local CSV)
- Frontend interface built with React

---

## Running the Platform

### Prerequisites
- Python 3.10+
- MongoDB instance running locally
- Node.js 18+

### Step-by-step Setup

#### Backend
```bash
cd backend
python -m venv sdv-env
source sdv-env/bin/activate  # Windows: sdv-env\Scripts\activate
pip install -r requirements.txt
python run.py
```
The backend will be available at `http://localhost:5000`.

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`.

---

## Job Configuration (YAML)

Each job is created based on a YAML file specifying input sources, generation model, and output targets:

```yaml
config:
  input:
    sources:
      - type: rest_api
        url: http://localhost:5000/api/sensors
        method: GET
        format: json

  data_generation:
    plugin: synthetic_data_generator
    parameters:
      model: CTGAN
      num_samples: 200
      random_seed: 42
      augmentation: true

  output:
    targets:
      - type: database
        connection_string: "mongodb://localhost:27017"
        collection: sensor_data
      - type: rest_api
        url: http://localhost:5000/api/sensors/upload
        method: POST
        format: json
```

---

## Output Location

Each job saves the generated data to a CSV file in the following path:
```
backend/output/job_<job_id>.csv
```

---

## Architecture

- Flask backend with Socket.IO (`async_mode="threading"`)
- Real-time event communication for job control and progress updates
- MongoDB integration for data persistence
- SDV for synthetic data modeling
- Frontend built with React and Material UI

---

## WebSocket Events

- `start_job`: Start a new job from the frontend
- `job_status_update`: Backend sends status updates (Running, Completed, Error)
- `job_progress_update`: Optional progress event with percentage

---

## Repository Structure
```
backend/
├── app.py
├── run.py
├── api/
│   └── job_api.py
├── models/
│   ├── job.py
│   └── sensor_data.py
├── generate_synthetic_data.py
├── output/  # Output folder for CSV files

frontend/
├── src/
│   ├── pages/
│   │   └── Dashboard.js
│   ├── services/
│   │   ├── api.js
│   │   └── socket.js
```

---

## Status
- WebSocket-based communication implemented
- Real-time status updates and toast notifications
- CSV output and database storage integrated
- Full job lifecycle supported

---

## License
MIT License

---

## Author
Fabio Grelloni  
Email: fabio.grelloni@studenti.unicam.it
LinkedIn: https://www.linkedin.com/in/fabio-grelloni-9264211b4

