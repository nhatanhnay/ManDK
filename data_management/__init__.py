# Data management module exports
from .system_configuration import NODE_MODULE_CONFIG, ModuleConfig
from .module_data_manager import module_manager
from .configuration_manager import config_manager
from .node_data_manager import SystemDataManager, NodeData, system_data_manager
from .node_mapping_manager import get_node_id_for_compartment, NODE_NAME_TO_ID

# Maintain backwards compatibility
import sys
from . import system_configuration as system_config
from . import module_data_manager as module_data
from . import node_data_manager as node_data
from . import node_mapping_manager as node_mapping

# For legacy imports
sys.modules['data.system_config'] = system_config
sys.modules['data.module_data'] = module_data
sys.modules['data.node_data'] = node_data
sys.modules['data.node_mapping'] = node_mapping