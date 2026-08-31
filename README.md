# Multi-Agent Delivery Simulator

Complete runnable Pygame boilerplate for Aufgabe 1.

## Included
- `map1`: original 10 x 10 bottleneck map
- `map2`: original 10 x 10 two-district map
- `random`: connected 20 x 20 random map with wall segments
- Config-based map selection in `config/app.json`
- Maps are built directly as coordinate graphs with adjacency lists
- Runtime buttons: Auto, Step, Reset, Agent, Express Agent, Task
- Separate UI windows for active tasks, messages, agent state and Contract-Net log
- Collision-safe placement and movement only on walkable nodes
- Battery data exists but behaviour is disabled pending clarification

## Map selection
Set `map.type` to `map1`, `map2` or `random`. For a different random map on each start use `random_seed: null`; use an integer for reproducibility.

## Run
```bash
python -m venv .venv
python -m pip install -r requirements.txt
python main.py
```

## Academic boundary
The assessed Contract-Net, A-star and Prolog algorithms are intentionally not implemented. The windows and event models are ready for later integration.
