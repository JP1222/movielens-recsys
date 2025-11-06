# MovieLens Recommender System Report Template

> **Note:** This Markdown outline is designed to expand into ~10 pages once figures and tables are embedded. Each section includes guidance on the expected content.

---

## 1. Title Page
- Project title, course, date.
- Team members and roles (practical tasks + AI assistance summary).

## 2. Abstract (0.5 page)
- Concise overview of goals, datasets, methods, and main findings.

## 3. Introduction (1 page)
- Motivation for movie recommendation systems.
- Dataset overview: MovieLens 1M (core) and 32M (extension).
- Research questions and success criteria.

## 4. Related Work (0.5 page)
- Brief survey of collaborative filtering and content-based systems.
- Positioning of this project relative to classic baselines.

## 5. Data Preparation (1 page)
- Describe raw data schema and preprocessing (parsing, cleaning).
- Leave-one-out split rationale (temporal order).
- Overview of generated artifacts (`pop_score.parquet`, `item_neighbors.npz`, etc.).
- Table summarizing dataset statistics (users, items, sparsity).

## 6. Methods (2 pages)
- **Popularity Model:** Bayesian smoothing, parameter choices.
- **Item-Based Collaborative Filtering:** similarity computation, pruning, neighborhood size.
- **Content-Based Model:** TF-IDF pipeline, feature engineering, normalization.
- **System Architecture:** Figure showing offline pipeline → FastAPI → React UI.

## 7. Experimental Setup (0.5 page)
- Hardware specs, environment versions.
- Evaluation protocol (Precision@10 / Recall@10 / NDCG@10).
- Baselines and hyperparameters.

## 8. Results & Visualization (2 pages)
- Table: Metrics comparison across algorithms on MovieLens 1M.
- Figure: Bar chart of Precision/Recall/NDCG (export from `scripts/visualize.plot_metric_comparison`).
- Discussion of per-user qualitative insights (case study).
- Extension experiment summary on 32M (runtime, memory).

## 9. Scalability Analysis (1 page)
- Figure: Runtime vs. dataset size curve (`plot_runtime_scaling`).
- Discussion on bottlenecks, parallelism opportunities, and artifact sizes.

## 10. Conclusion & Future Work (1 page)
- Key takeaways for each method.
- Limitations (cold-start, novelty).
- Planned enhancements (e.g., hybrid models, implicit feedback handling).
- **Human vs. AI Contributions:** Table documenting tasks delegated to team vs. AI agents.

## 11. References (0.5 page)
- Cite datasets, libraries, and relevant research papers (APA/IEEE style).

## Appendix (optional)
- Extended tables, hyperparameter sweeps, or code snippets.

---

### Usage Tips
- Export figures to `docs/figures/`.
- Convert to PDF/Word via `pandoc` if required:  
  `pandoc report_template.md -o movielens_report.pdf --from markdown --template eisvogel`
- Keep raw data analysis notebooks in `docs/notebooks/` for reproducibility.

