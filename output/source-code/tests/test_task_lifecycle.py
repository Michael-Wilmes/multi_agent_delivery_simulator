from app.domain.entities.agent import Agent, AgentType
from app.domain.entities.contractnetmessage import MessageType, describe
from app.domain.entities.depot import Depot
from app.domain.entities.destination import Destination
from app.domain.entities.deliverytask import DeliveryTask
from app.domain.entities.graph import GraphMap, GraphNode, NodeKind
from app.domain.services.contractnetmanager import ContractNetManager
from app.shared.constants import AWAIT_PICKUP, BUSY, DELIVERED, IDLE, IN_TRANSIT, LOADING, OPEN
from app.simulation.engine import SimulationEngine
from app.config import load_config
from pathlib import Path


def test_agent_status_changes_are_sent_to_contract_net():
    agent = Agent(
        id=1,
        type=AgentType.STANDARD,
        position=(0, 0),
        speed=1,
        capacity=1,
        task_capacity=1,
    )
    manager = ContractNetManager()
    manager.register_agent(agent)

    agent.set_status(BUSY, tick=4)
    agent.set_status(LOADING, tick=5)
    agent.set_status(IDLE, tick=6)
    agent.mark_stranded(tick=7)

    status_events = [
        event for event in manager.events
        if event.type in {
            MessageType.AGENT_LOADING,
            MessageType.AGENT_BUSY,
            MessageType.AGENT_IDLE,
            MessageType.AGENT_OUT_OF_ORDER,
        }
    ]
    assert [(event.tick, event.type) for event in status_events] == [
        (4, MessageType.AGENT_BUSY),
        (5, MessageType.AGENT_LOADING),
        (6, MessageType.AGENT_IDLE),
        (7, MessageType.AGENT_OUT_OF_ORDER),
    ]
    assert all(event.agent_id == agent.id and event.task_id is None for event in status_events)
    assert describe(status_events[-1]) == "Agent 1 is out of order"


def test_every_agent_emits_a_status_message_each_tick():
    config_path = Path(__file__).parents[1] / "config" / "app.json"
    engine = SimulationEngine(load_config(config_path))

    engine.step()

    tick_events = [
        event for event in engine.contract_net_manager.events
        if event.tick == engine.tick
        and event.type in {
            MessageType.AGENT_IDLE,
            MessageType.AGENT_BUSY,
            MessageType.AGENT_LOADING,
            MessageType.AGENT_OUT_OF_ORDER,
        }
    ]
    assert {event.agent_id for event in tick_events} == {
        agent.id for agent in engine.agents
    }


def test_announced_task_receives_agent_bid_and_award():
    config_path = Path(__file__).parents[1] / "config" / "app.json"
    engine = SimulationEngine(load_config(config_path))
    agent = engine.agents[0]
    depot = Depot(id=0, position=agent.position)
    destination = Destination(id=0, position=(agent.position[0] + 1, agent.position[1]))
    task = DeliveryTask(id=43, depot=depot, destination=destination, created_tick=0)
    engine.tasks.append(task)

    engine.contract_net_manager.submit_task(task, tick=0, deadline=1)
    engine.submit_pending_bids(agent)

    assert engine.contract_net_manager.has_bid(task.id, agent.id)
    outcomes = engine.contract_net_manager.award_ready_tasks(engine.tasks, tick=1)

    assert outcomes[0].type is MessageType.AUCTION_AWARD
    assert outcomes[0].agent_id == agent.id
    assert task.status == AWAIT_PICKUP
    assert task.assigned_agent_id == agent.id


def test_snapshot_counts_each_agents_assigned_tasks_awaiting_pickup():
    config_path = Path(__file__).parents[1] / "config" / "app.json"
    engine = SimulationEngine(load_config(config_path))
    agent = engine.agents[0]
    other_agent = next(candidate for candidate in engine.agents if candidate.id != agent.id)
    depot = engine.graph.depots[0]
    destination = engine.graph.destinations[0]
    engine.tasks = [
        DeliveryTask(
            id=1,
            depot=depot,
            destination=destination,
            created_tick=0,
            status=AWAIT_PICKUP,
            assigned_agent_id=agent.id,
        ),
        DeliveryTask(
            id=2,
            depot=depot,
            destination=destination,
            created_tick=0,
            status=AWAIT_PICKUP,
            assigned_agent_id=other_agent.id,
        ),
        DeliveryTask(
            id=3,
            depot=depot,
            destination=destination,
            created_tick=0,
            status=IN_TRANSIT,
            assigned_agent_id=agent.id,
        ),
    ]

    snapshot = engine.snapshot()

    assert snapshot.awaiting_pickup_counts[agent.id] == 1
    assert snapshot.awaiting_pickup_counts[other_agent.id] == 1
    assert all(
        count == 0
        for agent_id, count in snapshot.awaiting_pickup_counts.items()
        if agent_id not in {agent.id, other_agent.id}
    )


def test_contract_manager_emits_task_status_events_with_destination():
    depot = Depot(id=0, position=(0, 0))
    destination = Destination(id=3, position=(4, 2))
    agent = Agent(
        id=1,
        type=AgentType.STANDARD,
        position=depot.position,
        speed=1,
        capacity=2,
        task_capacity=2,
    )
    manager = ContractNetManager()
    manager.register_agent(agent)
    depot.connect_contract_net_manager(manager)
    task = DeliveryTask(id=41, depot=depot, destination=destination, created_tick=0)

    depot.submit_task(task, tick=1, deadline=2)
    assert task.status == OPEN
    assert [event.type for event in manager.events[:2]] == [
        MessageType.AUCTION_ANNOUNCE,
        MessageType.TASK_OPEN,
    ]

    manager.record_bid(agent.id, task.id, 6.0, tick=2)
    manager.award_ready_tasks([task], tick=2)
    assert task.status == AWAIT_PICKUP
    assert manager.assign_task_to_agent(agent, task, tick=3)

    assert agent.pick_task(task)
    assert manager.start_task_for_agent(agent, task, tick=4)
    assert task.status == IN_TRANSIT
    agent.position = destination.position
    assert agent.deliver_task(task)
    assert manager.deliver_task_for_agent(agent, task, tick=5)
    assert task.status == DELIVERED

    status_events = [
        event
        for event in manager.events
        if event.type in {
            MessageType.TASK_OPEN,
            MessageType.TASK_ASSIGNED,
            MessageType.TASK_AWAIT_PICKUP,
            MessageType.TASK_IN_TRANSIT,
            MessageType.TASK_DELIVERED,
        }
    ]
    assert [event.type for event in status_events] == [
        MessageType.TASK_OPEN,
        MessageType.TASK_ASSIGNED,
        MessageType.TASK_AWAIT_PICKUP,
        MessageType.TASK_IN_TRANSIT,
        MessageType.TASK_DELIVERED,
    ]
    assert all(event.task_id == task.id for event in status_events)
    assert all(
        event.destination_id == destination.id
        and event.destination == destination.position
        for event in status_events
    )
    assert "awaiting bids" in describe(status_events[0])
    assert "AWAIT_PICKUP" in describe(status_events[2])
    assert "in delivery" in describe(status_events[3])
    assert "delivered at Destination Z4 (4, 2)" in describe(status_events[4])


def test_assigned_agent_routes_to_depot_and_emits_in_transit():
    config_path = Path(__file__).parents[1] / "config" / "app.json"
    engine = SimulationEngine(load_config(config_path))
    agent = engine.agents[0]
    engine.agents = [agent]
    engine.contract_net_manager.agents = [agent]

    depot = Depot(id=0, position=(0, 0))
    destination = Destination(id=0, position=(4, 0))
    graph = GraphMap(width=5, height=1, name="Lifecycle test")
    graph.add_node(GraphNode((0, 0), NodeKind.DEPOT))
    graph.add_node(GraphNode((1, 0), NodeKind.ROAD))
    graph.add_node(GraphNode((2, 0), NodeKind.ROAD))
    graph.add_node(GraphNode((3, 0), NodeKind.ROAD))
    graph.add_node(GraphNode((4, 0), NodeKind.TARGET))
    graph.rebuild_edges()
    graph.depots = [depot]
    graph.destinations = [destination]
    depot.connect_contract_net_manager(engine.contract_net_manager)
    engine.graph = graph

    agent.position = (3, 0)
    task = DeliveryTask(
        id=42,
        depot=depot,
        destination=destination,
        created_tick=0,
        status=AWAIT_PICKUP,
        assigned_agent_id=agent.id,
    )
    engine.tasks = [task]
    depot.add_task(task)

    assert engine.snapshot().awaiting_pickup_counts[agent.id] == 1
    for _ in range(2):
        engine.move_agent(agent, {agent.position}, set())
        assert task.status == AWAIT_PICKUP
        assert engine.snapshot().awaiting_pickup_counts[agent.id] == 1

    engine.move_agent(agent, {agent.position}, set())

    assert task.status == IN_TRANSIT
    assert engine.snapshot().awaiting_pickup_counts[agent.id] == 0
    transit_events = [
        event
        for event in engine.contract_net_manager.events
        if event.type is MessageType.TASK_IN_TRANSIT
    ]
    assert task.status == IN_TRANSIT
    assert len(transit_events) == 1
    assert transit_events[0].task_id == task.id
    assert transit_events[0].destination == destination.position
    pickup_move_events = [
        event for event in engine.contract_net_manager.events
        if event.type is MessageType.AGENT_MOVING_PICK_UP
    ]
    assert pickup_move_events
    assert all(event.position is not None for event in pickup_move_events)
    assert any(
        event.type is MessageType.AGENT_PICK_OFF and event.task_id == task.id
        for event in engine.contract_net_manager.events
    )
    assert all("moved to (" in describe(event) for event in pickup_move_events)

    engine.step()
    for _ in range(4):
        engine.move_agent(agent, {agent.position}, set())
    engine.deliver_task(agent)

    dropoff_move_events = [
        event for event in engine.contract_net_manager.events
        if event.type is MessageType.AGENT_MOVING_DROPOFF
    ]
    assert agent.position == destination.position
    assert task.status == DELIVERED
    assert engine.snapshot().awaiting_pickup_counts[agent.id] == 0
    assert dropoff_move_events
    assert all(event.position is not None for event in dropoff_move_events)
    assert any(
        event.type is MessageType.AGENT_DROP_OFF and event.task_id == task.id
        for event in engine.contract_net_manager.events
    )
    assert all("moved to (" in describe(event) for event in dropoff_move_events)