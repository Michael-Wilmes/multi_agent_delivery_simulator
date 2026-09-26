# Multi-Agent Delivery Simulator — C4-style Architecture

```mermaid
flowchart TB
    User[User\nOperator / Player]

    subgraph System[Multi-Agent Delivery Simulator]
        subgraph C1[Context]
            App[Simulator App\nPygame UI\napp/ui/app.py]
            Engine[Simulation Engine\nstep(), reset(), tick loop\napp/simulation/simulation_engine.py]
        end

        subgraph C2[Containers]
            Config[Configuration\napp/config.py + config/app.json]
            Maps[Map Layer\napp/maps/ + graph generation]
            Domain[Domain Model\nEntities + Services]
            Contract[Contract-Net Manager\nBid / Award / Notifications]
            KPIs[KPI Recorder\nCSV export in kpis/]
        end

        subgraph C3[Components]
            Agents[Agents\nAgentType, routes, battery, load]
            Tasks[Task Queue\nDeliveryTask, depot + destination]
            Depots[Depots\ntask submission and assignment]
            Graph[Graph Map\nwalkable nodes, walls, roads]
            BidCalc[Bid Calculator\ncalculate bids and award readiness]
            UI[Renderer & Controls\nmap, panels, buttons, logs]
        end
    end

    Data[(CSV KPI files\ncontract_net_log.csv, simulation.csv, ...)]

    User --> App
    App --> Engine
    App --> UI
    Engine --> Config
    Engine --> Maps
    Engine --> Domain
    Engine --> Contract
    Engine --> KPIs

    Maps --> Graph
    Domain --> Agents
    Domain --> Tasks
    Domain --> Depots
    Contract --> BidCalc

    Engine --> Agents
    Engine --> Tasks
    Engine --> Depots
    Engine --> Graph

    UI --> App
    KPIs --> Data

    classDef user fill:#e0f2fe,stroke:#0284c7,color:#0f172a;
    classDef app fill:#dbeafe,stroke:#2563eb,color:#0f172a;
    classDef backend fill:#dcfce7,stroke:#16a34a,color:#0f172a;
    classDef data fill:#fef3c7,stroke:#d97706,color:#0f172a;

    class User user;
    class App,Engine,Config,Maps,Domain,Contract,UI,Graph,Agents,Tasks,Depots,BidCalc app;
    class KPIs,Data data;
```

## Architecture summary

### Context
- The user interacts with a Pygame-based simulator.
- The system simulates delivery agents moving through a graph-based map.
- The application coordinates tasks, bids, and execution in a tick-based loop.

### Containers
- Configuration container loads runtime settings from JSON.
- Map container builds graph topology and map presets.
- Domain container defines agent/task/depot state and logic.
- Contract-net container manages announcements, bids, awards, and notifications.
- KPI container persists simulation metrics and logs to CSV files.

### Main responsibilities
- `main.py` bootstraps the app and creates the engine.
- `app/simulation/simulation_engine.py` orchestrates the simulation.
- `app/ui/app.py` renders the game state and handles user controls.
- `app/domain/` contains the core business/domain logic.
- `kpis/` stores contract and simulation metrics for analysis.
