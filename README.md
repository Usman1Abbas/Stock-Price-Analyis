# Stock-Price-Analyis


This Streamlit application provides a user-friendly interface to retrieve, analyze, and visualize historical stock price data for basic technical analysis. It leverages the `yfinance` library to fetch data from Yahoo Finance, Pandas for data manipulation, and Matplotlib/Seaborn for plotting within an interactive Streamlit web app.

## Overview

The primary goal of this application is to offer an easy way for users interested in basic stock market analysis or data science enthusiasts to:

*   Fetch historical stock price data for one or two specified tickers.
*   Define a custom date range for the analysis.
*   Calculate and visualize key indicators like Closing Price and Moving Averages (Simple Moving Averages - SMA).
*   Optionally visualize daily simple returns.
*   Explore potential short-term trends using a simple visual indicator (difference between short-term and long-term SMAs).
*   Interact with the analysis parameters through a clean web interface.

## ✨ Features

*   Interactive UI: Built with Streamlit for easy input and navigation.
*   Ticker Input: Analyze data for one or two stock tickers simultaneously.
*   Custom Date Range: Select start and end dates for historical data retrieval.
*   Moving Average Calculation: Computes configurable short-term and long-term Simple Moving Averages (SMA).
*   Visualization:
    *   Plots the closing stock price over time.
    *   Overlays calculated SMAs on the price chart.
    *   Optional plot for daily simple returns (`pct_change`).
    *   Optional exploratory short-term trend visualization (based on 7-day MA difference).
*   Data Source: Fetches reliable data from Yahoo Finance using the `yfinance` library.
*   Caching: Uses Streamlit's caching to improve performance by avoiding redundant data downloads.


The application features a sidebar for configuration (tickers, dates, MA windows, plot options) and a main area displaying the generated plots and data insights.

## 🛠️ Tech Stack

*   **Language:** Python 3.x
*   **Web Framework:** Streamlit
*   **Data Handling:** Pandas
*   **Data Retrieval:** yfinance
*   **Plotting:** Matplotlib, Seaborn

## ⚙️ Installation

1.    download `stock_app.py`.*

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required libraries:**
    ```bash
    pip install streamlit yfinance pandas matplotlib seaborn
    ```
    *(Consider creating a `requirements.txt` file for easier dependency management)*

## ▶️ Usage

1.  **Navigate to the directory containing `stock_app.py` in your terminal.**

2.  **Run the Streamlit application:**
    ```bash
    streamlit run stock_app.py
    ```

3.  **Interact with the App:**
    *   The application will open in your default web browser.
    *   Use the sidebar on the left to:
        *   Enter one or two stock tickers (comma-separated, e.g., `AAPL, GOOGL`).
        *   Select the desired start and end dates.
        *   Adjust the window lengths for the short-term and long-term moving averages.
        *   Toggle optional plots (Daily Returns, Exploratory Trend).
    *   The main area will automatically update to display the analysis results and plots based on your selections.

## 🔧 Configuration

All primary configuration options (tickers, date range, MA windows, plot visibility) are handled interactively through the Streamlit sidebar widgets within the running application. No code modification is needed for typical use.

## 🚀 Future Considerations

Based on the original requirements, potential future enhancements include:

*   Implementing more advanced technical indicators (e.g., RSI, MACD, Bollinger Bands).
*   Adding more interactive features to the plots (e.g., zooming, tooltips using libraries like Plotly).
*   Implementing basic time series forecasting models.
*   Adding functionality to save the generated plots or analysis data.
*   Expanding ticker support or comparison features.


## 🙏 Acknowledgements

*   Data sourced from **Yahoo Finance**.
*   Data retrieval facilitated by the **`yfinance`** library.
*   Built with the awesome **Streamlit** framework.
