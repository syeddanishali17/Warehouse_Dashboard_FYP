"""
Data Loader Module for Warehouse Optimization Dashboard
Loads data from the Excel file without any hardcoded fallbacks.
"""
import pandas as pd
import openpyxl


class WarehouseDataLoader:
    """Loads and parses warehouse data from Excel file."""
    
    def __init__(self, excel_file_path):
        """Initialize the data loader with Excel file path."""
        self.excel_file_path = excel_file_path
        self.layout_data = None
        self.optimization_results = None
        
    def load_warehouse_layout(self):
        """
        Load warehouse layout data from 'Model Testing (Final)' sheet.
        Returns DataFrame with Location, x, y columns.
        """
        try:
            # Skip first 7 rows, row 8 is the header
            layout_df = pd.read_excel(
                self.excel_file_path, 
                sheet_name='Model Testing (Final)', 
                skiprows=7, 
                engine='openpyxl'
            )
            
            # Extract only the required columns
            required_columns = ['Location', 'x', 'y']
            for col in required_columns:
                if col not in layout_df.columns:
                    raise ValueError(f"Required column '{col}' not found in layout sheet")
            
            self.layout_data = layout_df[required_columns].copy()
            
            # Convert x and y to numeric, coercing errors to NaN
            self.layout_data['x'] = pd.to_numeric(self.layout_data['x'], errors='coerce')
            self.layout_data['y'] = pd.to_numeric(self.layout_data['y'], errors='coerce')
            
            # Remove any rows with NaN in critical columns
            self.layout_data = self.layout_data.dropna(subset=['Location', 'x', 'y'])
            
            return self.layout_data
            
        except Exception as e:
            raise Exception(f"Error loading warehouse layout data: {str(e)}")
    
    def load_optimization_results(self):
        """
        Load optimization results from 'Data Analysis (Comparison)' sheet.
        Parses scenarios and extracts Total Distance and Total Time metrics.
        Returns DataFrame with scenarios and their metrics.
        """
        try:
            # Read without header to parse manually
            comparison_df = pd.read_excel(
                self.excel_file_path, 
                sheet_name='Data Analysis (Comparison)', 
                header=None, 
                engine='openpyxl'
            )
            
            results = []
            
            # Find all rows containing "Loadform"
            for idx, row in comparison_df.iterrows():
                if pd.notna(row[0]) and 'Loadform' in str(row[0]):
                    # Extract scenario name (e.g., "Loadform 1")
                    scenario_text = str(row[0])
                    if 'Loadform' in scenario_text:
                        # Extract the number
                        parts = scenario_text.split('Loadform')
                        if len(parts) > 1:
                            scenario_num = parts[1].strip().split(')')[0].strip()
                            scenario_name = f"Loadform {scenario_num}"
                            
                            # Get Total Distance (meters) - 2 rows after scenario
                            distance_row_idx = idx + 2
                            if distance_row_idx < len(comparison_df):
                                distance_optimized = comparison_df.iloc[distance_row_idx, 2]  # Column C
                                distance_current = comparison_df.iloc[distance_row_idx, 12]  # Column M
                            else:
                                raise ValueError(f"Could not find distance data for {scenario_name}")
                            
                            # Get Total Time (Hours) - 4 rows after scenario
                            time_row_idx = idx + 4
                            if time_row_idx < len(comparison_df):
                                time_optimized = comparison_df.iloc[time_row_idx, 2]  # Column C
                                time_current = comparison_df.iloc[time_row_idx, 12]  # Column M
                            else:
                                raise ValueError(f"Could not find time data for {scenario_name}")
                            
                            results.append({
                                'Scenario': scenario_name,
                                'Distance_Optimized': float(distance_optimized),
                                'Distance_Current': float(distance_current),
                                'Time_Optimized': float(time_optimized),
                                'Time_Current': float(time_current)
                            })
            
            if not results:
                raise ValueError("No scenario data found in the comparison sheet")
            
            self.optimization_results = pd.DataFrame(results)
            return self.optimization_results
            
        except Exception as e:
            raise Exception(f"Error loading optimization results: {str(e)}")
    
    def load_all_data(self):
        """Load all data from Excel file."""
        self.load_warehouse_layout()
        self.load_optimization_results()
        return self.layout_data, self.optimization_results
    
    def get_scenario_data(self, scenario_name):
        """
        Get data for a specific scenario.
        Returns dictionary with distance and time metrics.
        """
        if self.optimization_results is None:
            raise ValueError("Optimization results not loaded yet")
        
        scenario_data = self.optimization_results[
            self.optimization_results['Scenario'] == scenario_name
        ]
        
        if scenario_data.empty:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        return scenario_data.iloc[0].to_dict()

