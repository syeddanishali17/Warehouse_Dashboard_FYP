# Warehouse Optimization Dashboard

An interactive Streamlit dashboard for analyzing warehouse optimization results and calculating ROI.

## Features

- **📊 ROI Dashboard**: Interactive dashboard with warehouse layout, performance metrics, and financial analysis
- **🚚 Route Animation**: Side-by-side animated visualization comparing Current vs Optimized routing
  - Progressive path drawing showing real-time route tracing
  - Live distance and stop counters
  - Realistic 12-item order picking scenario
  - Clear demonstration of optimization benefits
- **🗺️ Warehouse Layout Visualization**: Interactive scatter plot showing spatial distribution of all locations
- **📈 Performance Comparison**: Side-by-side comparison of optimized vs. current practice
- **💰 ROI Calculator**: Calculate annual cost savings based on customizable parameters
- **🎯 Multi-Scenario Analysis**: Compare results across all loadform scenarios

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

### Tab 1: 📈 ROI Dashboard

#### 1. Warehouse Layout
- Visual representation of all warehouse locations
- X and Y coordinates displayed
- Start point highlighted with 30 racks

#### 2. Performance Comparison
- Distance comparison bar chart
- Time comparison bar chart
- Percentage improvement metrics

#### 3. ROI Calculator
- Total annual cost savings
- Annual time saved
- Annual distance saved
- Detailed breakdown per order

#### 4. All Scenarios Comparison
- Table comparing all scenarios (Loadform 1-5)
- Distance reduction percentages
- Cost savings across scenarios
- Visual comparison charts

### Tab 2: 🚚 Route Animation

#### Order Picking Animation
- **Side-by-side comparison** of Current vs Optimized routes
- **Realistic scenario**: 12 items picked from 3-aisle warehouse
- **Progressive path tracing**: Watch routes being drawn in real-time
- **Live metrics**: Distance and stop count update during animation
- **Truck markers** (🚚): Visual representation of workers moving
- **Warehouse structure**: Aisle markers and depot clearly shown

#### Key Insights
- Problem vs Solution comparison
- Quantitative improvement metrics
- Business impact explanation
- Thesis presentation guidance

## Technical Details

- **Data Loader**: Custom module (`data_loader.py`) that parses the Excel file
- **UI Components**: Reusable visualization module (`ui_components.py`) for animations
- **Animation Engine**: Plotly subplots with frame-based animation
- **No Hardcoded Data**: All data is loaded from the Excel file (except demo routes)
- **Error Handling**: Clear error messages if data cannot be loaded
- **Caching**: Uses Streamlit's caching for efficient data loading
- **Real-time Calculations**: Distance metrics calculated using Euclidean distance

## Project Structure

```
Warehouse_dashboard/
├── app.py                                      # Main Streamlit application (2 tabs)
├── data_loader.py                              # Data loading module
├── ui_components.py                            # Animation and visualization components
├── requirements.txt                            # Python dependencies
├── README.md                                   # Documentation
├── LICENSE                                     # MIT License
├── .gitignore                                  # Git ignore rules
└── Danish Final Model - Flow Conservation      # Data source (Excel file)
    with Data Analysis and Results.xlsx
```

