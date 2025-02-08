Premier League Match Predictor

Overview

The Premier League Match Predictor is a machine learning project that predicts the outcomes of Premier League matches. It utilizes historical match data and current season statistics to generate scoreline predictions. The project involves web scraping, data cleaning, feature engineering, and model training to provide accurate match forecasts.

Project Structure

This repository consists of the following key files:

1. scraper.py
- Scrapes past and current match statistics from relevant football data sources.
- Collects data such as possession, shots on target, goals, and other key performance indicators (KPIs).
- Saves extracted data into structured formats for further processing.

2. cleaner.py
- Cleans and preprocesses raw scraped data.
- Handles missing values normalizes numerical features, and prepares datasets for machine learning models.
- Ensures data consistency by aligning past match statistics with current season metrics.

3. model.py
- Implements machine learning models to predict match outcomes.
- Currently uses a Random Forest algorithm, with potential future enhancements for more advanced models.
- Trains on past Premier League seasons while incorporating the latest team statistics.
- Outputs predicted scorelines based on input team data.

4. main.py
- Orchestrates the full workflow of scraping, cleaning, model training, and predictions.
- Provides a user-friendly interface to input upcoming matches and receive predictions.
- Integrates results into a locally hosted website for visualization.
