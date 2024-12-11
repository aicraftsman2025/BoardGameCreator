from utils.scripts.base_script import BaseScript, ConfigWidget
import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.spatial import distance_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import customtkinter as ctk
import os
import uuid
from tkinter import filedialog

class MapGenerator(BaseScript):
    def __init__(self):
        super().__init__()
    
    def get_title(self):
        return "Generate Game Map"
    
    def get_config_widgets(self, parent):
        # Create container frame for path selection
        path_frame = ctk.CTkFrame(parent)
        path_frame.pack(fill="x", padx=5, pady=2)
        
        # Create path entry and browse button
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Select output directory..."
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._browse_output_path,
            width=60
        )
        browse_btn.pack(side="right", padx=(2, 5))
        
        # Create path widget
        path_widget = ConfigWidget(
            parent, "output_path", "Output Directory:",
            widget_type=lambda p, **k: self.path_entry
        )
        
        return [
            path_widget,
            ConfigWidget(
                parent, "num_points", "Number of Points:",
                ctk.CTkEntry, placeholder_text="50"
            ),
            ConfigWidget(
                parent, "radius_min", "Min Radius:",
                ctk.CTkEntry, placeholder_text="1"
            ),
            ConfigWidget(
                parent, "radius_max", "Max Radius:",
                ctk.CTkEntry, placeholder_text="8"
            ),
            ConfigWidget(
                parent, "min_distance", "Min Distance:",
                ctk.CTkEntry, placeholder_text="1.5"
            ),
            ConfigWidget(
                parent, "start_nodes", "Start Nodes:",
                ctk.CTkEntry, placeholder_text="1"
            ),
            ConfigWidget(
                parent, "boss_nodes", "Boss Nodes:",
                ctk.CTkEntry, placeholder_text="1"
            ),
            ConfigWidget(
                parent, "mini_boss_nodes", "Mini Boss Nodes:",
                ctk.CTkEntry, placeholder_text="3"
            ),
            ConfigWidget(
                parent, "shop_nodes", "Shop Nodes:",
                ctk.CTkEntry, placeholder_text="5"
            ),
            ConfigWidget(
                parent, "event_nodes", "Event Nodes:",
                ctk.CTkEntry, placeholder_text="5"
            )
        ]
    
    def _browse_output_path(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir="."
        )
        if directory:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, directory)
    
    def run_script(self, config):
        try:
            # Get output directory from config
            output_dir = config["output_path"].strip()
            if not output_dir:
                output_dir = os.path.join("assets", "maps")  # Default path
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Parse other config values
            num_points = int(config["num_points"] or 50)
            radius_min = float(config["radius_min"] or 1)
            radius_max = float(config["radius_max"] or 8)
            min_distance = float(config["min_distance"] or 1.5)
            
            # Parse node counts with defaults
            start_nodes = int(config["start_nodes"] or 1)
            boss_nodes = int(config["boss_nodes"] or 1)
            mini_boss_nodes = int(config["mini_boss_nodes"] or 3)
            shop_nodes = int(config["shop_nodes"] or 5)
            event_nodes = int(config["event_nodes"] or 5)
            
            # Calculate neutral nodes as remaining
            special_nodes = start_nodes + boss_nodes + mini_boss_nodes + shop_nodes + event_nodes
            if special_nodes > num_points:
                raise ValueError("Total special nodes exceeds total number of points!")
            
            # Define node configuration
            node_config = {
                'Start': start_nodes,
                'Boss': boss_nodes,
                'Mini Boss': mini_boss_nodes,
                'Shop': shop_nodes,
                'Event': event_nodes,
                'Neutral': num_points - special_nodes  # Remaining nodes will be neutral
            }
            
            # Generate unique filename and final path
            filename = f"map-{uuid.uuid4().hex[:8]}.png"
            output_path = os.path.join(output_dir, filename)
            
            # Generate and save the map
            self.draw_board(
                num_points=num_points,
                radius_range=(radius_min, radius_max),
                min_distance=min_distance,
                config=node_config,
                output_path=output_path
            )
            
            self.output.insert("end", f"Map saved to: {output_path}\n")
            
        except Exception as e:
            self.output.insert("end", f"Error: {str(e)}\n")
    
    def generate_random_points(self, num_points, radius_range=(1, 10), min_distance=1.5, max_attempts=10000):
        """Generate random points within a given radius range and ensure minimum distance between points.
           Add a cap on attempts to prevent infinite loops.
        """
        points = []
        attempts = 0
        while len(points) < num_points:
            attempts += 1
            if attempts > max_attempts:
                raise RuntimeError(
                    f"Could not place {num_points} points with min_distance={min_distance} "
                    f"and radius_range={radius_range} after {max_attempts} attempts. "
                    "Try adjusting parameters."
                )
            radius = random.uniform(*radius_range)
            angle = random.uniform(0, 2 * np.pi)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            # Check minimum distance
            if all(np.sqrt((x - px) ** 2 + (y - py) ** 2) > min_distance for px, py in points):
                points.append((x, y))
        return points

    def ensure_two_connections(self, points, max_tries=5000):
        """Ensure each point is connected to exactly two other points.
           Add a limit to prevent infinite loops if conditions can't be met.
        """
        dist_matrix = distance_matrix(points, points)
        # Generate the Minimum Spanning Tree (MST)
        mst = minimum_spanning_tree(dist_matrix).toarray().astype(float)
        edges = set()

        # Extract edges from the MST
        for i in range(len(points)):
            for j in range(len(points)):
                if mst[i, j] > 0:
                    edges.add((i, j))

        connections = {i: 0 for i in range(len(points))}  # Track connections per node
        for i, j in edges:
            connections[i] += 1
            connections[j] += 1

        # Attempt to add edges until all have at least 2 connections
        tries = 0
        while any(conn < 2 for conn in connections.values()):
            tries += 1
            if tries > max_tries:
                raise RuntimeError(
                    "Could not ensure all points have two connections. "
                    "Try adjusting the number of points or spacing constraints."
                )
            for i in range(len(points)):
                if connections[i] < 2:
                    # Find a node to connect with that also has < 2 connections
                    # We'll try closest nodes first for efficiency
                    for j in np.argsort(dist_matrix[i]):
                        if i != j and connections[j] < 2:
                            # Add this edge if not already present
                            if (i, j) not in edges and (j, i) not in edges:
                                edges.add((i, j))
                                connections[i] += 1
                                connections[j] += 1
                                break

        return [(points[i], points[j]) for i, j in edges]

    def assign_node_types(self, points, config):
        """Assign a type to each point (node) based on the configuration."""
        total_points = len(points)
        
        # Calculate available types
        type_order = []
        for node_type, count in config.items():
            type_order.extend([node_type] * count)
        
        # If we don't have enough types, pad with Neutral
        if len(type_order) < total_points:
            type_order.extend(["Neutral"] * (total_points - len(type_order)))
        
        # Shuffle to randomize distribution
        random.shuffle(type_order)

        assigned_types = type_order[:total_points]
        return assigned_types

    def draw_board(self, num_points=30, radius_range=(1, 10), min_distance=1.5, config=None, output_path=None):
        """Draw a randomized board with points connected to exactly two other points in a connected graph."""
        # Default configuration
        if config is None:
            config = {
                'Start': 1,
                'Boss': 1,
                'Mini Boss': 3,
                'Shop': 5,
                'Event': 5,
                'Neutral': num_points - 15
            }

        # Ensure the total number of types matches the number of points (or less)
        total_configured = sum(config.values())
        if total_configured > num_points:
            raise ValueError("Total configured types exceed the number of points!")

        # Generate random points with minimum distance
        points = self.generate_random_points(num_points, radius_range, min_distance)

        # Ensure each point connects to exactly two others
        edges = self.ensure_two_connections(points)

        # Assign types to points
        node_types = self.assign_node_types(points, config)

        # Define colors for each type
        type_colors = {
            'Start': 'green',
            'Neutral': 'blue',
            'Event': 'yellow',
            'Shop': 'purple',
            'Mini Boss': 'orange',
            'Boss': 'red'
        }

        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor('none')  # Transparent background
        ax.axis("off")  # Turn off axes

        # Plot the points (colored by type)
        for (x, y), node_type in zip(points, node_types):
            ax.add_artist(plt.Circle((x, y), 0.3, color=type_colors.get(node_type, 'blue'), zorder=3))

        # Plot the edges (white lines connecting points)
        for (x1, y1), (x2, y2) in edges:
            ax.plot([x1, x2], [y1, y2], color='white', lw=2, zorder=2)

        # Add a legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=type_colors[type_], markersize=10, label=type_)
            for type_ in type_colors
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=False)

        # Save the final plot
        plt.axis("equal")  # Keep aspect ratio
        plt.savefig(output_path, dpi=300, bbox_inches="tight", transparent=True)
        plt.close()  # Close the figure to free memory
        print(f"Map saved to {output_path}")

def main():
    return MapGenerator()
