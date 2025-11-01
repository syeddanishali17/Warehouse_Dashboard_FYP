# Warehouse Optimization Dashboard

An interactive Streamlit dashboard for analyzing warehouse optimization results and calculating ROI.

## Features

- **Warehouse Layout Visualization**: Interactive scatter plot showing the spatial distribution of all warehouse locations
- **Performance Comparison**: Side-by-side comparison of optimized vs. current practice for distance and time metrics
- **ROI Calculator**: Calculate annual cost savings based on customizable parameters
- **Multi-Scenario Analysis**: Compare results across all loadform scenarios

## Data Source

The dashboard reads data directly from:
- **File**: `Danish Final Model - Flow Conservation with Data Analysis and Results.xlsx`
- **Warehouse Layout**: 'Model Testing (Final)' sheet
- **Optimization Results**: 'Data Analysis (Comparison)' sheet

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will automatically load data from the Excel file and display:
1. Warehouse layout plot
2. Performance comparison charts for the selected scenario
3. ROI calculations based on your input parameters
4. Comparison table across all scenarios

## Input Parameters

Adjust the following parameters in the sidebar:
- **Hourly Worker Wage**: Average hourly wage for warehouse workers ($10-$50)
- **Orders per Day**: Average number of orders processed daily (100-2000)
- **Working Days per Year**: Number of working days in a year (200-365)
- **Scenario Selection**: Choose from Loadform 1-5 scenarios

## Dashboard Sections

### 1. Warehouse Layout
- Visual representation of all warehouse locations
- X and Y coordinates displayed
- Start point highlighted

### 2. Performance Comparison
- Distance comparison bar chart
- Time comparison bar chart
- Percentage improvement metrics

### 3. ROI Calculator
- Total annual cost savings
- Annual time saved
- Annual distance saved
- Detailed breakdown per order

### 4. All Scenarios Comparison
- Table comparing all scenarios
- Distance reduction percentages
- Cost savings across scenarios
- Visual comparison charts

## Technical Details

- **Data Loader**: Custom module (`data_loader.py`) that parses the Excel file
- **No Hardcoded Data**: All data is loaded from the Excel file
- **Error Handling**: Clear error messages if data cannot be loaded
- **Caching**: Uses Streamlit's caching for efficient data loading

## Project Structure

```
Warehouse_dashboard/
├── app.py                                      # Main Streamlit application
├── data_loader.py                              # Data loading module
├── requirements.txt                            # Python dependencies
├── README.md                                   # This file
└── Danish Final Model - Flow Conservation      # Data source (Excel file)
    with Data Analysis and Results.xlsx
```

