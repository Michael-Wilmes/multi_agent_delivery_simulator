## The graph is the model of the map. ##  
The key idea is:

A cell on the map becomes a node
Each node has:
a position: (x, y)
a kind: road, wall, depot, or target
an optional label
Only walkable cells are connected to neighbors
The important parts
- NodeKind defines the meaning of cells:
  - ROAD
  - WALL
  - DEPOT
  - TARGET

- GraphNode represents one tile:
  - position
  - kind
  - label
  - walkable is True unless the node is a wall

- GraphMap stores:
  - width
  - height
  - name
  - nodes: all grid positions mapped to their node
  - adjacency: neighbor connections for each node
  - rebuild_edges() creates edges between adjacent tiles:

it looks right and down
only connects walkable tiles
this creates the movement graph
reachable_from(start) does a depth-first traversal to find all connected walkable positions


##  Why this matters for the simulation ? ##  
The simulator later does things like:

- find free road positions
- generate agents on walkable nodes
- move agents along graph edges
- find depots and targets
- decide whether positions are reachable
- So the graph is the navigation backbone of the app.  

