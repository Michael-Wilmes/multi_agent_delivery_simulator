# Multi-Agent Delivery Simulator — Application Architecture

This component view follows the implementation under `output/source-code/`. For the system-level layer view, see [architecture-overview.md](architecture-overview.md).

```mermaid
flowchart TB
    Operator[Operator\nMouse and keyboard]

    subgraph Startup[Startup and configuration]
        Main[main.py\nBootstrap]
        Config[app/config.py\nLoad and validate AppConfig]
        Json[config/app.json]
    end

    subgraph UI[Presentation: app/ui/]
        App[SimulatorApp\nPygame loop, controls, rendering]
        Snapshot[SimulationSnapshot]
    end

    subgraph Core[Application core: app/simulation/]
        Engine[SimulationEngine\nstep, reset, add_agent, add_task]
        Recorder[KpiRecorder]
    end

    subgraph MapLayer[Map creation: app/maps/]
        Factory[create_graph_map]
        Sources[Presets or RandomGraphMapFactory]
        Graph[GraphMap\nNodes, roads, walls, depots, destinations]
    end

    subgraph Domain[Domain: app/domain/]
        Agents[Agent\nState, notifications, task capacity]
        Tasks[DeliveryTask\nStatus and assignment]
        Depot[Depot\nTask queue and auction entry point]
        Contract[ContractNetManager\nEvents and agent notifications]
        Bid[BidCalculator\nAnnouncements and bids]
        Award[AwardPolicy\nLowest-cost eligible bid]
        Distance[ManhattanRouteCalculator\nBid cost estimate]
    end

    Csv[(kpis/*.csv\nTask, contract, and tick metrics)]

    Operator -->|input| App
    Main --> Config
    Json --> Config
    Main --> Engine
    Main --> App
    Config -->|validated settings| Engine
    App -->|commands and timed ticks| Engine
    Engine --> Factory
    Factory --> Sources
    Sources --> Graph
    Engine --> Graph
    Engine --> Agents
    Engine --> Tasks
    Graph --> Depot
    Depot -->|submit task| Contract
    Contract --> Bid
    Bid --> Award
    Award --> Contract
    Contract -->|notifications and assignment| Agents
    Agents -->|bid estimate| Distance
    Engine -->|bid submission and lifecycle updates| Contract
    Engine -->|movement over graph neighbors| Agents
    Engine --> Recorder
    Contract -->|event records| Recorder
    Recorder --> Csv
    Engine --> Snapshot
    Snapshot --> App
    App -->|map, panels, contract log| Operator

    classDef entry fill:#dcebf2,stroke:#38677a,color:#15252d
    classDef core fill:#e9f1d9,stroke:#627b38,color:#1d2714
    classDef domain fill:#f7e8d7,stroke:#9a6534,color:#332316
    classDef output fill:#eee4f1,stroke:#775783,color:#291d2e
    class Main,Config,Engine,Factory,Graph entry
    class App,Snapshot,Recorder core
    class Sources,Agents,Tasks,Depot,Contract,Bid,Award,Distance domain
    class Csv output
```

## Runtime flow

1. `main.py` loads and validates `config/app.json`, then creates the engine and Pygame application.
2. `SimulationEngine.reset()` creates a preset or random graph, validates it, initializes the contract-net manager and KPI recorder, and creates configured agents.
3. The UI sends manual commands and timed ticks to the engine. Each tick submits pending bids, processes agent actions, creates periodic tasks, closes auctions at their deadlines, and records simulation metrics.
4. A depot announces a task through `ContractNetManager`. Agents calculate a cost estimate using `ManhattanRouteCalculator`; `BidCalculator` tracks bids and `AwardPolicy` selects the lowest-cost bid once the deadline is reached.
5. Assigned agents pick up and deliver tasks through engine-coordinated domain state changes. Movement follows graph neighbors and uses BFS distances to guide movement toward an assigned task.
6. The engine returns a `SimulationSnapshot` for rendering. `KpiRecorder` writes package creation, bidding/contract events, and per-tick metrics to CSV files in `kpis/`.

## Ownership boundaries

- `main.py` wires configuration, engine, and UI at startup.
- `app/config.py` parses JSON into typed settings and validates map/depot limits.
- `app/simulation/engine.py` owns live simulation state and coordinates ticks, movement, task lifecycle, contract-net calls, and snapshots.
- `app/domain/entities/` defines the simulation's state-bearing entities and messages. `app/domain/services/` implements auction, award, and bid-distance behavior.
- `app/maps/` constructs graph maps. `app/ui/` handles Pygame input and rendering. `app/simulation/kpi_recorder.py` persists CSV metrics.

## Current implementation note

Action selection still uses the engine's milestone random-action policy. The `ManhattanRouteCalculator` is used for bid cost estimates; movement itself is graph-based and uses BFS distances in the engine, not that calculator.
