# Multi-Agent Delivery Simulator — Sequence Diagram for One Tick

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant App as SimulatorApp
    participant Engine as SimulationEngine
    participant Graph as GraphMap
    participant Depot as Depot
    participant Contract as ContractNetManager
    participant BidCalc as BidCalculator
    participant Agent as Agent
    participant Task as DeliveryTask
    participant KPI as KpiRecorder

    User->>App: Press Auto / Step / Add Agent / Add Task
    App->>Engine: step() / toggle_running()

    Engine->>Graph: inspect map and positions
    Graph-->>Engine: walkable nodes, depots, targets

    loop each agent in shuffled order
        Engine->>Agent: submit_pending_bids(agent)

        Agent->>Contract: has_bid(taskId, agentId)
        Contract->>BidCalc: has_bid(taskId, agentId)
        BidCalc-->>Contract: bool
        Contract-->>Agent: bool

        alt there are ANNOUNCE notifications for open tasks
            Agent->>Agent: build delivery entry and task cost
            Agent->>Contract: record_bid(agentId, taskId, cost, tick)
            Contract->>BidCalc: record_bid(...)
            BidCalc->>BidCalc: append BID to bids[taskId]
            BidCalc-->>Contract: ContractNetMessage(BID)
            Contract->>KPI: record_contract_event(bid)
            Contract-->>Agent: bid recorded
        end

        alt agent is charging
            Engine->>Agent: decrement charging time
        else battery empty
            Engine->>Agent: mark_stranded()
        else at depot and task is available
            Engine->>Agent: pick_up_task()
            Agent->>Task: set status = IN_TRANSIT
            Agent->>Depot: remove_task(task)
        else default action
            Engine->>Agent: choose_random_action()
            Engine->>Agent: move_agent() / execute_action()
            Agent->>Graph: get neighbors
            Graph-->>Agent: valid positions
        end
    end

    Engine->>Engine: every 5 ticks => add_task()
    Engine->>Depot: submit_task(task, tick, deadline)
    Depot->>Contract: submit_task(task, tick, deadline)
    Contract->>BidCalc: announce_task(task, tick, deadline)
    BidCalc->>BidCalc: store announcement and initialize bids[taskId]
    BidCalc-->>Contract: ContractNetMessage(ANNOUNCE)
    Contract->>Agent: receive_notification(ANNOUNCE, task)
    Agent->>Agent: check capacity and reachability
    Agent-->>Contract: NO_BID_RESOURCES or none

    Engine->>Contract: award_ready_tasks(tasks, tick)
    Contract->>BidCalc: award_ready_tasks(tasks, tick)
    BidCalc->>BidCalc: evaluate deadline / choose winner / create AWARD + BID_LOST + NO_BID
    BidCalc-->>Contract: outcomes
    Contract->>Agent: _notify_agent(outcome, tasks)
    Agent->>Task: set status = AWAIT_PICKUP / DELIVERED
    Agent-->>Contract: task update

    Engine->>KPI: record_contract_event(outcome)
    Engine->>KPI: record_simulation_tick(...)
    Engine->>Engine: stop_if_all_agents_stranded()

    Engine-->>App: snapshot()
    App-->>User: redraw map, logs, panels, contract window
```

## Why the earlier version was wrong

The bug in the earlier diagram was that it showed bids being sent directly to the contract manager without the actual stateful auction logic in the BidCalculator.

In the real implementation:

1. `ContractNetManager.submit_task()` announces the task.
2. Each agent evaluates the task and may create a delivery entry.
3. `SimulationEngine.submit_pending_bids()` calls `ContractNetManager.record_bid()`.
4. `ContractNetManager.record_bid()` delegates to `BidCalculator.record_bid()`.
5. `BidCalculator` stores bids in `self.bids[task_id]` and exposes `has_bid()` and `award_ready_tasks()`.
6. Only later, when the deadline is reached, `award_ready_tasks()` selects the winner and emits `AWARD` / `BID_LOST` / `NO_BID` messages.

So the correct flow is: task announcement -> bid storage in the BidCalculator -> deadline-based award decision -> agent notifications.
