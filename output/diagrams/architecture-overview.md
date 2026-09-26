# Multi-Agent Delivery Simulator — Architecture Overview

This overview describes the running application at the system boundary and shows how its major layers collaborate. The detailed component flow is in [application-architecture.md](application-architecture.md).

```mermaid
flowchart TB
    Operator[Operator\nMouse and keyboard]
    ConfigFile[config/app.json\nRuntime settings]
    KPIFiles[(kpis/*.csv\nPackage, bidding, contract, tick metrics)]

    subgraph Application[Multi-Agent Delivery Simulator]
        subgraph Presentation[Presentation]
            UI[SimulatorApp\nPygame controls and visualization]
            Snapshot[SimulationSnapshot\nRead-only view of current state]
        end

        subgraph ApplicationCore[Application orchestration]
            Bootstrap[main.py\nStartup and dependency wiring]
            Config[AppConfig\nLoad and validate settings]
            Engine[SimulationEngine\nTick loop and live simulation state]
            Recorder[KpiRecorder\nCSV persistence]
        end

        subgraph MapLayer[Map generation]
            MapFactory[create_graph_map]
            MapSources[Preset maps or\nRandomGraphMapFactory]
        end

        subgraph Domain[Simulation domain]
            Graph[GraphMap\nNodes, roads, walls, depots, destinations]
            Agents[Agents\nPosition, capacity, battery, notifications]
            Tasks[Delivery tasks\nAssignment and lifecycle]
            ContractNet[ContractNetManager\nAnnouncements, bids, awards]
            BidCalc[BidCalculator\nAnnouncements and bid collection]
            AwardPolicy[AwardPolicy\nDeadline and lowest-cost decision]
            RouteCalc[ManhattanRouteCalculator\nBid cost estimate]
        end
    end

    Operator -->|input| UI
    UI -->|commands and timed ticks| Engine
    Bootstrap --> Config
    ConfigFile --> Config
    Bootstrap --> Engine
    Bootstrap --> UI
    Config -->|map and simulation settings| Engine
    Engine --> MapFactory
    MapFactory --> MapSources
    MapSources --> Graph
    Engine --> Graph
    Engine --> Agents
    Engine --> Tasks
    Engine --> ContractNet
    ContractNet --> BidCalc
    BidCalc --> AwardPolicy
    AwardPolicy -->|award outcome| ContractNet
    ContractNet <-->|task assignment and notifications| Agents
    Agents -->|estimate delivery cost| RouteCalc
    RouteCalc -->|distance estimate| Engine
    Engine -->|submit bids and coordinate task lifecycle| ContractNet
    Engine -->|graph-based movement and task lifecycle| Agents
    Engine -->|task, contract, and tick metrics| Recorder
    Recorder --> KPIFiles
    Engine --> Snapshot
    Snapshot --> UI
    UI -->|map, agents, tasks, event log| Operator
```

## Architectural boundaries

- **Presentation:** `app/ui/` owns the Pygame event loop, controls, and rendering. It sends user commands to the engine and renders an engine snapshot.
- **Application core:** `main.py` loads configuration and wires the UI to `SimulationEngine`. The engine owns the tick loop and coordinates live state, tasks, auctions, and snapshots.
- **Map generation:** `app/maps/` creates preset or random maps and returns a `GraphMap` used by the engine for placement and movement.
- **Domain:** `app/domain/entities/` holds agents, tasks, depots, destinations, graph nodes, and contract-net messages. `ContractNetManager`, `BidCalculator`, and `AwardPolicy` coordinate announcements, bid collection, and deadline-based awards. Agents use `ManhattanRouteCalculator` for bid cost estimates.
- **Persistence:** `KpiRecorder` writes package creation, bidding, contract-net events, and per-tick metrics as CSV files under `kpis/`.

## Runtime at a glance

1. Startup loads and validates `config/app.json`, then the engine asks `app/maps/` to create a preset or random graph and initializes agents.
2. The UI sends manual commands or timed ticks to the engine.
3. Each tick submits pending bids, processes agent actions and task transitions, closes auctions that reached their deadline, and records metrics.
4. The UI redraws from a snapshot; KPI data is written to CSV.

## Current implementation note

The engine currently selects agent actions through its milestone random-action policy. Movement is constrained by graph neighbors and uses BFS distances to guide assigned deliveries. Bid cost estimation uses Manhattan distance; it is separate from movement routing.
