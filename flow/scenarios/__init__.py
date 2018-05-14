# base scenario class
from flow.scenarios.base_scenario import Scenario

# custom generators
from flow.scenarios.bay_bridge.gen import BayBridgeGenerator
from flow.scenarios.bottleneck.gen import BottleneckGenerator
from flow.scenarios.bridge_toll.gen import BBTollGenerator
from flow.scenarios.figure8.gen import Figure8Generator
from flow.scenarios.grid.gen import SimpleGridGenerator
from flow.scenarios.highway.gen import HighwayGenerator
from flow.scenarios.loop.gen import CircleGenerator
from flow.scenarios.merge.gen import MergeGenerator
from flow.scenarios.netfile.gen import NetFileGenerator

# custom scenarios
from flow.scenarios.bay_bridge.scenario import BayBridgeScenario
from flow.scenarios.bottleneck.scenario import BottleneckScenario
from flow.scenarios.bridge_toll.scenario import BBTollScenario
from flow.scenarios.figure8.figure8_scenario import Figure8Scenario
from flow.scenarios.grid.grid_scenario import SimpleGridScenario
from flow.scenarios.highway.scenario import HighwayScenario
from flow.scenarios.loop.loop_scenario import LoopScenario
from flow.scenarios.merge.scenario import MergeScenario
from flow.scenarios.netfile.scenario import NetFileScenario

# base scenario class
__all__ = ["Scenario"]

# custom generators
__all__ += ["BayBridgeGenerator", "BottleneckGenerator", "BBTollGenerator",
            "Figure8Generator", "SimpleGridGenerator", "HighwayGenerator",
            "CircleGenerator", "MergeGenerator", "NetFileGenerator"]

# custom scenarios
__all__ += ["BayBridgeScenario", "BottleneckScenario", "BBTollScenario",
            "Figure8Scenario", "SimpleGridScenario", "HighwayScenario",
            "LoopScenario", "MergeScenario", "NetFileScenario"]
