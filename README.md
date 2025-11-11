# MovieLens Recommendation System

An end-to-end stack for preparing, serving, and visualizing MovieLens movie recommendations built on the MovieLens dataset.

## Features
- Offline jobs (Python) create Parquet/NPZ artifacts for popularity scoring, item-based collaborative filtering, content similarity, user history, and movie metadata.
- FastAPI backend loads artifacts into memory and exposes REST endpoints for popular, personalized, and title-based recommendations.
- Vite + React interface shows Popular and For You tabs plus a title search panel that calls the backend.
- Evaluation helpers (Precision@10 / Recall@10 / NDCG@10) and a ready-to-fill 10-page report template.

### Feature ↔ Algorithm Map
- **Popular tab / `GET /recommend/popular`** → Bayesian-smoothed popularity ranking computed offline.
- **For You tab / `GET /recommend/itemcf`** → Item-based collaborative filtering using cosine similarities between movies.
- **Recommend by Titles / `POST /recommend/by-titles`** → Content-based retrieval via TF-IDF features on titles and genres.

## Repository Layout
```
movielens-recsys/
|-- backend/              # FastAPI application
|-- data/                 # Raw datasets and generated artifacts
|-- docs/                 # Report template and documentation assets
|-- frontend/             # Vite + React client
|-- scripts/              # Offline pipeline, evaluation, visualization
`-- README.md
```

## Prerequisites
- Python 3.10+
- Node.js 18+
- PowerShell users may need to relax the execution policy when activating virtualenvs or running `npm`:  
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## Setup
```bash
# 1. Position inside the project
cd movielens-recsys

# 2. Create & activate a virtual environment
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell (if needed: Set-ExecutionPolicy -Scope Process Bypass)
.venv\Scripts\Activate.ps1

# 3. Install Python dependencies
pip install -r scripts/requirements.txt -r backend/requirements.txt
```

## Prepare MovieLens Data
1. Download MovieLens 1M from [GroupLens](https://grouplens.org/datasets/movielens/) and extract to `data/ml-1m/`, resulting in files such as:
   ```
   data/ml-1m/ratings.dat
   data/ml-1m/movies.dat
   data/ml-1m/users.dat
   ```
2. (Optional) Download MovieLens 32M into `data/ml-32m/` for large-scale experiments.

## Generate Offline Artifacts
```powershell
python -m scripts.cli `
  --ratings data/ml-1m/ratings.dat `
  --movies data/ml-1m/movies.dat `
  --output-dir data/artifacts/ml-1m
```
Artifacts produced:
- `pop_score.parquet`
- `item_neighbors.npz` + `item_index.json`
- `content_neighbors.npz` + `content_index.json`
- `user_history.parquet`
- `movie_meta.parquet`

Adjustments:
- `--topk 200` widens the neighbor list.
- `--min-rating 3.5` changes the positive rating threshold.
- `--smoothing 25` tweaks Bayesian popularity smoothing.

## Start the FastAPI Backend
```bash
export RECSYS_ARTIFACT_DIR=$(pwd)/data/artifacts/ml-1m     # PowerShell: $env:RECSYS_ARTIFACT_DIR = Resolve-Path "data/artifacts/ml-1m"
python -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```
Available endpoints:
- `GET /recommend/popular?k=10`
- `GET /recommend/itemcf?user_id=123&k=10`
- `POST /recommend/by-titles?k=10` with body `{"titles": ["Toy Story", "The Matrix"]}`

Override individual artifact paths via env vars such as `RECSYS_POPULARITY_PATH`, `RECSYS_ITEM_NEIGHBORS_PATH`, etc.

## Start the React Frontend
```bash
cd frontend
npm install          # run once
npm run dev
```
Visit `http://localhost:5173`. The Vite dev server proxies API calls to `http://localhost:8000` (configured in `vite.config.ts`).

### Movie posters (TMDB)
- Create `frontend/.env.local` (already gitignored) and add:
  ```
  VITE_TMDB_API_KEY=your-tmdb-api-key
  VITE_TMDB_BEARER_TOKEN=your-tmdb-read-token
  ```
- Restart `npm run dev` so the client can fetch poster artwork from TMDB.

## Validation & Evaluation
- Smoke test the API: `curl http://localhost:8000/recommend/popular?k=5`
- Front-end linting: `npm run lint`
- Compute Precision/Recall/NDCG using `scripts/evaluate.py`; visualize metrics and runtime scaling with `scripts/visualize.py`.

## Scaling to MovieLens 32M
1. Point the pipeline CLI to the 32M CSV files.
2. Increase `--topk` if you need broader neighborhoods.
3. Set `RECSYS_ARTIFACT_DIR` to the new artifacts before restarting FastAPI.
4. Capture runtime statistics with `plot_runtime_scaling` for documentation.

## Documentation & Next Steps
- `docs/report_template.md` contains a 10-page markdown outline covering Introduction → Conclusion (with a human vs. AI contribution section).
- Suggested follow-ups:
  1. Blend popularity and item-CF scores for hybrid ranking.
  2. Persist evaluation snapshots (JSON/Parquet) for trend tracking.
  3. Dockerize FastAPI + React for deployment.

---
Happy recommending! Adapt the pipeline to other datasets by modifying the loaders in `scripts/data_pipeline.py`.
