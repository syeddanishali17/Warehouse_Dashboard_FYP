"""
UI Components Module
Contains reusable UI components and visualizations for the Warehouse Dashboard.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def create_route_animation(layout_df, current_route_coords, optimized_route_coords):
    """
    Creates an animated side-by-side comparison showing Current vs Optimized routes.
    Features progressive path drawing and real-time metrics.
    
    Args:
        layout_df: DataFrame with warehouse layout data
        current_route_coords: List of coordinate dicts for current practice route
        optimized_route_coords: List of coordinate dicts for optimized route
    
    Returns:
        Plotly Figure object with animation
    """
    
    # Calculate cumulative distances for each route
    def calc_distance(coord1, coord2):
        return np.sqrt((coord2['x'] - coord1['x'])**2 + (coord2['y'] - coord1['y'])**2)
    
    current_distances = [0]
    for i in range(1, len(current_route_coords)):
        current_distances.append(
            current_distances[-1] + calc_distance(current_route_coords[i-1], current_route_coords[i])
        )
    
    optimized_distances = [0]
    for i in range(1, len(optimized_route_coords)):
        optimized_distances.append(
            optimized_distances[-1] + calc_distance(optimized_route_coords[i-1], optimized_route_coords[i])
        )
    
    # Create subplots: side by side comparison
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('❌ Current Practice (Inefficient)', '✅ Optimized Model (Efficient)'),
        horizontal_spacing=0.1,
        specs=[[{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Get coordinate ranges
    x_min, x_max = layout_df['x'].min() - 3, layout_df['x'].max() + 3
    y_min, y_max = layout_df['y'].min() - 3, layout_df['y'].max() + 3
    
    # Helper function to add warehouse layout to subplot
    def add_warehouse_elements(fig, row, col):
        # Add aisle markers (horizontal lines)
        for y_level in [10, 20, 30]:
            fig.add_shape(
                type="line",
                x0=x_min, x1=x_max, y0=y_level, y1=y_level,
                line=dict(color="lightgray", width=1, dash="dash"),
                row=row, col=col
            )
        
        # Add racks
        racks = layout_df[layout_df['Location'] != 'Start']
        fig.add_trace(go.Scatter(
            x=racks['x'], y=racks['y'],
            mode='markers',
            marker=dict(color='#ecf0f1', size=8, symbol='square',
                       line=dict(color='#95a5a6', width=1)),
            name='Racks',
            showlegend=False,
            hoverinfo='skip'
        ), row=row, col=col)
        
        # Add depot
        depot = layout_df[layout_df['Location'] == 'Start']
        fig.add_trace(go.Scatter(
            x=depot['x'], y=depot['y'],
            mode='markers+text',
            marker=dict(color='#f39c12', size=18, symbol='star'),
            text=['DEPOT'],
            textposition='top center',
            textfont=dict(size=10, color='#f39c12', family='Arial Black'),
            name='Depot',
            showlegend=False,
            hoverinfo='skip'
        ), row=row, col=col)
    
    # Add warehouse elements to both subplots
    add_warehouse_elements(fig, 1, 1)  # Left: Current
    add_warehouse_elements(fig, 1, 2)  # Right: Optimized
    
    # Add INITIAL path traces (will be animated)
    # Left subplot - Current route
    fig.add_trace(go.Scatter(
        x=[current_route_coords[0]['x']], 
        y=[current_route_coords[0]['y']],
        mode='lines',
        line=dict(color='#e74c3c', width=3),
        name='Current Path',
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=1)
    
    # Right subplot - Optimized route
    fig.add_trace(go.Scatter(
        x=[optimized_route_coords[0]['x']], 
        y=[optimized_route_coords[0]['y']],
        mode='lines',
        line=dict(color='#2ecc71', width=3),
        name='Optimized Path',
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=2)
    
    # Add INITIAL worker markers (trucks/workers)
    # Left subplot - Current worker
    fig.add_trace(go.Scatter(
        x=[current_route_coords[0]['x']],
        y=[current_route_coords[0]['y']],
        mode='markers+text',
        marker=dict(color='#c0392b', size=16, symbol='diamond',
                   line=dict(color='white', width=2)),
        text=['🚚'],
        textfont=dict(size=20),
        name='Current Worker',
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=1)
    
    # Right subplot - Optimized worker
    fig.add_trace(go.Scatter(
        x=[optimized_route_coords[0]['x']],
        y=[optimized_route_coords[0]['y']],
        mode='markers+text',
        marker=dict(color='#27ae60', size=16, symbol='diamond',
                   line=dict(color='white', width=2)),
        text=['🚚'],
        textfont=dict(size=20),
        name='Optimized Worker',
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=2)
    
    # Create animation frames
    max_steps = max(len(current_route_coords), len(optimized_route_coords))
    
    # Pad shorter route
    current_coords_padded = current_route_coords + [current_route_coords[-1]] * (max_steps - len(current_route_coords))
    optimized_coords_padded = optimized_route_coords + [optimized_route_coords[-1]] * (max_steps - len(optimized_route_coords))
    current_dist_padded = current_distances + [current_distances[-1]] * (max_steps - len(current_distances))
    optimized_dist_padded = optimized_distances + [optimized_distances[-1]] * (max_steps - len(optimized_distances))
    
    frames = []
    for k in range(max_steps):
        # Build progressive path (all points up to current frame)
        current_path_x = [c['x'] for c in current_coords_padded[:k+1]]
        current_path_y = [c['y'] for c in current_coords_padded[:k+1]]
        
        opt_path_x = [c['x'] for c in optimized_coords_padded[:k+1]]
        opt_path_y = [c['y'] for c in optimized_coords_padded[:k+1]]
        
        # Create annotation texts with metrics
        current_annotation = f"Distance: {current_dist_padded[k]:.1f}m<br>Stop: {min(k+1, len(current_route_coords))}/{len(current_route_coords)}"
        opt_annotation = f"Distance: {optimized_dist_padded[k]:.1f}m<br>Stop: {min(k+1, len(optimized_route_coords))}/{len(optimized_route_coords)}"
        
        frame = go.Frame(
            data=[
                # Path traces (indices match the add_trace order)
                go.Scatter(x=current_path_x, y=current_path_y),  # Current path
                go.Scatter(x=opt_path_x, y=opt_path_y),  # Optimized path
                # Worker markers
                go.Scatter(
                    x=[current_coords_padded[k]['x']], 
                    y=[current_coords_padded[k]['y']],
                    text=['🚚']
                ),  # Current worker
                go.Scatter(
                    x=[optimized_coords_padded[k]['x']], 
                    y=[optimized_coords_padded[k]['y']],
                    text=['🚚']
                ),  # Optimized worker
            ],
            traces=[2, 3, 4, 5],  # Only update the path and worker traces
            name=str(k),
            layout=go.Layout(
                annotations=[
                    # Left annotation (Current)
                    dict(
                        text=current_annotation,
                        xref="x domain", yref="y domain",
                        x=0.02, y=0.98, xanchor='left', yanchor='top',
                        showarrow=False,
                        bgcolor='rgba(231, 76, 60, 0.8)',
                        font=dict(color='white', size=12, family='Arial Black'),
                        bordercolor='white',
                        borderwidth=2,
                        borderpad=6
                    ),
                    # Right annotation (Optimized)
                    dict(
                        text=opt_annotation,
                        xref="x2 domain", yref="y2 domain",
                        x=0.02, y=0.98, xanchor='left', yanchor='top',
                        showarrow=False,
                        bgcolor='rgba(46, 204, 113, 0.8)',
                        font=dict(color='white', size=12, family='Arial Black'),
                        bordercolor='white',
                        borderwidth=2,
                        borderpad=6
                    )
                ]
            )
        )
        frames.append(frame)
    
    fig.frames = frames
    
    # Update layout
    fig.update_xaxes(range=[x_min, x_max], title_text="X Coordinate (meters)", row=1, col=1)
    fig.update_xaxes(range=[x_min, x_max], title_text="X Coordinate (meters)", row=1, col=2)
    fig.update_yaxes(range=[y_min, y_max], title_text="Y Coordinate (meters)", row=1, col=1)
    fig.update_yaxes(range=[y_min, y_max], title_text="Y Coordinate (meters)", row=1, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='white',
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {
                    "label": "▶ Play Animation",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 200, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 0}
                    }]
                },
                {
                    "label": "⏸ Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                },
                {
                    "label": "⏮ Reset",
                    "method": "animate",
                    "args": [[frames[0].name], {
                        "frame": {"duration": 0, "redraw": True},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 70},
            "showactive": True,
            "x": 0.5,
            "xanchor": "center",
            "y": 0,
            "yanchor": "top"
        }],
        # Add initial annotations
        annotations=[
            dict(
                text=f"Distance: 0.0m<br>Stop: 1/{len(current_route_coords)}",
                xref="x domain", yref="y domain",
                x=0.02, y=0.98, xanchor='left', yanchor='top',
                showarrow=False,
                bgcolor='rgba(231, 76, 60, 0.8)',
                font=dict(color='white', size=12, family='Arial Black'),
                bordercolor='white',
                borderwidth=2,
                borderpad=6
            ),
            dict(
                text=f"Distance: 0.0m<br>Stop: 1/{len(optimized_route_coords)}",
                xref="x2 domain", yref="y2 domain",
                x=0.02, y=0.98, xanchor='left', yanchor='top',
                showarrow=False,
                bgcolor='rgba(46, 204, 113, 0.8)',
                font=dict(color='white', size=12, family='Arial Black'),
                bordercolor='white',
                borderwidth=2,
                borderpad=6
            )
        ]
    )
    
    return fig
