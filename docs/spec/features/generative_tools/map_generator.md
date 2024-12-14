# Map Generator Specification

## Overview
The Map Generator is a tool for creating randomized board game maps with configurable node types and connections.

## Features

### Node Types
1. Start Nodes
   - Beginning points for players
   - Always accessible from other nodes
   - Typically 1 per map

2. Boss Nodes
   - End-game encounter locations
   - Strategically placed far from start
   - Limited number per map

3. Mini-Boss Nodes
   - Medium difficulty encounter locations
   - Distributed throughout the map
   - Multiple instances allowed

4. Shop Nodes
   - Resource/item exchange points
   - Evenly distributed
   - Configurable quantity

5. Event Nodes
   - Random encounter locations
   - Scattered throughout the map
   - Flexible quantity

6. Neutral Nodes
   - Basic movement spaces
   - Fill remaining positions
   - Automatic quantity calculation

## Configuration Parameters

### Required Parameters
- `num_points`: Total number of nodes (default: 30)
- `radius_range`: Min/max node size (default: 1-10)
- `min_distance`: Minimum space between nodes (default: 1.5)

### Optional Parameters
- Node type quantities
- Connection rules
- Map dimensions

## Algorithm

### Node Placement
1. Generate random positions
2. Apply minimum distance rules
3. Ensure connectivity
4. Assign node types

### Connection Rules
- Each node connects to exactly two others
- No crossing connections
- Guaranteed path from start to boss

## Output Format

### Visual Output
- PNG image with:
  - Colored nodes by type
  - Connection lines
  - Optional grid overlay

### Data Output
- Node positions
- Node types
- Connection map
- Generation parameters