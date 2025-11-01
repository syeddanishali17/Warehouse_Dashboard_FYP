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
            xaxis=dict(title="X Coordinate", range=[layout_df['x'].min()-5, layout_df['x'].max()+5]),
            yaxis=dict(title="Y Coordinate", range=[layout_df['y'].min()-5, layout_df['y'].max()+5]),
            hovermode="closest",
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {
                        "label": "► Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 100, "redraw": False}, "fromcurrent": True, "transition": {"duration": 0}}]
                    },
                    {
                        "label": "■ Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )
    )

    # Add all 30 racks as a static background
    racks = layout_df[layout_df['Location'] != 'Start']
    fig.add_trace(go.Scatter(
        x=racks['x'], y=racks['y'],
        mode='markers+text', name='Racks',
        marker=dict(color='lightgrey', size=10),
        text=racks['Location'],
        textposition='top center',
        textfont=dict(size=8),
        hoverinfo='none'
    ))
    
    # Add Depot (Start)
    depot = layout_df[layout_df['Location'] == 'Start']
    fig.add_trace(go.Scatter(
        x=depot['x'], y=depot['y'],
        mode='markers', name='Depot',
        marker=dict(color='black', size=15, symbol='star')
    ))

    # 2. Add Route Paths (Static Lines)
    fig.add_trace(go.Scatter(
        x=[c['x'] for c in current_route_coords],
        y=[c['y'] for c in current_route_coords],
        mode='lines', name='Current Path',
        line=dict(color='rgba(231, 76, 60, 0.5)', width=2, dash='dot')
    ))
    
    fig.add_trace(go.Scatter(
        x=[c['x'] for c in optimized_route_coords],
        y=[c['y'] for c in optimized_route_coords],
        mode='lines', name='Optimized Path',
        line=dict(color='rgba(46, 204, 113, 0.5)', width=2)
    ))

    # 3. Add Moving "Trucks" (These are the traces we will animate)
    # The data here is just the starting point.
    fig.add_trace(go.Scatter(
        x=[current_route_coords[0]['x']],
        y=[current_route_coords[0]['y']],
        mode='markers', name='Current Worker',
        marker=dict(color='#e74c3c', size=12, symbol='square', line=dict(width=1, color='black'))
    ))
    
    fig.add_trace(go.Scatter(
        x=[optimized_route_coords[0]['x']],
        y=[optimized_route_coords[0]['y']],
        mode='markers', name='Optimized Worker',
        marker=dict(color='#2ecc71', size=12, symbol='circle', line=dict(width=1, color='black'))
    ))

    # 4. Create Animation Frames
    max_steps = max(len(current_route_coords), len(optimized_route_coords))
    
    current_frames_x = [c['x'] for c in current_route_coords]
    current_frames_y = [c['y'] for c in current_route_coords]
    
    opt_frames_x = [c['x'] for c in optimized_route_coords]
    opt_frames_y = [c['y'] for c in optimized_route_coords]

    # Pad the shorter (optimized) route so it "finishes" and waits at the end
    if len(opt_frames_x) < max_steps:
        opt_frames_x.extend([optimized_route_coords[-1]['x']] * (max_steps - len(opt_frames_x)))
        opt_frames_y.extend([optimized_route_coords[-1]['y']] * (max_steps - len(opt_frames_y)))
    
    # *** THIS IS THE CORRECTED LOGIC ***
    frames = [go.Frame(
        data=[
            # This data maps to the 4th trace (Current Worker)
            go.Scatter(x=[current_frames_x[k]], y=[current_frames_y[k]]), 
            # This data maps to the 5th trace (Optimized Worker)
            go.Scatter(x=[opt_frames_x[k]], y=[opt_frames_y[k]])
        ],
        # We target traces 4 and 5 (the two moving markers)
        traces=[4, 5], 
        name=f'frame{k}'
    ) for k in range(max_steps)]
    
    fig.frames = frames
    
    # Adjust layout
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
