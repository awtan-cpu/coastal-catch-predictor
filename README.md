# Coastal Catch & Tide Predictor

An end-to-end data pipeline and survival analysis tool designed to predict time-to-first-bite for target fish species (Speckled Trout, Black Drum) in the Galveston, Texas area.

## Project Architecture

This project bridges automated environmental data extraction with biostatistical modeling using a three-tier architecture:

1. **Data Ingestion (Python):** Automated scripts querying the NOAA CO-OPS API to extract continuous environmental covariates, including water temperature, barometric pressure, and predicted tide levels (Station: 8771341 - Galveston Pleasure Pier).
2. **Relational Storage (PostgreSQL):** A local, robust SQL database storing continuous weather readings alongside right-censored event data (fishing catch logs) using `UPSERT` logic for seamless time-series merging.
3. **Statistical Modeling (R):** Connecting directly to the PostgreSQL database to perform a rolling join on the time-series data. Fitting a Kaplan-Meier baseline curve and a Cox Proportional Hazards Model to evaluate how fluctuating environmental covariates impact bite velocity.

## Repository Structure

* `scripts/noaa_ingestion.py`: The Python pipeline handling API requests and PostgreSQL injection.
* `scripts/init_schema.sql`: The database blueprint establishing relational tables (`catch_logs`, `environmental_conditions`, `tide_predictions`).
* `scripts/survival_analysis.R`: The biostatistical model calculating baseline hazards and covariate impacts.

## Future Product Roadmap (Mobile Application & Model Expansion)

This repository serves as the analytical backend for a planned mobile application and an expanded predictive model, featuring:

* **Expanded Covariate Tracking:** Integrating categorical variables into the SQL schema—such as bait type (e.g., Live Shrimp vs. Artificial), rig setup, and water clarity—to calculate highly specific hazard ratios.
* **Live Session Tracking:** Building a real-time timer interface that automatically pulls the user's GPS coordinates and live forecast conditions to generate an on-the-spot predicted median wait time.
* **One-Tap Event Logging:** Seamlessly logging a catch to stop the timer and automatically writing the event to the `catch_logs` database. 
* **Computer Vision Integration:** Allowing users to snap a photo of the catch, utilizing image classification to automatically populate the species and estimated length.
* **Predictive Trip Planning:** Inputting a future time and location to generate a survival curve forecast based on public predictive weather models and localized tide shifts.