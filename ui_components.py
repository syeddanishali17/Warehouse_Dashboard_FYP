"""
UI Components Module
Contains reusable UI components and visualizations for the Warehouse Dashboard.
"""
import plotly.graph_objects as go


def create_route_animation(layout_df, current_route_coords, optimized_route_coords):
    """
    Creates an animated Plotly chart showing two routes.
    
    Args:
        layout_df: DataFrame with warehouse layout data
        current_route_coords: List of coordinate dicts for current practice route
        optimized_route_coords: List of coordinate dicts for optimized route
    
    Returns:
        Plotly Figure object with animation
    """
    
    # 1. Base Figure (Warehouse Layout)
    fig = go.Figure(
        layout=go.Layout(
            title="Route Comparison: 'Optimized' (Green) vs. 'Current' (Red)",
            xaxis=dict(title="X Coordinate (meters)", gridcolor='lightgray'),
            yaxis=dict(title="Y Coordinate (meters)", gridcolor='lightgray'),
            hovermode="closest",
            plot_bgcolor='white',
            height=600,
            updatemenus=[{
                "type": "buttons",
                "showactive": False,
                "x": 0.05,
                "y": 1.15,
                "xanchor": "left",
                "yanchor": "top",
                "buttons": [{
                    "label": "► Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 100, "redraw": False}, 
                        "fromcurrent": True,
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                }, {
                    "label": "■ Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False}, 
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                }]
            }]
        )
    )
    
    # Add all 30 racks as a static background
    racks = layout_df[layout_df['Location'] != 'Start']
    fig.add_trace(go.Scatter(
        x=racks['x'], y=racks['y'],
        mode='markers', name='Racks',
        marker=dict(color='lightgrey', size=10),
        hovertemplate='<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>',
        text=racks['Location']
    ))
    
    # Add Depot (Start)
    depot = layout_df[layout_df['Location'] == 'Start']
    fig.add_trace(go.Scatter(
        x=depot['x'], y=depot['y'],
        mode='markers', name='Depot',
        marker=dict(color='black', size=15, symbol='star'),
        hovertemplate='<b>Depot</b><br>X: %{x}<br>Y: %{y}<extra></extra>'
    ))
    
    # 2. Add Route Paths (Static Lines)
    fig.add_trace(go.Scatter(
        x=[c['x'] for c in current_route_coords],
        y=[c['y'] for c in current_route_coords],
        mode='lines', name='Current Path',
        line=dict(color='red', width=1, dash='dot'),
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=[c['x'] for c in optimized_route_coords],
        y=[c['y'] for c in optimized_route_coords],
        mode='lines', name='Optimized Path',
        line=dict(color='green', width=2),
        hoverinfo='skip'
    ))
    
    # 3. Add Moving "Workers" (as initial data)
    fig.add_trace(go.Scatter(
        x=[current_route_coords[0]['x']],
        y=[current_route_coords[0]['y']],
        mode='markers', name='Current Worker',
        marker=dict(color='red', size=14, symbol='square', line=dict(width=2, color='darkred')),
        hovertemplate='<b>Current Worker</b><br>X: %{x}<br>Y: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[optimized_route_coords[0]['x']],
        y=[optimized_route_coords[0]['y']],
        mode='markers', name='Optimized Worker',
        marker=dict(color='green', size=14, symbol='square', line=dict(width=2, color='darkgreen')),
        hovertemplate='<b>Optimized Worker</b><br>X: %{x}<br>Y: %{y}<extra></extra>'
    ))
    
    # 4. Create Animation Frames
    # Ensure routes have the same number of frames by padding the shorter route
    max_steps = max(len(current_route_coords), len(optimized_route_coords))
    
    current_frames_x = [c['x'] for c in current_route_coords]
    current_frames_y = [c['y'] for c in current_route_coords]
    
    opt_frames_x = [c['x'] for c in optimized_route_coords]
    opt_frames_y = [c['y'] for c in optimized_route_coords]
    
    # Pad the shorter route so it "finishes" and waits
    if len(current_frames_x) < max_steps:
        current_frames_x.extend([current_route_coords[-1]['x']] * (max_steps - len(current_frames_x)))
        current_frames_y.extend([current_route_coords[-1]['y']] * (max_steps - len(current_frames_y)))
    
    if len(opt_frames_x) < max_steps:
        opt_frames_x.extend([optimized_route_coords[-1]['x']] * (max_steps - len(opt_frames_x)))
        opt_frames_y.extend([optimized_route_coords[-1]['y']] * (max_steps - len(opt_frames_y)))
    
    frames = [go.Frame(
        data=[
            # Frame data must match the traces in order
            go.Scatter(x=racks['x'], y=racks['y']),  # 0 - Racks
            go.Scatter(x=depot['x'], y=depot['y']),  # 1 - Depot
            go.Scatter(x=[c['x'] for c in current_route_coords], y=[c['y'] for c in current_route_coords]),  # 2 - Current Path
            go.Scatter(x=[c['x'] for c in optimized_route_coords], y=[c['y'] for c in optimized_route_coords]),  # 3 - Optimized Path
            go.Scatter(x=[current_frames_x[k]], y=[current_frames_y[k]]),  # 4 - Current Worker
            go.Scatter(x=[opt_frames_x[k]], y=[opt_frames_y[k]])  # 5 - Optimized Worker
        ],
        # We only update the worker positions (traces 4 and 5)
        traces=[4, 5],
        name=f'frame{k}'
    ) for k in range(max_steps)]
    
    fig.frames = frames
    return fig

