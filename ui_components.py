"""
UI Components Module
Contains reusable UI components and visualizations for the Warehouse Dashboard.
"""
import plotly.graph_objects as go
import numpy as np


def create_multi_route_animation(layout_df, route_definitions, steps_between=5, dwell_time=3):
    """
    Creates an advanced, multi-vehicle animation with interpolation and dwell time.

    Args:
        layout_df: DataFrame with warehouse layout (for background).
        route_definitions: A list of route dictionaries.
                           Each dict has "name", "color", "symbol", "coords".
        steps_between: Number of interpolation steps between stops (for smooth movement).
        dwell_time: Number of frames to pause at each stop (to simulate picking).
    """

    # 1. --- Prepare Animation Data ---
    
    # This list will hold the X, Y coordinates for *every frame* for *each* route
    # e.g., route_frames_data[0] = {'x': [list of all x frames], 'y': [list of all y frames]}
    route_frames_data = []
    
    max_frames = 0 # We'll need this to sync all animations

    # Get start coords from layout
    start_row = layout_df[layout_df['Location'] == 'Start']
    if start_row.empty:
        start_coords = {'x': 0, 'y': 0}
    else:
        start_coords = {'x': start_row.iloc[0]['x'], 'y': start_row.iloc[0]['y']}

    for route in route_definitions:
        route_x_frames = []
        route_y_frames = []
        
        # Get the coordinate list (e.g., [Start, Rack 1, Rack 5, Start])
        coord_path = route["coords"]
        
        if not coord_path:
            route_frames_data.append({"x": [], "y": []})
            continue
            
        # Iterate over pairs of points (e.g., (Start, Rack 1), (Rack 1, Rack 5), ...)
        for i in range(len(coord_path) - 1):
            start_point = coord_path[i]
            end_point = coord_path[i+1]
            
            # --- Interpolation ---
            # Create a smooth path between the two points
            interp_x = np.linspace(start_point['x'], end_point['x'], steps_between)
            interp_y = np.linspace(start_point['y'], end_point['y'], steps_between)
            
            route_x_frames.extend(interp_x)
            route_y_frames.extend(interp_y)

            # --- Dwell Time ---
            # Add pause frames at the destination (unless it's the final return to depot)
            if i < len(coord_path) - 2: # Don't pause at the end
                route_x_frames.extend([end_point['x']] * dwell_time)
                route_y_frames.extend([end_point['y']] * dwell_time)
        
        route_frames_data.append({"x": route_x_frames, "y": route_y_frames})
        
        # Track the longest animation
        if len(route_x_frames) > max_frames:
            max_frames = len(route_x_frames)

    # --- Sync Animations ---
    # All animations must have the same number of frames.
    # We "pad" the shorter routes by making them wait at their final stop (the depot).
    for i, route_data in enumerate(route_frames_data):
        num_frames = len(route_data["x"])
        if num_frames == 0:
            route_data["x"] = [start_coords['x']] * max_frames
            route_data["y"] = [start_coords['y']] * max_frames
            continue
            
        if num_frames < max_frames:
            padding_needed = max_frames - num_frames
            final_x = route_data["x"][-1]
            final_y = route_data["y"][-1]
            
            route_data["x"].extend([final_x] * padding_needed)
            route_data["y"].extend([final_y] * padding_needed)

            
    # 2. --- Create the Plotly Figure ---
    
    fig = go.Figure(
        layout=go.Layout(
            title="Warehouse Simulation: 1 Inefficient vs. 4 Optimized Workers",
            xaxis=dict(title="X Coordinate", range=[layout_df['x'].min()-5, layout_df['x'].max()+5]),
            yaxis=dict(title="Y Coordinate", range=[layout_df['y'].min()-5, layout_df['y'].max()+5]),
            hovermode="closest",
            # Add a "Time Step" slider
            sliders=[dict(
                active=0,
                steps=[dict(label=f"Time: {k}",
                            method="animate",
                            args=[[f"frame{k}"],
                                  dict(mode="immediate",
                                       frame=dict(duration=50, redraw=False),
                                       transition=dict(duration=0))])
                       for k in range(max_frames)],
                pad=dict(t=50, b=10)
            )],
            # Add play/pause button
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {
                        "label": "► Play",
                        "method": "animate",
                        "args": [None, dict(frame=dict(duration=50, redraw=False),
                                            fromcurrent=True,
                                            transition=dict(duration=0, easing="linear"))]
                    },
                    {
                        "label": "■ Pause",
                        "method": "animate",
                        "args": [[None], dict(mode="immediate",
                                              frame=dict(duration=0, redraw=False),
                                              transition=dict(duration=0))]
                    }
                ],
                "direction": "left", "pad": dict(r=10, t=70),
                "showactive": False, "x": 0.1, "xanchor": "right", "y": 0, "yanchor": "top"
            }]
        )
    )

    # 3. --- Add Static Traces (Layout, Paths) ---
    
    # Racks (background)
    racks = layout_df[layout_df['Location'] != 'Start']
    fig.add_trace(go.Scatter(
        x=racks['x'], y=racks['y'],
        mode='markers+text', name='Racks',
        marker=dict(color='lightgrey', size=8),
        text=racks['Location'].apply(lambda x: x.split(' ')[1] if 'Rack' in x else ''), # Show only '1', '2', etc.
        textposition='middle center',
        textfont=dict(size=8, color='black'),
        hoverinfo='none'
    ))
    
    # Depot (Start)
    depot = layout_df[layout_df['Location'] == 'Start']
    fig.add_trace(go.Scatter(
        x=depot['x'], y=depot['y'],
        mode='markers', name='Depot',
        marker=dict(color='black', size=15, symbol='star'),
        hoverinfo='none'
    ))

    # Add static route path lines (the "snail trails")
    for i, route in enumerate(route_definitions):
        fig.add_trace(go.Scatter(
            x=[c['x'] for c in route["coords"]],
            y=[c['y'] for c in route["coords"]],
            mode='lines',
            name=f'{route["name"]} Path',
            line=dict(color=route["color"], width=1, dash='dot'),
            opacity=0.5
        ))

    # 4. --- Add Animated Traces ("Trucks") ---
    # These are the markers that will actually move.
    # We only add their *starting position* here.
    trace_indices = []
    for i, route in enumerate(route_definitions):
        fig.add_trace(go.Scatter(
            x=[route_frames_data[i]["x"][0]],
            y=[route_frames_data[i]["y"][0]],
            mode='markers',
            name=route["name"],
            marker=dict(color=route["color"], size=12, symbol=route["symbol"],
                        line=dict(width=2, color='black'))
        ))
        # Keep track of which trace index this is.
        # It's (number of static traces) + i
        trace_indices.append(len(fig.data) - 1)

    # 5. --- Create and Add Frames ---
    frames = []
    for k in range(max_frames):
        frame_data = []
        # For each frame, create new data for each "truck"
        for i, trace_index in enumerate(trace_indices):
            frame_data.append(go.Scatter(
                x=[route_frames_data[i]["x"][k]],
                y=[route_frames_data[i]["y"][k]]
            ))
        
        frames.append(go.Frame(
            name=f"frame{k}",
            data=frame_data,
            traces=trace_indices # This tells Plotly which traces to update
        ))

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
