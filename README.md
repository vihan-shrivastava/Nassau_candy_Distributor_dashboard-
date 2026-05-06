# Nassau_candy_Distributor_dashboard-

## 🚀 Project Overview

This project delivers an interactive Streamlit dashboard for analyzing shipping efficiency at a fictional confectionery distributor. Using shipment order data, it compares route performance, spotlights geographic bottlenecks, and evaluates shipping modes across US regions.

## 🔍 What the Dashboard Shows

- **Route efficiency rankings** from factories to customer regions
- **US state heatmap** of average lead time
- **Shipping mode comparison** with distribution analysis
- **Route drill-down** with state-level and order timeline detail
- **Dynamic filtering** by date, state/region, ship mode, and lead-time threshold

## 📁 Project Files

- `app.py` — main Streamlit dashboard code
- `requirements.txt` — pinned dependency versions for reproducibility
- `research_report.txt` — complete research report and project analysis
- `Nassau Candy Distributor.csv` — dataset for the app

## 🧰 Tech Stack

- Python
- pandas
- numpy
- Streamlit
- Plotly

## ✅ Local Setup

1. Activate your Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Launch the app:

```bash
streamlit run app.py
```

4. Open the local URL shown in the terminal.

## ☁️ Deployment Notes for Streamlit Cloud

- Push this repository to GitHub.
- Make sure `requirements.txt` and the CSV dataset are included.
- Do not use local paths such as `C:\Users\...` in the app code.

## 📌 Key Insights

- **Top-performing routes** and least efficient routes are identified
- **High-risk bottleneck regions** are highlighted by lead time
- **Standard shipping** often performs best, while expedited modes can be inconsistent
- **Congestion-prone regions** are detected using volume + lead time criteria

## 🔗 Additional Documentation

See `research_report.txt` for the full analysis, including methodology, findings, limitations, and future work.
