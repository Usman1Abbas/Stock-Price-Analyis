import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# -------------------------------------
# Page Configuration
# -------------------------------------
st.set_page_config(
    page_title="Stock Price Analyzer",
    page_icon="📈",
    layout="wide",  # Use wide layout for better plot visibility
    initial_sidebar_state="expanded"
)

# Apply Seaborn theme for plots
sns.set_theme(style="darkgrid")
plt.style.use('seaborn-v0_8-darkgrid') # Ensure consistent style

# -------------------------------------
# Caching Functions for Performance
# -------------------------------------
# Cache data fetching to avoid re-downloading on every interaction
@st.cache_data(ttl=60*60) # Cache for 1 hour
def fetch_stock_data(tickers, start_date, end_date):
    """
    Fetches historical stock price data from Yahoo Finance. (Cached)
    """
    st.info(f"Fetching data for: {', '.join(tickers)} from {start_date} to {end_date}...")
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False) # Disable yf progress bar
        if data.empty:
            st.error("Error: No data downloaded. Check tickers and date range.")
            return None, None

        # Handle single ticker download format
        if len(tickers) == 1 and isinstance(data.columns, pd.Index):
             data.columns = pd.MultiIndex.from_product([data.columns, tickers])

        # Determine price column ('Adj Close' preferred)
        if 'Adj Close' not in data.columns.get_level_values(0):
             if 'Close' in data.columns.get_level_values(0):
                  price_col = 'Close'
                  st.warning("Using 'Close' price as 'Adj Close' is not available.")
             else:
                  st.error("Error: Neither 'Adj Close' nor 'Close' price found in data.")
                  return None, None
        else:
             price_col = 'Adj Close'

        st.success("Data fetched successfully.")
        return data, price_col

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None

# Cache indicator calculation
@st.cache_data
def calculate_indicators(data, price_col='Adj Close', short_window=20, long_window=50):
    """
    Calculates moving averages and simple returns. (Cached)
    """
    if data is None or price_col not in data.columns.get_level_values(0):
        st.error("Error: Invalid data provided for indicator calculation.")
        return None

    df_processed = data.copy()
    tickers = data.columns.get_level_values(1).unique().tolist()

    short_ma_label = f'MA_{short_window}'
    long_ma_label = f'MA_{long_window}'

    for ticker in tickers:
         price_series = df_processed[(price_col, ticker)]
         if price_series.isnull().all(): # Skip if all price data is NaN for a ticker
              st.warning(f"Skipping indicator calculation for {ticker} due to missing price data.")
              continue

         df_processed[(short_ma_label, ticker)] = price_series.rolling(window=short_window, min_periods=1).mean()
         df_processed[(long_ma_label, ticker)] = price_series.rolling(window=long_window, min_periods=1).mean()
         df_processed[('Simple Return', ticker)] = price_series.pct_change()

    df_processed = df_processed.sort_index(axis=1) # Sort columns for consistency
    return df_processed


# -------------------------------------
# Plotting Function (Modified for Streamlit)
# -------------------------------------
def create_plots(data, price_col, tickers, short_window, long_window, plot_returns, plot_trend):
    """
    Generates Matplotlib figures for stock data visualization.
    Returns a dictionary of figures {ticker: fig_object}.
    """
    if data is None:
        st.warning("No data available to generate plots.")
        return {}

    figures = {}
    short_ma_label = f'MA_{short_window}'
    long_ma_label = f'MA_{long_window}'

    for ticker in tickers:
        # Determine number of subplots needed for this ticker
        num_subplots = 1
        if plot_returns: num_subplots += 1
        if plot_trend: num_subplots += 1

        fig, axes = plt.subplots(num_subplots, 1, figsize=(12, 6 * num_subplots), sharex=True, squeeze=False) # Always return 2D array
        axes = axes.flatten() # Flatten for easy indexing
        plot_idx = 0

        # Check if data exists for the ticker after processing
        if (price_col, ticker) not in data.columns:
            st.warning(f"No data found for ticker {ticker} to plot.")
            plt.close(fig) # Close the empty figure
            continue

        # --- 1. Main Price and Moving Averages Plot ---
        ax_main = axes[plot_idx]
        price_data = data[(price_col, ticker)]
        short_ma_data = data.get((short_ma_label, ticker)) # Use .get for safety
        long_ma_data = data.get((long_ma_label, ticker))

        ax_main.plot(price_data.index, price_data, label=f'{ticker} {price_col}', linewidth=1.5, color='skyblue')
        if short_ma_data is not None:
            ax_main.plot(short_ma_data.index, short_ma_data, label=f'{short_ma_label}', linestyle='--', linewidth=1, color='orange')
        if long_ma_data is not None:
            ax_main.plot(long_ma_data.index, long_ma_data, label=f'{long_ma_label}', linestyle=':', linewidth=1, color='lightgreen')

        ax_main.set_title(f'{ticker} Price and Moving Averages', fontsize=14)
        ax_main.set_ylabel('Price ($)', fontsize=10)
        ax_main.legend(fontsize=9)
        ax_main.tick_params(axis='x', rotation=0, labelsize=9)
        ax_main.tick_params(axis='y', labelsize=9)
        ax_main.grid(True, linestyle='--', alpha=0.6)
        plot_idx += 1

        # --- 2. Optional: Simple Returns Plot ---
        if plot_returns:
            ax_ret = axes[plot_idx]
            return_data = data.get(('Simple Return', ticker))

            if return_data is not None and not return_data.isnull().all():
                 ax_ret.plot(return_data.index, return_data, label=f'{ticker} Simple Return', color='grey', alpha=0.8, linewidth=1)
                 ax_ret.axhline(0, color='white', linestyle='--', linewidth=0.8) # Zero line
                 ax_ret.set_title(f'{ticker} Daily Simple Returns', fontsize=14)
                 ax_ret.set_ylabel('Return (%)', fontsize=10)
                 ax_ret.tick_params(axis='x', rotation=0, labelsize=9)
                 ax_ret.tick_params(axis='y', labelsize=9)
                 ax_ret.grid(True, axis='y', linestyle='--', alpha=0.5)
                 # Optional: Format y-axis as percentage
                 # from matplotlib.ticker import PercentFormatter
                 # ax_ret.yaxis.set_major_formatter(PercentFormatter(1.0))
            else:
                 ax_ret.text(0.5, 0.5, 'No return data to display', ha='center', va='center', transform=ax_ret.transAxes)
                 ax_ret.set_title(f'{ticker} Daily Simple Returns (No Data)', fontsize=14)
            plot_idx += 1


        # --- 3. Optional: Trend Exploration Plot (Last 7 days MA difference) ---
        if plot_trend:
            ax_trend = axes[plot_idx]
            if short_ma_data is not None and long_ma_data is not None:
                 trend_data = (short_ma_data - long_ma_data).dropna()
                 if len(trend_data) >= 7:
                     recent_trend = trend_data.tail(7) # Last 7 trading days
                     colors = ['#2ca02c' if x > 0 else '#d62728' for x in recent_trend] # Seaborn green/red
                     bars = ax_trend.bar(recent_trend.index, recent_trend, color=colors, width=0.6)

                     ax_trend.axhline(0, color='white', linestyle='-', linewidth=1)
                     ax_trend.set_title(f'{ticker} Exploratory Trend (7d: {short_ma_label} - {long_ma_label})', fontsize=14)
                     ax_trend.set_ylabel('MA Difference', fontsize=10)
                     ax_trend.grid(False)
                     ax_trend.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
                     ax_trend.tick_params(axis='x', rotation=45, labelsize=9)
                     ax_trend.tick_params(axis='y', labelsize=9)
                 else:
                     ax_trend.text(0.5, 0.5, 'Not enough data (< 7 days) for trend plot', ha='center', va='center', transform=ax_trend.transAxes)
                     ax_trend.set_title(f'{ticker} Exploratory Trend (Insufficient Data)', fontsize=14)
            else:
                 ax_trend.text(0.5, 0.5, 'Moving averages not available for trend plot', ha='center', va='center', transform=ax_trend.transAxes)
                 ax_trend.set_title(f'{ticker} Exploratory Trend (Missing MAs)', fontsize=14)
            plot_idx += 1


        # Final figure adjustments
        fig.autofmt_xdate() # Auto-format date labels if needed
        fig.tight_layout(rect=[0, 0.03, 1, 0.97]) # Adjust layout, leave space for suptitle if needed
        # fig.suptitle(f"Analysis for {ticker}", fontsize=16) # Optional: Title per figure

        figures[ticker] = fig # Store the figure object

    return figures

# -------------------------------------
# Streamlit App Layout
# -------------------------------------

st.title("📈 Interactive Stock Price Analyzer")
st.markdown("""
Welcome! Use the sidebar to select stock tickers, date range, and analysis options.
The application uses `yfinance` to fetch data and visualizes price trends, moving averages,
and optional return/trend indicators using Matplotlib/Seaborn.
""")

# --- Sidebar for User Inputs ---
st.sidebar.header("⚙️ Analysis Configuration")

# Ticker Selection (Allow up to 2)
ticker_input = st.sidebar.text_input("Enter Stock Tickers (comma-separated, max 2)", "AAPL, MSFT")
tickers = [t.strip().upper() for t in ticker_input.split(',') if t.strip()] # Clean input

if not tickers:
    st.sidebar.warning("Please enter at least one stock ticker.")
    st.stop() # Halt execution if no tickers
elif len(tickers) > 2:
    st.sidebar.warning("Please enter a maximum of two stock tickers.")
    tickers = tickers[:2] # Limit to first two
    st.sidebar.info(f"Using the first two tickers: {', '.join(tickers)}")

# Date Range Selection
today = datetime.date.today()
default_start = today - datetime.timedelta(days=365 * 2) # Default 2 years back

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", default_start, max_value=today - datetime.timedelta(days=1))
with col2:
    end_date = st.date_input("End Date", today, min_value=start_date + datetime.timedelta(days=1), max_value=today)

if start_date >= end_date:
    st.sidebar.error("Error: End date must fall after start date.")
    st.stop()

# Moving Average Windows
st.sidebar.subheader("Moving Averages")
short_window = st.sidebar.number_input("Short MA Window (days)", min_value=1, max_value=100, value=20, step=1)
long_window = st.sidebar.number_input("Long MA Window (days)", min_value=short_window + 1, max_value=250, value=50, step=1)

if short_window >= long_window:
    st.sidebar.warning("Short MA window should be smaller than Long MA window. Adjusting Long MA.")
    long_window = short_window + 30 # Auto-adjust for usability

# Optional Plot Toggles
st.sidebar.subheader("Optional Plots")
plot_returns = st.sidebar.checkbox("Show Daily Simple Returns", value=False)
plot_trend = st.sidebar.checkbox("Show Exploratory Trend (7-day MA diff)", value=True)


# --- Main Area for Results ---
st.header(f"Analysis for: {', '.join(tickers)}")
st.markdown(f"**Date Range:** `{start_date}` to `{end_date}`")

# Execute Analysis
# 1. Fetch Data
raw_data, price_col_used = fetch_stock_data(tickers, start_date, end_date)

# 2. Calculate Indicators
if raw_data is not None:
    processed_data = calculate_indicators(
        raw_data,
        price_col=price_col_used,
        short_window=short_window,
        long_window=long_window
    )

    # 3. Generate and Display Plots
    if processed_data is not None:
        st.header("📊 Visualizations")
        plot_figures = create_plots(
            processed_data,
            price_col=price_col_used,
            tickers=tickers,
            short_window=short_window,
            long_window=long_window,
            plot_returns=plot_returns,
            plot_trend=plot_trend
        )

        if not plot_figures:
            st.warning("Could not generate any plots based on the selected data and options.")

        # Display plots - consider columns for two tickers
        if len(plot_figures) == 2:
            cols = st.columns(2)
            ticker_list = list(plot_figures.keys())
            with cols[0]:
                st.pyplot(plot_figures[ticker_list[0]])
            with cols[1]:
                st.pyplot(plot_figures[ticker_list[1]])
        elif len(plot_figures) == 1:
             st.pyplot(list(plot_figures.values())[0])


        # Optional: Display DataFrames
        st.subheader(" Glimpse Data")
        with st.expander("Show Processed Data Sample"):
             st.dataframe(processed_data.tail()) # Show tail for recent data

        # Display Raw Data if needed (less common)
        # with st.expander("Show Raw Downloaded Data"):
        #     st.dataframe(raw_data)

    else:
        st.error("Failed to calculate indicators. Cannot proceed with plotting.")

else:
    st.error("Failed to fetch data. Cannot proceed with analysis.")

# --- Footer ---
st.markdown("---")
st.markdown("Built with [Streamlit](https://streamlit.io) | Data from [Yahoo Finance](https://finance.yahoo.com/) via `yfinance`")