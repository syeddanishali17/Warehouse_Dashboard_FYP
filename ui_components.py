"""
UI Components Module
Contains reusable UI components and visualizations for the Warehouse Dashboard.
"""
import plotly.graph_objects as go
import numpy as np


def create_multi_route_animation(layout_df, route_definitions, steps_between=5, dwell_time=3):
    """
    Creates an advanced, multi-vehicle animation with interpolation, dwell time,
    progress tracking, and visual feedback.

    Args:
        layout_df: DataFrame with warehouse layout (for background).
        route_definitions: A list of route dictionaries.
                           Each dict has "name", "color", "symbol", "coords".
        steps_between: Number of interpolation steps between stops (for smooth movement).
        dwell_time: Number of frames to pause at each stop (to simulate picking).
    """

    # 1. --- Prepare Animation Data with Progress Tracking ---
    
    route_frames_data = []
    route_progress = []  # Track which stop each worker is at
    max_frames = 0

    # Get start coords from layout
    start_row = layout_df[layout_df['Location'] == 'Start']
    if start_row.empty:
        start_coords = {'x': 0, 'y': 0}
    else:
        start_coords = {'x': start_row.iloc[0]['x'], 'y': start_row.iloc[0]['y']}

    for route in route_definitions:
        route_x_frames = []
        route_y_frames = []
        progress_frames = []  # Which stop number for this frame
        is_picking_frames = []  # Is worker picking? (for visual feedback)
        
        coord_path = route["coords"]
        
        if not coord_path:
            route_frames_data.append({"x": [], "y": [], "progress": [], "picking": []})
            continue
        
        stop_number = 0
        total_stops = len(coord_path) - 2  # Exclude start and return to depot
            
        # Iterate over pairs of points
        for i in range(len(coord_path) - 1):
            start_point = coord_path[i]
            end_point = coord_path[i+1]
            
            # --- Interpolation (Moving) ---
            interp_x = np.linspace(start_point['x'], end_point['x'], steps_between)
            interp_y = np.linspace(start_point['y'], end_point['y'], steps_between)
            
            route_x_frames.extend(interp_x)
            route_y_frames.extend(interp_y)
            progress_frames.extend([stop_number] * steps_between)
            is_picking_frames.extend([False] * steps_between)

            # Update stop number (don't count depot as a stop)
            if i > 0 and i < len(coord_path) - 1:
                stop_number += 1
            
            # --- Dwell Time (Picking) ---
            if i < len(coord_path) - 2:  # Don't pause at final depot
                route_x_frames.extend([end_point['x']] * dwell_time)
                route_y_frames.extend([end_point['y']] * dwell_time)
                progress_frames.extend([stop_number] * dwell_time)
                is_picking_frames.extend([True] * dwell_time)  # Mark as picking
        
        route_frames_data.append({
            "x": route_x_frames, 
            "y": route_y_frames,
            "progress": progress_frames,
            "picking": is_picking_frames,
            "total_stops": total_stops
        })
        
        if len(route_x_frames) > max_frames:
            max_frames = len(route_x_frames)

    # --- Sync Animations ---
    for i, route_data in enumerate(route_frames_data):
        num_frames = len(route_data["x"])
        if num_frames == 0:
            route_data["x"] = [start_coords['x']] * max_frames
            route_data["y"] = [start_coords['y']] * max_frames
            route_data["progress"] = [0] * max_frames
            route_data["picking"] = [False] * max_frames
            route_data["total_stops"] = 0
            continue
            
        if num_frames < max_frames:
            padding_needed = max_frames - num_frames
            final_x = route_data["x"][-1]
            final_y = route_data["y"][-1]
            final_progress = route_data["progress"][-1]
            
            route_data["x"].extend([final_x] * padding_needed)
            route_data["y"].extend([final_y] * padding_needed)
            route_data["progress"].extend([final_progress] * padding_needed)
            route_data["picking"].extend([False] * padding_needed)  # Not picking while waiting

            
    # 2. --- Create the Plotly Figure ---
    
    fig = go.Figure(
        layout=go.Layout(
            title="Warehouse Simulation: 1 Inefficient Worker vs. 4 Optimized Workers",
            xaxis=dict(title="X Coordinate (meters)", range=[layout_df['x'].min()-5, layout_df['x'].max()+5]),
            yaxis=dict(title="Y Coordinate (meters)", range=[layout_df['y'].min()-5, layout_df['y'].max()+5]),
            hovermode="closest",
            plot_bgcolor='#f8f9fa',
            # Add a "Time Step" slider
            sliders=[dict(
                active=0,
                steps=[dict(
                    label=f"Step {k}/{max_frames}",
                    method="animate",
                    args=[[f"frame{k}"],
                          dict(mode="immediate",
                               frame=dict(duration=40, redraw=True),
                               transition=dict(duration=0))])
                       for k in range(max_frames)],
                pad=dict(t=50, b=10),
                currentvalue=dict(prefix="Time Step: ", visible=True, xanchor="center")
            )],
            # Add play/pause button
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [None, dict(frame=dict(duration=40, redraw=True),
                                            fromcurrent=True,
                                            transition=dict(duration=0))]
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [[None], dict(mode="immediate",
                                              frame=dict(duration=0, redraw=True),
                                              transition=dict(duration=0))]
                    },
                    {
                        "label": "⏮ Reset",
                        "method": "animate",
                        "args": [["frame0"], dict(mode="immediate",
                                                   frame=dict(duration=0, redraw=True),
                                                   transition=dict(duration=0))]
                    }
                ],
                "direction": "left", 
                "pad": dict(r=10, t=70),
                "showactive": True, 
                "x": 0.15, 
                "xanchor": "right", 
                "y": 0, 
                "yanchor": "top",
                "bgcolor": "#2c3e50",
                "font": dict(color="white")
            }]
        )
    )

    # 3. --- Add Static Traces (Layout, Paths) ---
    
    # Add warehouse zone labels as shapes
    # Aisle 1 (y=10)
    fig.add_annotation(x=-25, y=10, text="AISLE 1", showarrow=False,
                      font=dict(size=10, color="gray"), xanchor="right")
    # Aisle 2 (y=20)
    fig.add_annotation(x=-25, y=20, text="AISLE 2", showarrow=False,
                      font=dict(size=10, color="gray"), xanchor="right")
    # Aisle 3 (y=30)
    fig.add_annotation(x=-25, y=30, text="AISLE 3", showarrow=False,
                      font=dict(size=10, color="gray"), xanchor="right")
    
    # Racks (background)
    racks = layout_df[layout_df['Location'] != 'Start']
    fig.add_trace(go.Scatter(
        x=racks['x'], y=racks['y'],
        mode='markers+text', name='Racks',
        marker=dict(color='#ecf0f1', size=10, line=dict(color='#bdc3c7', width=1)),
        text=racks['Location'].apply(lambda x: x.split(' ')[1] if 'Rack' in str(x) else ''),
        textposition='middle center',
        textfont=dict(size=7, color='#7f8c8d'),
        hoverinfo='skip',
        showlegend=False
    ))
    
    # Depot (Start)
    depot = layout_df[layout_df['Location'] == 'Start']
    fig.add_trace(go.Scatter(
        x=depot['x'], y=depot['y'],
        mode='markers+text', name='DEPOT',
        marker=dict(color='#f39c12', size=20, symbol='star'),
        text=['DEPOT'],
        textposition='bottom center',
        textfont=dict(size=10, color='#f39c12', family='Arial Black'),
        hoverinfo='skip',
        showlegend=False
    ))

    # Add static route path lines with better styling
    for i, route in enumerate(route_definitions):
        fig.add_trace(go.Scatter(
            x=[c['x'] for c in route["coords"]],
            y=[c['y'] for c in route["coords"]],
            mode='lines',
            name=f'{route["name"]} Path',
            line=dict(color=route["color"], width=2, dash='dot'),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))

    # 4. --- Add Animated Traces ("Trucks") with Initial State ---
    trace_indices = []
    for i, route in enumerate(route_definitions):
        # Different marker sizes for better differentiation
        size = 18 if i == 0 else 14  # Red worker slightly bigger
        
        fig.add_trace(go.Scatter(
            x=[route_frames_data[i]["x"][0]],
            y=[route_frames_data[i]["y"][0]],
            mode='markers+text',
            name=route["name"],
            marker=dict(
                color=route["color"], 
                size=size, 
                symbol=route["symbol"],
                line=dict(width=2, color='white')
            ),
            text=[f'🚚'],
            textfont=dict(size=16),
            hoverinfo='text',
            hovertext=f'{route["name"]}<br>Stop: 0/{route_frames_data[i]["total_stops"]}'
        ))
        trace_indices.append(len(fig.data) - 1)

    # 5. --- Create Frames with Enhanced Visual Feedback ---
    frames = []
    for k in range(max_frames):
        frame_data = []
        annotations = []
        
        for i, trace_index in enumerate(trace_indices):
            # Check if this worker is picking (dwelling)
            is_picking = route_frames_data[i]["picking"][k]
            progress = route_frames_data[i]["progress"][k]
            total = route_frames_data[i]["total_stops"]
            
            # VISUAL FEEDBACK: Make marker larger and add pulsing effect during picking
            if is_picking:
                size = 22 if i == 0 else 18  # Larger when picking
                text = '📦'  # Show box emoji when picking
            else:
                size = 18 if i == 0 else 14
                text = '🚚'  # Show truck when moving
            
            # Check if worker is finished (at depot and done with all stops)
            is_finished = (progress >= total and 
                          abs(route_frames_data[i]["x"][k] - start_coords['x']) < 1 and
                          abs(route_frames_data[i]["y"][k] - start_coords['y']) < 1)
            
            if is_finished and k > 50:  # Don't show at start
                text = '✅'  # Show checkmark when finished
                size = 20
            
            frame_data.append(go.Scatter(
                x=[route_frames_data[i]["x"][k]],
                y=[route_frames_data[i]["y"][k]],
                text=[text],
                marker=dict(size=size),
                hovertext=f'{route_definitions[i]["name"]}<br>Stop: {progress}/{total}'
            ))
            
            # Add progress annotation for each worker
            annotation_text = f"{route_definitions[i]['name']}: {progress}/{total}"
            if is_finished and k > 50:
                annotation_text += " ✓ DONE"
            
            # Position annotations vertically on the right side
            annotations.append(dict(
                text=annotation_text,
                xref="paper", yref="paper",
                x=1.02, y=0.95 - (i * 0.08),
                xanchor='left', yanchor='top',
                showarrow=False,
                bgcolor=route_definitions[i]["color"],
                font=dict(color='white', size=10, family='Arial'),
                bordercolor='white',
                borderwidth=1,
                borderpad=4,
                opacity=0.9
            ))
        
        frames.append(go.Frame(
            name=f"frame{k}",
            data=frame_data,
            traces=trace_indices,
            layout=go.Layout(annotations=annotations)
        ))

    fig.frames = frames
    
    # Add initial annotations
    initial_annotations = list(fig.layout.annotations) if fig.layout.annotations else []
    for i, route in enumerate(route_definitions):
        initial_annotations.append(dict(
            text=f"{route['name']}: 0/{route_frames_data[i]['total_stops']}",
            xref="paper", yref="paper",
            x=1.02, y=0.95 - (i * 0.08),
            xanchor='left', yanchor='top',
            showarrow=False,
            bgcolor=route["color"],
            font=dict(color='white', size=10, family='Arial'),
            bordercolor='white',
            borderwidth=1,
            borderpad=4,
            opacity=0.9
        ))
    
    fig.update_layout(
        annotations=initial_annotations,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        ),
        margin=dict(r=200)  # Make room for annotations
    )
    
    return fig
