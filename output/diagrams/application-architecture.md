# Multi-Agent Delivery Simulator — Architecture

```mermaid
flowchart LR
    User[User / Keyboard / Mouse] --> Main[main.py]
    Main --> Config[app/config.py\nAppConfig + validation]
    Config --> JSON[config/app.json]

    Main --> Engine[app/simulation/engine.py\nSimulationEngine]
    Main --> UI[app/ui/app.py\nSimulatorApp]

    Engine --> GraphFactory[app/maps/factory.py\ncreate_graph_map]
    GraphFactory --> MapPreset[Map Presets / Random Map Generator]
    MapPreset --> Graph[GraphMap + Nodes + Depots + Destinations]

    Engine --> Agents[Agent[]\napp/domain/entities/agent.py]
    Engine --> Tasks[DeliveryTask[]]
    Engine --> Depots[Depot[]]
    Engine --> ContractMgr[ContractNetManager\napp/domain/services/contractnetmanager.py]
    Engine --> KPI[KpiRecorder\napp/simulation/kpi_recorder.py]

    ContractMgr --> BidCalc[BidCalculator]
    ContractMgr --> Events[ContractNetMessage events]
    Events --> Agents
    Agents --> Notifications[Agent notifications / bids / awards]
    Notifications --> ContractMgr

    Tasks --> DepotTasks[Depot task queue]
    Depots --> Tasks
    Agents --> Move[Movement / pickup / delivery logic]
    Graph --> Move

    UI --> Snapshot[Simulation snapshot]
    Engine --> Snapshot
    Snapshot --> Render[Map rendering + panels + controls]
    Render --> User

    Engine --> Tick[Tick loop\nstep() / add_agent() / add_task()]
    Tick --> CONTRACT[Contract-Net award cycle]
    CONTRACT --> KPI
    Tick --> KPI

    classDef core fill:#dfe8ff,stroke:#3657c8,color:#111827
    classDef domain fill:#eafaf1,stroke:#2d8f60,color:#111827
    classDef ui fill:#fff4d6,stroke:#c58900,color:#111827
    classDef data fill:#f9e8f5,stroke:#a33fa5,color:#111827

    class Main,Engine,ContractMgr,GraphFactory,Graph,Tick core;
    class Agents,Tasks,Depots,Events,BidCalc,Notifications,DepotTasks domain;
    class UI,Render,Snapshot data;
    class Config,JSON,KPI ui;
```

## Runtime flow

1. `main.py` loads configuration and creates the `SimulationEngine`.
2. The engine builds a graph map and validates map size / depot count.
3. Agents and tasks are created, and `ContractNetManager` coordinates bidding/awards.
4. `SimulatorApp` renders the live simulation, controls, and contract log.
5. KPIs are recorded in `kpis/` while the simulation advances tick by tick.

## Main application responsibilities

- Simulation core: `app/simulation/engine.py`
- Domain model: `app/domain/entities/` and `app/domain/services/`
- Map generation: `app/maps/`
- UI layer: `app/ui/`
- Configuration: `app/config.py` and `config/app.json`
- Data output: `kpis/`
