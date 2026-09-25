from app.domain.entities.agent import Agent, AgentType
from app.domain.entities.contractnetmessage import MessageType, describe
from app.domain.entities.depot import Depot
from app.domain.entities.destination import Destination
from app.domain.entities.deliverytask import DeliveryTask
from app.domain.entities.graph import GraphMap, GraphNode, NodeKind
from app.domain.services.contractnetmanager import ContractNetManager
from app.shared.constants import AWAIT_PICKUP, DELIVERED, IN_TRANSIT, OPEN
from app.simulation.engine import SimulationEngine
from app.config import load_config
from pathlib import Path


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
        MessageType.ANNOUNCE,
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

    for _ in range(3):
        engine.move_agent(agent, {agent.position}, set())

    transit_events = [
        event
        for event in engine.contract_net_manager.events
        if event.type is MessageType.TASK_IN_TRANSIT
    ]
    assert task.status == IN_TRANSIT
    assert len(transit_events) == 1
    assert transit_events[0].task_id == task.id
    assert transit_events[0].destination == destination.position