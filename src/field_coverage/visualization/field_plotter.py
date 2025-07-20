"""
Field plotting and visualization for coverage planning.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MPLPolygon
import numpy as np
from typing import List, Optional, Tuple, Union
import os

from ..core.field import Field
from ..core.waypoint import WaypointSequence


class FieldPlotter:
    """Visualizes fields, boundaries, and coverage paths."""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the field plotter.
        
        Args:
            figsize: Figure size (width, height) in inches
        """
        self.figsize = figsize
        self.fig = None
        self.ax = None
        
    def setup_plot(self, title: str = "Field Coverage Plan") -> None:
        """Setup the matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_title(title, fontsize=16, fontweight='bold')
        self.ax.set_xlabel('Longitude (°)', fontsize=12)
        self.ax.set_ylabel('Latitude (°)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
    def plot_field_boundary(self, field: Field, color: str = 'blue', 
                          linewidth: float = 2.0, alpha: float = 0.3) -> None:
        """
        Plot the field boundary.
        
        Args:
            field: Field object to plot
            color: Boundary color
            linewidth: Line width for boundary
            alpha: Fill transparency
        """
        if self.ax is None:
            self.setup_plot()
            
        # Get GPS coordinates of boundary
        coords = []
        for coord in field.main_boundary.gps_coordinates:
            coords.append([coord.longitude, coord.latitude])
        
        # Close the polygon
        if coords and coords[0] != coords[-1]:
            coords.append(coords[0])
            
        coords = np.array(coords)
        
        # Plot boundary
        polygon = MPLPolygon(coords, fill=True, alpha=alpha, 
                           facecolor=color, edgecolor=color, 
                           linewidth=linewidth, label='Field Boundary')
        self.ax.add_patch(polygon)
        
        # Plot boundary points
        self.ax.plot(coords[:, 0], coords[:, 1], 'o', 
                    color=color, markersize=6, label='Boundary Points')
        
    def plot_coverage_path(self, waypoints: WaypointSequence, 
                          color: str = 'red', linewidth: float = 1.0,
                          show_waypoints: bool = True, 
                          waypoint_size: float = 2.0) -> None:
        """
        Plot the coverage path.
        
        Args:
            waypoints: WaypointSequence to plot
            color: Path color
            linewidth: Line width for path
            show_waypoints: Whether to show individual waypoints
            waypoint_size: Size of waypoint markers
        """
        if self.ax is None:
            self.setup_plot()
            
        if len(waypoints.waypoints) == 0:
            return
            
        # Extract coordinates
        lons = [wp.gps_coordinate.longitude for wp in waypoints.waypoints]
        lats = [wp.gps_coordinate.latitude for wp in waypoints.waypoints]
        
        # Plot path
        self.ax.plot(lons, lats, color=color, linewidth=linewidth, 
                    alpha=0.7, label='Coverage Path')
        
        # Plot waypoints if requested
        if show_waypoints:
            self.ax.plot(lons, lats, 'o', color=color, 
                        markersize=waypoint_size, alpha=0.6, 
                        label='Waypoints')
            
        # Highlight start and end points
        if len(waypoints.waypoints) > 0:
            start_wp = waypoints.waypoints[0]
            end_wp = waypoints.waypoints[-1]
            
            self.ax.plot(start_wp.gps_coordinate.longitude, 
                        start_wp.gps_coordinate.latitude, 
                        'o', color='green', markersize=8, 
                        label='Start Point')
            
            self.ax.plot(end_wp.gps_coordinate.longitude, 
                        end_wp.gps_coordinate.latitude, 
                        's', color='orange', markersize=8, 
                        label='End Point')
    
    def plot_swath_lines(self, field: Field, waypoints: WaypointSequence,
                        swath_width: float, color: str = 'gray',
                        alpha: float = 0.2) -> None:
        """
        Plot swath coverage areas.
        
        Args:
            field: Field object
            waypoints: Waypoint sequence
            swath_width: Width of each swath in meters
            color: Swath color
            alpha: Transparency
        """
        if self.ax is None:
            self.setup_plot()
            
        # This is a simplified visualization
        # In a real implementation, you'd calculate actual swath polygons
        # For now, we'll just show the concept with lines
        
        # Group waypoints into swaths (simplified approach)
        if len(waypoints.waypoints) < 2:
            return
            
        # Calculate approximate swath direction from first few waypoints
        wp1 = waypoints.waypoints[0]
        wp2 = waypoints.waypoints[min(10, len(waypoints.waypoints)-1)]
        
        # Add a simple note about swath visualization
        self.ax.text(0.02, 0.98, f'Swath Width: {swath_width}m', 
                    transform=self.ax.transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                    verticalalignment='top')
    
    def add_statistics(self, field: Field, waypoints: WaypointSequence,
                      total_distance: float, estimated_time: float) -> None:
        """
        Add statistics text box to the plot.
        
        Args:
            field: Field object
            waypoints: Waypoint sequence
            total_distance: Total path distance in meters
            estimated_time: Estimated time in minutes
        """
        if self.ax is None:
            return
            
        stats_text = (
            f"Field Area: {field.calculate_area():.1f} m²\n"
            f"Waypoints: {len(waypoints.waypoints)}\n"
            f"Path Distance: {total_distance:.1f} m\n"
            f"Est. Time: {estimated_time:.1f} min"
        )
        
        self.ax.text(0.02, 0.02, stats_text, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='bottom',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    def add_legend(self, loc: str = 'upper right') -> None:
        """Add legend to the plot."""
        if self.ax is None:
            return
        self.ax.legend(loc=loc, fontsize=10)
    
    def save_plot(self, filename: str, dpi: int = 300, 
                  bbox_inches: str = 'tight') -> None:
        """
        Save the plot to file.
        
        Args:
            filename: Output filename
            dpi: Resolution in dots per inch
            bbox_inches: Bounding box setting
        """
        if self.fig is None:
            return
            
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', 
                   exist_ok=True)
        
        self.fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        print(f"Plot saved to: {filename}")
    
    def show(self) -> None:
        """Display the plot."""
        if self.fig is None:
            return
        plt.tight_layout()
        plt.show()
    
    def close(self) -> None:
        """Close the plot."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
    
    def plot_complete_coverage(self, field: Field, waypoints: WaypointSequence,
                             swath_width: float, total_distance: float,
                             estimated_time: float, title: str = None,
                             save_path: str = None, show: bool = True) -> None:
        """
        Create a complete coverage visualization.
        
        Args:
            field: Field object
            waypoints: Waypoint sequence
            swath_width: Swath width in meters
            total_distance: Total path distance
            estimated_time: Estimated time in minutes
            title: Plot title
            save_path: Path to save the plot
            show: Whether to display the plot
        """
        # Setup plot
        if title is None:
            title = f"Field Coverage Plan - {field.field_id}"
        self.setup_plot(title)
        
        # Plot field boundary
        self.plot_field_boundary(field)
        
        # Plot coverage path
        self.plot_coverage_path(waypoints, show_waypoints=False)
        
        # Add statistics
        self.add_statistics(field, waypoints, total_distance, estimated_time)
        
        # Add legend
        self.add_legend()
        
        # Save if requested
        if save_path:
            self.save_plot(save_path)
        
        # Show plot only if requested
        if show:
            self.show()


def create_coverage_visualization(field: Field, waypoints: WaypointSequence,
                                swath_width: float, total_distance: float,
                                estimated_time: float, output_path: str = None,
                                show: bool = True) -> str:
    """
    Convenience function to create a complete coverage visualization.
    
    Args:
        field: Field object
        waypoints: Waypoint sequence
        swath_width: Swath width in meters
        total_distance: Total path distance
        estimated_time: Estimated time in minutes
        output_path: Path to save the plot (optional)
        show: Whether to display the plot
    
    Returns:
        Path where the plot was saved (if saved)
    """
    plotter = FieldPlotter()
    
    try:
        title = f"Coverage Plan - {field.field_id}"
        plotter.plot_complete_coverage(
            field=field,
            waypoints=waypoints,
            swath_width=swath_width,
            total_distance=total_distance,
            estimated_time=estimated_time,
            title=title,
            save_path=output_path,
            show=show
        )
        
        if not show:
            plotter.close()
            
        return output_path if output_path else None
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        plotter.close()
        return None
