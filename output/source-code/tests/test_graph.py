from app.config import load_config
from app.domain.depot import Depot
from app.domain.destination import Destination
from app.domain.deliverytask import DeliveryTask
from app.domain.agentdelivery import AgentDelivery
from app.domain.graph import NodeKind
from app.maps.presets import create_map1, create_map2, graph_from_ascii
from app.maps.random_map import RandomGraphMapFactory
from app.shared.constants import AWAIT_PICKUP, CHARGE, DELIVER, DELIVERED, IN_TRANSIT, LOAD_DELIVERY, LOADING, MOVE, PICKUP, STRANDED, SUBMIT_BID
from app.simulation.engine import SimulationEngine


def check(g, w, h):
    assert (g.width, g.height) == (w, h)
    walk = g.walkable_positions()
    assert len(g.reachable_from(walk[0])) == len(walk)
    assert len(g.positions_of_kind(NodeKind.DEPOT)) >= 2
    assert len(g.positions_of_kind(NodeKind.TARGET)) >= 3


def test_ascii_space_is_road():
    g = graph_from_ascii(['. # ', 'D Z '], 'space-map')
    assert g.nodes[(0, 0)].kind is NodeKind.ROAD
    assert g.nodes[(2, 0)].kind is NodeKind.ROAD
    assert g.nodes[(0, 1)].kind is NodeKind.DEPOT
    assert g.nodes[(2, 1)].kind is NodeKind.TARGET


def test_map_special_fields_are_domain_entities():
    g = graph_from_ascii(['D.Z', '...'], 'entity-map')

    assert g.depots == [Depot(0, (0, 0))]
    assert g.destinations == [Destination(0, (2, 0))]


def test_map_depots_are_domain_entities():
    g = graph_from_ascii(['D.Z', '...'], 'entity-map')

    assert g.depots == [Depot(0, (0, 0))]
    assert g.depots[0].position == (0, 0)


def test_engine_starts_with_configured_agents():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    assert len(engine.agents) == config.simulation.initial_standard_agents + config.simulation.initial_express_agents
    assert all(engine.graph.neighbors(agent.position) for agent in engine.agents)
    standard = next(agent for agent in engine.agents if agent.type.value == 'Standard')
    express = next(agent for agent in engine.agents if agent.type.value == 'Express')
    assert (standard.speed, standard.capacity, standard.battery, standard.battery_cost_per_field) == (1, 3, 100.0, 2)
    assert (express.speed, express.capacity, express.battery, express.battery_cost_per_field) == (2, 1, 100.0, 3)
    assert config.battery.chargingDurationTicks == 2
    assert config.battery.reserve == 10


def test_engine_creates_package_every_five_ticks_and_records_depot_kpi():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    engine.agents.clear()

    for _ in range(5):
        engine.step()

    assert len(engine.tasks) == 1
    tick, depot_id, task_id = engine.package_creation_kpi[0]
    assert tick == 5
    assert task_id == engine.tasks[0].id
    assert depot_id in {depot.id for depot in engine.graph.depots}
    assert any(f'Depot D{depot_id + 1} erzeugt T-{task_id:03d}' in message for message in engine.messages)


def test_agents_stay_within_map_bounds_after_steps():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)

    for _ in range(100):
        engine.step()
        assert all(engine.graph.in_bounds(agent.position) for agent in engine.agents)


def test_random_actions_match_special_map_positions():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]

    depot = engine.graph.depots[0]
    target = engine.graph.destinations[0]

    agent.position = depot.position
    engine.tasks.append(DeliveryTask(2, depot, target, engine.tick))
    assert engine.choose_random_action(agent) == PICKUP

    engine.tasks.clear()
    assert engine.choose_random_action(agent) in {MOVE, SUBMIT_BID}

    engine.tasks.append(DeliveryTask(3, depot, target, engine.tick, IN_TRANSIT, agent.id))
    assert engine.choose_random_action(agent) != DELIVER

    agent.position = target.position
    engine.tasks.append(DeliveryTask(1, depot, target, engine.tick, IN_TRANSIT, agent.id))
    assert engine.choose_random_action(agent) == DELIVER

    engine.tasks.clear()
    assert engine.choose_random_action(agent) in {MOVE, SUBMIT_BID}

    road = next(
        position for position, node in engine.graph.nodes.items()
        if node.kind is NodeKind.ROAD and position != agent.position
    )
    agent.position = road
    assert engine.choose_random_action(agent) in {MOVE, SUBMIT_BID}


def test_agent_charges_at_depot_without_moving_but_can_pick_up():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]
    depot = engine.graph.depots[0]
    destination = engine.graph.destinations[0]
    agent.position = depot.position
    agent.battery = 20.0
    engine.tasks.append(DeliveryTask(2, depot, destination, engine.tick))
    position = agent.position

    engine.step()

    assert agent.position == position
    assert agent.battery == 20.0
    assert agent.status == LOADING
    assert agent.current_action == LOAD_DELIVERY
    assert engine.tasks[-1].status == IN_TRANSIT

    engine.step()

    assert agent.battery == 100.0
    assert agent.current_action == CHARGE

    engine.step()

    assert agent.status != LOADING


def test_depot_tracks_created_tasks_and_removes_picked_up_task():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    depot = engine.graph.depots[0]
    agent = engine.agents[0]
    agent.position = depot.position

    assert engine.add_task()
    task = depot.tasks[-1]

    engine.pick_up_task(agent)

    assert task not in depot.tasks
    assert task.status == IN_TRANSIT
    assert task.assigned_agent_id == agent.id


def test_agent_marks_task_delivered_and_removes_active_delivery():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]
    depot = engine.graph.depots[0]
    destination = engine.graph.destinations[0]
    task = DeliveryTask(2, depot, destination, engine.tick, IN_TRANSIT, agent.id)
    agent.position = destination.position
    agent.load = 1
    agent.deliveries.append(AgentDelivery(task, agent.id, []))
    engine.tasks.append(task)

    engine.deliver_task(agent)

    assert task.status == DELIVERED
    assert task not in [delivery.task for delivery in agent.deliveries]
    assert agent.load == 0


def test_award_updates_the_depot_task_record():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    depot = engine.graph.depots[0]
    destination = engine.graph.destinations[0]
    task = DeliveryTask(2, depot, destination, engine.tick)
    depot.add_task(task)

    engine.contract_net_manager.award_task(task.id, engine.agents[0].id, engine.tick, task)

    assert depot.tasks[0].assigned_agent_id == engine.agents[0].id
    assert depot.tasks[0].status == AWAIT_PICKUP


def test_no_bid_is_recorded_at_task_deadline():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    depot = engine.graph.depots[0]
    destination = engine.graph.destinations[0]
    task = DeliveryTask(2, depot, destination, engine.tick)
    depot.add_task(task)
    engine.contract_net_manager.announce_task(task, engine.tick, deadline=engine.tick)

    outcomes = engine.contract_net_manager.award_ready_tasks([task], engine.tick)

    assert len(outcomes) == 1
    assert outcomes[0].type.value == 'NO_BID'
    assert outcomes[0].task_id == task.id
    assert outcomes[0].agent_id is None


def test_agent_without_task_loads_immediately_and_waits_one_tick():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]
    agent.position = engine.graph.positions_of_kind(NodeKind.DEPOT)[0]
    agent.battery = 20.0
    engine.tasks.clear()

    engine.step()

    assert agent.status == LOADING
    assert agent.current_action == CHARGE
    assert agent.battery == 20.0

    engine.step()

    assert agent.battery == 100.0
    assert agent.current_action == CHARGE


def test_deliver_is_ignored_outside_target():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]
    agent.position = engine.graph.positions_of_kind(NodeKind.DEPOT)[0]
    agent.current_action = MOVE

    engine.execute_action(agent, DELIVER, {agent.position}, set())

    assert agent.current_action == MOVE


def test_agent_without_delivery_task_cannot_enter_target():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]
    target = engine.graph.positions_of_kind(NodeKind.TARGET)[0]
    previous_position = next(
        position
        for position in engine.graph.neighbors(target)
        if engine.graph.node_at(position).kind is NodeKind.ROAD
    )
    agent.position = previous_position
    engine.tasks.clear()

    engine.move_agent(agent, {agent.position}, set())

    assert agent.position != target


def test_empty_battery_strands_agent_after_movement():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    agent = engine.agents[0]
    position = next(
        position for position, node in engine.graph.nodes.items()
        if node.kind is NodeKind.ROAD and engine.graph.neighbors(position)
    )
    agent.position = position
    agent.battery = float(agent.battery_cost_per_field)

    engine.move_agent(agent, {agent.position}, set())

    assert agent.battery == 0.0
    assert agent.status == STRANDED
    assert agent.current_action == STRANDED


def test_simulation_stops_when_all_agents_are_stranded():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    for agent in engine.agents:
        engine.mark_stranded(agent)
    engine.running = True

    engine.step()

    assert engine.running is False
    assert 'Keine Bewegungen mehr möglich' in engine.messages


def test_one_stranded_agent_does_not_stop_simulation():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    engine.mark_stranded(engine.agents[0])
    engine.running = True

    engine.step()

    assert engine.running is True
    assert 'Keine Bewegungen mehr möglich' not in engine.messages


def test_maps():
    maps = [create_map1(), create_map2(), RandomGraphMapFactory(42).create()]
    for graph in maps:
        check(graph, 10 if graph.name != 'Zufallskarte' else 20, 10 if graph.name != 'Zufallskarte' else 20)
        special_positions = graph.positions_of_kind(NodeKind.DEPOT) + graph.positions_of_kind(NodeKind.TARGET)
        assert all(graph.neighbors(position) for position in special_positions)
