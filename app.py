"""
Warehouse Optimization Dashboard
Interactive Streamlit dashboard for analyzing warehouse optimization results.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data_loader import WarehouseDataLoader
from ui_components import create_route_animation


# Page configuration
st.set_page_config(
    page_title="Warehouse Optimization Dashboard",
    page_icon="📦",
    layout="wide"
)

# Title
st.title("📦 Warehouse Optimization Dashboard")

# Load data
@st.cache_data
def load_data():
    """Load all data from Excel file."""
    try:
        loader = WarehouseDataLoader(
            'Danish Final Model - Flow Conservation with Data Analysis and Results.xlsx'
        )
        layout_data, optimization_results = loader.load_all_data()
        return layout_data, optimization_results, loader
    except Exception as e:
        st.error(f"Error loading data from Excel file: {str(e)}")
        st.stop()

# Load the data
layout_data, optimization_results, loader = load_data()

# Sidebar - Input Parameters
st.sidebar.header("📊 Input Parameters")
st.sidebar.markdown("Adjust the parameters below to calculate ROI:")

hourly_wage = st.sidebar.slider(
    "Hourly Worker Wage ($)",
    min_value=10.0,
    max_value=50.0,
    value=25.0,
    step=0.5,
    help="Average hourly wage for warehouse workers"
)

orders_per_day = st.sidebar.slider(
    "Orders per Day",
    min_value=100,
    max_value=2000,
    value=600,
    step=50,
    help="Average number of orders processed per day"
)

working_days_per_year = st.sidebar.slider(
    "Working Days per Year",
    min_value=200,
    max_value=365,
    value=300,
    step=5,
    help="Number of working days in a year"
)

# Scenario selector
st.sidebar.markdown("---")
st.sidebar.header("🎯 Scenario Selection")
available_scenarios = optimization_results['Scenario'].tolist()
selected_scenario = st.sidebar.selectbox(
    "Select Loadform Scenario",
    available_scenarios,
    index=available_scenarios.index('Loadform 5') if 'Loadform 5' in available_scenarios else 0,
    help="Select the scenario to analyze"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:**")
st.sidebar.info("Danish Final Model - Flow Conservation with Data Analysis and Results.xlsx")

# Create tabs
tab1, tab2 = st.tabs(["📈 ROI Dashboard", "🚚 Route Animation"])

with tab1:
    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("🗺️ Warehouse Layout")
        st.markdown("Spatial distribution of warehouse locations")
        
        # Create warehouse layout plot
        fig_layout = go.Figure()
        
        # Add scatter plot for locations
        fig_layout.add_trace(go.Scatter(
            x=layout_data['x'],
            y=layout_data['y'],
            mode='markers+text',
            marker=dict(
                size=10,
                color='#1f77b4',
                line=dict(width=1, color='white')
            ),
            text=layout_data['Location'],
            textposition='top center',
            textfont=dict(size=8),
            hovertemplate='<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>',
            showlegend=False
        ))
        
        # Highlight the start location
        start_data = layout_data[layout_data['Location'] == 'Start']
        if not start_data.empty:
            fig_layout.add_trace(go.Scatter(
                x=start_data['x'],
                y=start_data['y'],
                mode='markers',
                marker=dict(
                    size=15,
                    color='#ff7f0e',
                    symbol='star',
                    line=dict(width=2, color='white')
                ),
                name='Start Point',
                hovertemplate='<b>Start Point</b><br>X: %{x}<br>Y: %{y}<extra></extra>'
            ))
        
        fig_layout.update_layout(
            xaxis_title="X Coordinate (meters)",
            yaxis_title="Y Coordinate (meters)",
            hovermode='closest',
            height=500,
            plot_bgcolor='#f8f9fa',
            xaxis=dict(gridcolor='white', zeroline=True, zerolinecolor='gray'),
            yaxis=dict(gridcolor='white', zeroline=True, zerolinecolor='gray'),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )
        
        st.plotly_chart(fig_layout, use_container_width=True)
        
        # Display layout statistics
        st.markdown("**Layout Statistics:**")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Locations", len(layout_data))
        with stat_col2:
            st.metric("X Range", f"{layout_data['x'].min():.0f} to {layout_data['x'].max():.0f}")
        with stat_col3:
            st.metric("Y Range", f"{layout_data['y'].min():.0f} to {layout_data['y'].max():.0f}")
    
    with col2:
        st.header("📈 Performance Comparison")
        st.markdown(f"Comparing **{selected_scenario}** results")
        
        # Get scenario data
        scenario_data = loader.get_scenario_data(selected_scenario)
        
        # Create comparison dataframe for visualization
        comparison_data = pd.DataFrame({
            'Metric': ['Distance (m)', 'Distance (m)', 'Time (hrs)', 'Time (hrs)'],
            'Model': ['Optimized', 'Current Practice', 'Optimized', 'Current Practice'],
            'Value': [
                scenario_data['Distance_Optimized'],
                scenario_data['Distance_Current'],
                scenario_data['Time_Optimized'],
                scenario_data['Time_Current']
            ]
        })
        
        # Distance comparison chart
        st.subheader("Distance Comparison")
        distance_data = comparison_data[comparison_data['Metric'] == 'Distance (m)']
        fig_distance = px.bar(
            distance_data,
            x='Model',
            y='Value',
            color='Model',
            color_discrete_map={'Optimized': '#2ecc71', 'Current Practice': '#e74c3c'},
            text='Value',
            labels={'Value': 'Total Distance (meters)'}
        )
        fig_distance.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_distance.update_layout(
            showlegend=False,
            height=300,
            yaxis_title="Distance (meters)"
        )
        st.plotly_chart(fig_distance, use_container_width=True)
        
        # Calculate improvement
        distance_improvement = ((scenario_data['Distance_Current'] - scenario_data['Distance_Optimized']) 
                               / scenario_data['Distance_Current'] * 100)
        st.success(f"✅ **{distance_improvement:.1f}% reduction** in travel distance")
        
        # Time comparison chart
        st.subheader("Time Comparison")
        time_data = comparison_data[comparison_data['Metric'] == 'Time (hrs)']
        fig_time = px.bar(
            time_data,
            x='Model',
            y='Value',
            color='Model',
            color_discrete_map={'Optimized': '#2ecc71', 'Current Practice': '#e74c3c'},
            text='Value',
            labels={'Value': 'Total Time (hours)'}
        )
        fig_time.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_time.update_layout(
            showlegend=False,
            height=300,
            yaxis_title="Time (hours)"
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Calculate improvement
        time_improvement = ((scenario_data['Time_Current'] - scenario_data['Time_Optimized']) 
                           / scenario_data['Time_Current'] * 100)
        st.success(f"✅ **{time_improvement:.1f}% reduction** in operation time")
    
    # ROI Calculator Section
    st.markdown("---")
    st.header("💰 ROI Calculator")
    st.markdown("Calculate the financial impact of optimization based on your input parameters")
    
    # Calculate annual metrics
    annual_orders = orders_per_day * working_days_per_year
    
    # Time savings per order
    time_saved_per_order_hours = (scenario_data['Time_Current'] - scenario_data['Time_Optimized'])
    
    # Annual time saved
    annual_time_saved_hours = time_saved_per_order_hours * annual_orders
    
    # Annual cost savings
    annual_cost_savings = annual_time_saved_hours * hourly_wage
    
    # Distance savings
    distance_saved_per_order = scenario_data['Distance_Current'] - scenario_data['Distance_Optimized']
    annual_distance_saved = distance_saved_per_order * annual_orders
    
    # Display ROI metrics
    roi_col1, roi_col2, roi_col3 = st.columns(3)
    
    with roi_col1:
        st.metric(
            label="💵 Total Annual Cost Savings",
            value=f"${annual_cost_savings:,.2f}",
            delta=f"{distance_improvement:.1f}% improvement",
            delta_color="normal"
        )
        st.caption(f"Based on {annual_orders:,} annual orders")
    
    with roi_col2:
        st.metric(
            label="⏱️ Annual Time Saved",
            value=f"{annual_time_saved_hours:,.2f} hrs",
            delta=f"{time_saved_per_order_hours:.3f} hrs per order",
            delta_color="normal"
        )
        st.caption(f"At ${hourly_wage}/hour wage rate")
    
    with roi_col3:
        st.metric(
            label="🚶 Annual Distance Saved",
            value=f"{annual_distance_saved:,.2f} m",
            delta=f"{distance_saved_per_order:.2f} m per order",
            delta_color="normal"
        )
        st.caption(f"Reduced travel distance")
    
    # Detailed breakdown
    st.markdown("---")
    st.subheader("📋 Detailed Breakdown")
    
    breakdown_col1, breakdown_col2 = st.columns(2)
    
    with breakdown_col1:
        st.markdown("**Calculation Parameters:**")
        calc_df = pd.DataFrame({
            'Parameter': [
                'Hourly Wage',
                'Orders per Day',
                'Working Days per Year',
                'Annual Orders',
                'Selected Scenario'
            ],
            'Value': [
                f"${hourly_wage:.2f}",
                f"{orders_per_day:,}",
                f"{working_days_per_year}",
                f"{annual_orders:,}",
                selected_scenario
            ]
        })
        st.dataframe(calc_df, hide_index=True, use_container_width=True)
    
    with breakdown_col2:
        st.markdown("**Per Order Metrics:**")
        per_order_df = pd.DataFrame({
            'Metric': [
                'Time - Optimized',
                'Time - Current',
                'Time Saved',
                'Distance - Optimized',
                'Distance - Current',
                'Distance Saved'
            ],
            'Value': [
                f"{scenario_data['Time_Optimized']:.3f} hrs",
                f"{scenario_data['Time_Current']:.3f} hrs",
                f"{time_saved_per_order_hours:.3f} hrs",
                f"{scenario_data['Distance_Optimized']:.2f} m",
                f"{scenario_data['Distance_Current']:.2f} m",
                f"{distance_saved_per_order:.2f} m"
            ]
        })
        st.dataframe(per_order_df, hide_index=True, use_container_width=True)
    
    # All scenarios comparison
    st.markdown("---")
    st.header("🎯 All Scenarios Comparison")
    st.markdown("Compare optimization results across all loadform scenarios")
    
    # Prepare data for all scenarios
    all_scenarios_data = []
    for _, row in optimization_results.iterrows():
        scenario = row['Scenario']
        
        # Calculate metrics for this scenario with current parameters
        time_saved = row['Time_Current'] - row['Time_Optimized']
        annual_time = time_saved * annual_orders
        cost_savings = annual_time * hourly_wage
        distance_saved = row['Distance_Current'] - row['Distance_Optimized']
        
        all_scenarios_data.append({
            'Scenario': scenario,
            'Distance Reduction (%)': ((row['Distance_Current'] - row['Distance_Optimized']) 
                                       / row['Distance_Current'] * 100),
            'Time Reduction (%)': ((row['Time_Current'] - row['Time_Optimized']) 
                                  / row['Time_Current'] * 100),
            'Annual Savings ($)': cost_savings,
            'Annual Time Saved (hrs)': annual_time,
            'Annual Distance Saved (m)': distance_saved * annual_orders
        })
    
    all_scenarios_df = pd.DataFrame(all_scenarios_data)
    
    # Display table
    st.dataframe(
        all_scenarios_df.style.format({
            'Distance Reduction (%)': '{:.2f}%',
            'Time Reduction (%)': '{:.2f}%',
            'Annual Savings ($)': '${:,.2f}',
            'Annual Time Saved (hrs)': '{:,.2f}',
            'Annual Distance Saved (m)': '{:,.2f}'
        }).background_gradient(subset=['Annual Savings ($)'], cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )
    
    # Comparison charts
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        fig_all_distance = px.bar(
            all_scenarios_df,
            x='Scenario',
            y='Distance Reduction (%)',
            title='Distance Reduction by Scenario',
            color='Distance Reduction (%)',
            color_continuous_scale='Greens'
        )
        fig_all_distance.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_all_distance, use_container_width=True)
    
    with comp_col2:
        fig_all_savings = px.bar(
            all_scenarios_df,
            x='Scenario',
            y='Annual Savings ($)',
            title='Annual Cost Savings by Scenario',
            color='Annual Savings ($)',
            color_continuous_scale='Blues'
        )
        fig_all_savings.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_all_savings, use_container_width=True)
    
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; padding: 20px;'>
                <p>Warehouse Optimization Dashboard | Data-driven insights for warehouse operations</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
with tab2:
    st.header("🚚 Order Picking Animation: Current vs. Optimized")
    
    st.markdown("""
    ### 📦 Scenario: Picking 12 Items from a Multi-Aisle Warehouse
    
    This animation demonstrates how route optimization reduces travel time and distance in a real warehouse operation.
    Watch as both workers pick the same 12 items, but following different routes.
    
    **Key Observations:**
    - 🟥 **Left (Current Practice)**: Worker jumps between aisles unnecessarily
    - 🟩 **Right (Optimized Model)**: Worker follows a systematic pattern, staying within aisles
    - 📊 **Metrics Update**: Distance and stop count shown in real-time
    - 🛣️ **Path Visualization**: Route is drawn progressively as the worker moves
    """)
    
    # --- Route Definitions ---
    # Realistic picking scenario: 12 items spread across 3 aisles
    
    # Current Practice: Poor route planning - jumping between aisles
    # Picks items in the order they appear on the pick list (without optimization)
    CURRENT_ROUTE_NODES = [
        1,   # Aisle 1, Left side
        21,  # Jump to Aisle 3, Left side (BAD!)
        3,   # Back to Aisle 1 (BAD!)
        23,  # Jump to Aisle 3 again (BAD!)
        5,   # Back to Aisle 1 (BAD!)
        15,  # Jump to Aisle 2, Right side (BAD!)
        7,   # Aisle 1, Right side
        27,  # Jump to Aisle 3, Right side (BAD!)
        12,  # Jump to Aisle 2, Left side (BAD!)
        24,  # Jump to Aisle 3 (BAD!)
        9,   # Back to Aisle 1 (BAD!)
        19   # Aisle 2, Right side
    ]
    
    # Optimized Route: Intelligent clustering - complete each aisle before moving to next
    # Same 12 items, but picked in optimal sequence
    OPTIMIZED_ROUTE_NODES = [
        1, 3, 5, 7, 9,      # Complete Aisle 1 (left to right)
        12, 15, 19,         # Complete Aisle 2 (left to right)
        21, 23, 24, 27      # Complete Aisle 3 (left to right)
    ]
    
    # --- Coordinate Mapping ---
    # We need to map these node lists to the x,y coordinates from layout_data
    
    # Create a 'node_id' column to match our lists
    layout_data_copy = layout_data.copy()
    layout_data_copy['node_id'] = layout_data_copy['Location'].apply(
        lambda x: 0 if x == 'Start' else (int(x.split(' ')[1]) if 'Rack' in x else -1)
    )
    
    # Filter to only include Start and Racks 1-30 (remove duplicates)
    layout_data_copy = layout_data_copy[layout_data_copy['node_id'] >= 0]
    layout_data_copy = layout_data_copy.drop_duplicates(subset='node_id', keep='first')
    
    # Create a coordinate lookup dictionary
    node_coords = layout_data_copy.set_index('node_id')[['x', 'y']].to_dict('index')
    
    # Get Start/Depot coordinates (Node 0)
    start_coords = node_coords[0]
    
    # Build the coordinate lists for the routes
    current_route_coords = [start_coords] + [node_coords[node] for node in CURRENT_ROUTE_NODES] + [start_coords]
    optimized_route_coords = [start_coords] + [node_coords[node] for node in OPTIMIZED_ROUTE_NODES] + [start_coords]
    
    # Calculate actual distances for comparison
    def calc_route_distance(coords):
        total = 0
        for i in range(1, len(coords)):
            dx = coords[i]['x'] - coords[i-1]['x']
            dy = coords[i]['y'] - coords[i-1]['y']
            total += (dx**2 + dy**2)**0.5
        return total
    
    # Build coordinate lists
    current_full_route = [start_coords] + [node_coords[node] for node in CURRENT_ROUTE_NODES] + [start_coords]
    optimized_full_route = [start_coords] + [node_coords[node] for node in OPTIMIZED_ROUTE_NODES] + [start_coords]
    
    current_distance = calc_route_distance(current_full_route)
    optimized_distance = calc_route_distance(optimized_full_route)
    distance_saved = current_distance - optimized_distance
    improvement_pct = (distance_saved / current_distance) * 100
    
    # Display comparison metrics
    st.markdown("### 📊 Route Comparison Metrics")
    col_anim1, col_anim2, col_anim3 = st.columns(3)
    
    with col_anim1:
        st.metric(
            "Current Practice Distance", 
            f"{current_distance:.1f}m",
            delta=None,
            help="Total distance traveled including return to depot"
        )
        st.caption("❌ Inefficient aisle-jumping")
    
    with col_anim2:
        st.metric(
            "Optimized Distance", 
            f"{optimized_distance:.1f}m",
            delta=f"-{distance_saved:.1f}m",
            delta_color="normal",
            help="Total distance traveled including return to depot"
        )
        st.caption("✅ Systematic aisle completion")
    
    with col_anim3:
        st.metric(
            "Improvement", 
            f"{improvement_pct:.1f}%",
            delta=f"{distance_saved:.1f}m saved",
            delta_color="normal",
            help="Percentage reduction in travel distance"
        )
        st.caption(f"🎯 Same {len(CURRENT_ROUTE_NODES)} items picked")
    
    # --- Create and Display the Chart ---
    st.markdown("---")
    if st.button("🎬 Generate Animation", type="primary", use_container_width=True):
        st.info("💡 **Click '▶ Play Animation' on the chart to start** • Watch both workers simultaneously")
        
        with st.spinner("Generating side-by-side animation..."):
            fig_anim = create_route_animation(layout_data_copy, current_route_coords, optimized_route_coords)
            st.plotly_chart(fig_anim, use_container_width=True)
            
            # Detailed insights after animation
            st.markdown("---")
            st.markdown("### 🎓 Key Insights for Thesis")
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                st.markdown("""
                #### ❌ Current Practice Problems:
                1. **Aisle Jumping**: Worker constantly moves between aisles (e.g., Rack 1 → Rack 21 → Rack 3)
                2. **Backtracking**: Returns to previously visited aisles multiple times
                3. **No Clustering**: Items picked in pick-list order without spatial consideration
                4. **Longer Distance**: Travels {:.1f}m for the same 12 items
                5. **Higher Labor Cost**: More time = higher operational cost
                """.format(current_distance))
            
            with col_insight2:
                st.markdown("""
                #### ✅ Optimized Model Benefits:
                1. **Aisle Completion**: Finishes each aisle before moving to next
                2. **Systematic Flow**: Follows a clear left-to-right, aisle-by-aisle pattern
                3. **Intelligent Clustering**: Groups items by proximity
                4. **Shorter Distance**: Only {:.1f}m - **{:.1f}% reduction**
                5. **Lower Labor Cost**: Less time = reduced operational expenses
                """.format(optimized_distance, improvement_pct))
            
            st.success(f"""
            **💰 Business Impact**: For a warehouse processing {orders_per_day} orders/day × {working_days_per_year} days/year, 
            this {improvement_pct:.1f}% improvement translates to significant cost savings as shown in the ROI Dashboard tab.
            """)
            
            st.markdown("---")
            st.markdown("""
            ### 📝 How to Use This Animation in Your Thesis:
            
            1. **Problem Statement**: Show the Current Practice (left) to illustrate inefficiency
            2. **Proposed Solution**: Show the Optimized Model (right) demonstrating systematic routing
            3. **Quantitative Results**: Reference the distance reduction ({:.1f}m → {:.1f}m = {:.1f}% improvement)
            4. **Visual Evidence**: Use screenshots from the animation showing the contrast in routing patterns
            5. **Scalability**: Explain this improvement applies to every order, compounding savings over time
            
            **💡 Tip**: Pause the animation at key moments to highlight specific inefficiencies in your presentation!
            """.format(current_distance, optimized_distance, improvement_pct))

