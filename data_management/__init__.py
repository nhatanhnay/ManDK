# Data management module exports
from .module_data_manager import module_manager
from .configuration_manager import config_manager
from .node_data_manager import SystemDataManager, NodeData, system_data_manager
from .node_mapping_manager import get_node_id_for_compartment, NODE_NAME_TO_ID
from .unified_threshold_manager import unified_threshold_manager

# Maintain backwards compatibility
import sys
from . import module_data_manager as module_data
from . import node_data_manager as node_data
from . import node_mapping_manager as node_mapping
from . import unified_threshold_manager as threshold_manager

# For legacy imports
sys.modules['data.module_data'] = module_data
sys.modules['data.node_data'] = node_data
sys.modules['data.node_mapping'] = node_mapping
sys.modules['data.threshold_manager'] = threshold_manager