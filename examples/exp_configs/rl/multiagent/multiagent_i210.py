"""Multi-agent highway with ramps example.

Trains a non-constant number of agents, all sharing the same policy, on the
highway with ramps network.
"""
import os
import numpy as np

from ray.rllib.agents.ppo.ppo_policy import PPOTFPolicy
import flow.config as config
from flow.envs.ring.accel import ADDITIONAL_ENV_PARAMS
from flow.controllers.rlcontroller import RLController
from flow.controllers.car_following_models import IDMController
from flow.core.params import EnvParams
from flow.core.params import NetParams
from flow.core.params import InitialConfig
from flow.core.params import InFlows
from flow.core.params import VehicleParams
from flow.core.params import SumoParams
from flow.core.params import SumoLaneChangeParams
from flow.core.rewards import energy_consumption
from flow.networks.i210_subnetwork import I210SubNetwork, EDGES_DISTRIBUTION
from flow.envs.multiagent import I210MultiEnv
from flow.utils.registry import make_create_env
from ray.tune.registry import register_env

# SET UP PARAMETERS FOR THE SIMULATION

# number of rollouts per training iteration
N_ROLLOUTS = 2
# number of steps per rollout
HORIZON = 500
# number of parallel workers
N_CPUS = 1

VEH_PER_HOUR_BASE_119257914 = 8378
VEH_PER_HOUR_BASE_27414345 = 321
VEH_PER_HOUR_BASE_27414342 = 421

# percentage of autonomous vehicles compared to human vehicles on highway
PENETRATION_RATE = 10

# SET UP PARAMETERS FOR THE ENVIRONMENT
additional_env_params = ADDITIONAL_ENV_PARAMS.copy()
additional_env_params.update({
    'max_accel': 1,
    'max_decel': 1,
})

# CREATE VEHICLE TYPES AND INFLOWS
# no vehicles in the network
vehicles = VehicleParams()
vehicles.add(
    "human",
    num_vehicles=0,
    lane_change_params=SumoLaneChangeParams(lane_change_mode="strategic")
)
vehicles.add(
    "av",
    acceleration_controller=(RLController, {}),
    num_vehicles=0,
)

inflow = InFlows()
# main highway
pen_rate = PENETRATION_RATE / 100
assert pen_rate < 1.0, "your penetration rate is over 100%"
assert pen_rate > 0.0, "your penetration rate should be above zero"
inflow.add(
    veh_type="human",
    edge="119257914",
    vehs_per_hour=VEH_PER_HOUR_BASE_119257914 * (1 - pen_rate),
    # probability=1.0,
    departLane="random",
    departSpeed=20)
# on ramp
inflow.add(
    veh_type="human",
    edge="27414345",
    vehs_per_hour=VEH_PER_HOUR_BASE_27414345 * (1 - pen_rate),
    departLane="random",
    departSpeed=20)
inflow.add(
    veh_type="human",
    edge="27414342#0",
    vehs_per_hour=VEH_PER_HOUR_BASE_27414342 * (1 - pen_rate),
    departLane="random",
    departSpeed=20)

# Now add the AVs
# main highway
inflow.add(
    veh_type="av",
    edge="119257914",
    vehs_per_hour=int(VEH_PER_HOUR_BASE_119257914 * pen_rate),
    # probability=1.0,
    departLane="random",
    departSpeed=20)
# # on ramp
# NOTE: this seems to error out with some array mismatch
# (also not clear whether we want to control RL vehicles on an onramp)
# inflow.add(
#     veh_type="av",
#     edge="27414345",
#     vehs_per_hour=int(VEH_PER_HOUR_BASE_27414345 * pen_rate),
#     departLane="random",
#     departSpeed=20)
# inflow.add(
#     veh_type="av",
#     edge="27414342#0",
#     vehs_per_hour=int(VEH_PER_HOUR_BASE_27414342 * pen_rate),
#     departLane="random",
#     departSpeed=20)

NET_TEMPLATE = os.path.join(
    config.PROJECT_PATH,
    "examples/exp_configs/templates/sumo/test2.net.xml")

flow_params = dict(
    # name of the experiment
    exp_tag='I_210_subnetwork',

    # name of the flow environment the experiment is running on
    env_name=I210MultiEnv,

    # name of the network class the experiment is running on
    network=I210SubNetwork,

    # simulator that is used by the experiment
    simulator='traci',

    # simulation-related parameters
    sim=SumoParams(
        sim_step=0.1,
        render=False,
        color_by_speed=True,
        restart_instance=True
    ),

    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        horizon=HORIZON,  # TODO(@evinitsky) decrease it when testing
        additional_params=additional_env_params,
    ),

    # network-related parameters (see flow.core.params.NetParams and the
    # network's documentation or ADDITIONAL_NET_PARAMS component)
    net=NetParams(
        inflows=inflow,
        template=NET_TEMPLATE
    ),

    # vehicles to be placed in the network at the start of a rollout (see
    # flow.core.params.VehicleParams)
    veh=vehicles,

    # parameters specifying the positioning of vehicles upon initialization/
    # reset (see flow.core.params.InitialConfig)
    initial=InitialConfig(
        edges_distribution=EDGES_DISTRIBUTION,
    ),
)

# SET UP RLLIB MULTI-AGENT FEATURES

create_env, env_name = make_create_env(params=flow_params, version=0)

# register as rllib env
register_env(env_name, create_env)

# multiagent configuration
test_env = create_env()
obs_space = test_env.observation_space
act_space = test_env.action_space

POLICY_GRAPHS = {'av': (PPOTFPolicy, obs_space, act_space, {})}

POLICIES_TO_TRAIN = ['av']


def policy_mapping_fn(_):
    """Map a policy in RLlib."""
    return 'av'

custom_callables = {
    "avg_speed": lambda env: np.mean([speed for speed in env.k.vehicle.get_speed(env.k.vehicle.get_ids()) if speed >= 0]),
    "avg_outflow": lambda env: np.nan_to_num(
        env.k.vehicle.get_outflow_rate(120)),
    # we multiply by 5 to account for the vehicle length and by 1000 to convert
    # into veh/km
    # "avg_density": lambda env: 5 * 1000 * len(env.k.vehicle.get_ids_by_edge(
    #     edge_id)) / (env.k.network.edge_length(edge_id)
    #                  * env.k.network.num_lanes(edge_id)),
    "avg_energy": lambda env: energy_consumption(env, 0.1)
}
