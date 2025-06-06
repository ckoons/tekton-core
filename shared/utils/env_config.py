"""
Environment configuration loader for Tekton components.

Provides typed, validated configuration objects for each component
using Pydantic models and the underlying env_manager.
"""
import os
from typing import Optional, Dict, Any
import logging
from pydantic import BaseModel, Field, field_validator

from shared.utils.env_manager import get_env_manager, TektonEnvManager

logger = logging.getLogger(__name__)


class BaseComponentConfig(BaseModel):
    """Base configuration for all Tekton components."""
    
    port: int
    
    @classmethod
    def from_env(cls) -> 'BaseComponentConfig':
        """Create config instance from environment variables."""
        # This will be overridden by subclasses
        return cls()
    
    @classmethod
    def _get_env_value(cls, key: str, default: Any = None, value_type: str = 'str') -> Any:
        """
        Get typed value from environment with fallback to default.
        
        Args:
            key: Environment variable name
            default: Default value if not found or invalid
            value_type: Type to convert to ('str', 'int', 'float', 'bool')
            
        Returns:
            Typed value or default
        """
        value = os.environ.get(key)
        if value is None:
            return default
        
        try:
            if value_type == 'int':
                return int(value)
            elif value_type == 'float':
                return float(value)
            elif value_type == 'bool':
                return value.lower() in ('true', 'yes', '1', 'y', 't', 'on')
            else:
                return value
        except (ValueError, AttributeError):
            logger.debug(f"Invalid {value_type} value for {key}: {value}, using default: {default}")
            return default


class HermesConfig(BaseComponentConfig):
    """Configuration for Hermes service registry."""
    
    port: int = 8001
    discovery_enabled: bool = True
    registration_timeout: int = 30
    health_check_interval: int = 60
    
    @classmethod
    def from_env(cls) -> 'HermesConfig':
        """Create HermesConfig from environment variables."""
        return cls(
            port=cls._get_env_value('HERMES_PORT', 8001, 'int'),
            discovery_enabled=cls._get_env_value('TEKTON_HERMES_DISCOVERY', True, 'bool'),
            registration_timeout=cls._get_env_value('HERMES_REGISTRATION_TIMEOUT', 30, 'int'),
            health_check_interval=cls._get_env_value('HERMES_HEALTH_CHECK_INTERVAL', 60, 'int')
        )


class EngramConfig(BaseComponentConfig):
    """Configuration for Engram memory system."""
    
    port: int = 8000
    memory_limit: int = 1000
    cache_enabled: bool = True
    vector_dimensions: int = 768
    
    @classmethod
    def from_env(cls) -> 'EngramConfig':
        """Create EngramConfig from environment variables."""
        return cls(
            port=cls._get_env_value('ENGRAM_PORT', 8000, 'int'),
            memory_limit=cls._get_env_value('ENGRAM_MEMORY_LIMIT', 1000, 'int'),
            cache_enabled=cls._get_env_value('ENGRAM_CACHE_ENABLED', True, 'bool'),
            vector_dimensions=cls._get_env_value('ENGRAM_VECTOR_DIMENSIONS', 768, 'int')
        )


class RhetorConfig(BaseComponentConfig):
    """Configuration for Rhetor LLM service."""
    
    port: int = 8003
    default_model: str = 'claude-3-sonnet'
    default_provider: str = 'anthropic'
    request_timeout: int = 120
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'RhetorConfig':
        """Create RhetorConfig from environment variables."""
        return cls(
            port=cls._get_env_value('RHETOR_PORT', 8003, 'int'),
            default_model=cls._get_env_value('TEKTON_DEFAULT_MODEL', 'claude-3-sonnet', 'str'),
            default_provider=cls._get_env_value('TEKTON_DEFAULT_PROVIDER', 'anthropic', 'str'),
            request_timeout=cls._get_env_value('RHETOR_TIMEOUT', 120, 'int'),
            max_retries=cls._get_env_value('RHETOR_MAX_RETRIES', 3, 'int')
        )


class AthenaConfig(BaseComponentConfig):
    """Configuration for Athena knowledge graph."""
    
    port: int = 8005
    graph_enabled: bool = True
    max_nodes: int = 10000
    
    @classmethod
    def from_env(cls) -> 'AthenaConfig':
        """Create AthenaConfig from environment variables."""
        return cls(
            port=cls._get_env_value('ATHENA_PORT', 8005, 'int'),
            graph_enabled=cls._get_env_value('ATHENA_GRAPH_ENABLED', True, 'bool'),
            max_nodes=cls._get_env_value('ATHENA_MAX_NODES', 10000, 'int')
        )


class ApolloConfig(BaseComponentConfig):
    """Configuration for Apollo prediction system."""
    
    port: int = 8012
    predictions_enabled: bool = True
    confidence_threshold: float = 0.75
    update_interval: int = 300
    
    @classmethod
    def from_env(cls) -> 'ApolloConfig':
        """Create ApolloConfig from environment variables."""
        return cls(
            port=cls._get_env_value('APOLLO_PORT', 8012, 'int'),
            predictions_enabled=cls._get_env_value('TEKTON_APOLLO_PREDICTIONS', True, 'bool'),
            confidence_threshold=cls._get_env_value('APOLLO_CONFIDENCE_THRESHOLD', 0.75, 'float'),
            update_interval=cls._get_env_value('APOLLO_UPDATE_INTERVAL', 300, 'int')
        )


class BudgetConfig(BaseComponentConfig):
    """Configuration for Budget cost management."""
    
    port: int = 8013
    tracking_enabled: bool = True
    warning_threshold: float = 100.0
    limit: float = 500.0
    
    @classmethod
    def from_env(cls) -> 'BudgetConfig':
        """Create BudgetConfig from environment variables."""
        return cls(
            port=cls._get_env_value('BUDGET_PORT', 8013, 'int'),
            tracking_enabled=cls._get_env_value('TEKTON_BUDGET_TRACKING', True, 'bool'),
            warning_threshold=cls._get_env_value('BUDGET_WARNING_THRESHOLD', 100.0, 'float'),
            limit=cls._get_env_value('BUDGET_LIMIT', 500.0, 'float')
        )


class ErgonConfig(BaseComponentConfig):
    """Configuration for Ergon agent system."""
    
    port: int = 8002
    agent_enabled: bool = True
    max_agents: int = 10
    
    @classmethod
    def from_env(cls) -> 'ErgonConfig':
        return cls(
            port=cls._get_env_value('ERGON_PORT', 8002, 'int'),
            agent_enabled=cls._get_env_value('ERGON_AGENT_ENABLED', True, 'bool'),
            max_agents=cls._get_env_value('ERGON_MAX_AGENTS', 10, 'int')
        )


class HarmoniaConfig(BaseComponentConfig):
    """Configuration for Harmonia workflow system."""
    
    port: int = 8007
    workflow_enabled: bool = True
    max_workflows: int = 100
    
    @classmethod
    def from_env(cls) -> 'HarmoniaConfig':
        return cls(
            port=cls._get_env_value('HARMONIA_PORT', 8007, 'int'),
            workflow_enabled=cls._get_env_value('HARMONIA_WORKFLOW_ENABLED', True, 'bool'),
            max_workflows=cls._get_env_value('HARMONIA_MAX_WORKFLOWS', 100, 'int')
        )


class MetisConfig(BaseComponentConfig):
    """Configuration for Metis task management."""
    
    port: int = 8011
    task_enabled: bool = True
    max_tasks: int = 1000
    
    @classmethod
    def from_env(cls) -> 'MetisConfig':
        return cls(
            port=cls._get_env_value('METIS_PORT', 8011, 'int'),
            task_enabled=cls._get_env_value('METIS_TASK_ENABLED', True, 'bool'),
            max_tasks=cls._get_env_value('METIS_MAX_TASKS', 1000, 'int')
        )


class PrometheusConfig(BaseComponentConfig):
    """Configuration for Prometheus planning system."""
    
    port: int = 8006
    planning_enabled: bool = True
    max_plans: int = 100
    
    @classmethod
    def from_env(cls) -> 'PrometheusConfig':
        return cls(
            port=cls._get_env_value('PROMETHEUS_PORT', 8006, 'int'),
            planning_enabled=cls._get_env_value('PROMETHEUS_PLANNING_ENABLED', True, 'bool'),
            max_plans=cls._get_env_value('PROMETHEUS_MAX_PLANS', 100, 'int')
        )


class SophiaConfig(BaseComponentConfig):
    """Configuration for Sophia ML system."""
    
    port: int = 8014
    ml_enabled: bool = True
    max_models: int = 10
    
    @classmethod
    def from_env(cls) -> 'SophiaConfig':
        return cls(
            port=cls._get_env_value('SOPHIA_PORT', 8014, 'int'),
            ml_enabled=cls._get_env_value('SOPHIA_ML_ENABLED', True, 'bool'),
            max_models=cls._get_env_value('SOPHIA_MAX_MODELS', 10, 'int')
        )


class SynthesisConfig(BaseComponentConfig):
    """Configuration for Synthesis execution engine."""
    
    port: int = 8009
    execution_enabled: bool = True
    max_executions: int = 50
    
    @classmethod
    def from_env(cls) -> 'SynthesisConfig':
        return cls(
            port=cls._get_env_value('SYNTHESIS_PORT', 8009, 'int'),
            execution_enabled=cls._get_env_value('SYNTHESIS_EXECUTION_ENABLED', True, 'bool'),
            max_executions=cls._get_env_value('SYNTHESIS_MAX_EXECUTIONS', 50, 'int')
        )


class TelosConfig(BaseComponentConfig):
    """Configuration for Telos requirements system."""
    
    port: int = 8008
    requirements_enabled: bool = True
    max_requirements: int = 500
    
    @classmethod
    def from_env(cls) -> 'TelosConfig':
        return cls(
            port=cls._get_env_value('TELOS_PORT', 8008, 'int'),
            requirements_enabled=cls._get_env_value('TELOS_REQUIREMENTS_ENABLED', True, 'bool'),
            max_requirements=cls._get_env_value('TELOS_MAX_REQUIREMENTS', 500, 'int')
        )


class TektonConfig(BaseModel):
    """Global Tekton system configuration."""
    
    # Debug settings
    debug: bool = False
    log_level: str = 'INFO'
    
    # System settings
    auto_launch: bool = True
    component_timeout: int = 30
    
    # UI settings
    show_greek_names: bool = True
    theme_mode: str = 'dark'
    theme_color: str = 'blue'
    
    # Feature flags
    mcp_enabled: bool = True
    notifications_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> 'TektonConfig':
        """Create TektonConfig from environment variables."""
        return cls(
            debug=cls._get_env_value('TEKTON_DEBUG', False, 'bool'),
            log_level=cls._get_env_value('TEKTON_LOG_LEVEL', 'INFO', 'str'),
            auto_launch=cls._get_env_value('TEKTON_AUTO_LAUNCH', True, 'bool'),
            component_timeout=cls._get_env_value('TEKTON_COMPONENT_TIMEOUT', 30, 'int'),
            show_greek_names=cls._get_env_value('SHOW_GREEK_NAMES', True, 'bool'),
            theme_mode=cls._get_env_value('TEKTON_THEME_MODE', 'dark', 'str'),
            theme_color=cls._get_env_value('TEKTON_THEME_COLOR', 'blue', 'str'),
            mcp_enabled=cls._get_env_value('TEKTON_MCP_ENABLED', True, 'bool'),
            notifications_enabled=cls._get_env_value('TEKTON_NOTIFICATIONS_ENABLED', True, 'bool')
        )
    
    @classmethod
    def _get_env_value(cls, key: str, default: Any = None, value_type: str = 'str') -> Any:
        """Get typed value from environment (needed since TektonConfig doesn't inherit from BaseComponentConfig)."""
        return BaseComponentConfig._get_env_value(key, default, value_type)


class ComponentConfig:
    """
    Central configuration object for all Tekton components.
    
    Provides typed access to all component configurations and
    global Tekton settings.
    """
    
    def __init__(self):
        """Initialize component configuration."""
        self.env_manager = get_env_manager()
        self.env_manager.load_environment()
        
        # Load all component configs
        self._load_configs()
    
    def _load_configs(self):
        """Load all component configurations from environment."""
        self.hermes = HermesConfig.from_env()
        self.engram = EngramConfig.from_env()
        self.rhetor = RhetorConfig.from_env()
        self.athena = AthenaConfig.from_env()
        self.apollo = ApolloConfig.from_env()
        self.budget = BudgetConfig.from_env()
        self.ergon = ErgonConfig.from_env()
        self.harmonia = HarmoniaConfig.from_env()
        self.metis = MetisConfig.from_env()
        self.prometheus = PrometheusConfig.from_env()
        self.sophia = SophiaConfig.from_env()
        self.synthesis = SynthesisConfig.from_env()
        self.telos = TelosConfig.from_env()
        self.tekton = TektonConfig.from_env()
    
    def refresh(self):
        """Refresh configuration from environment."""
        self.env_manager.load_environment()
        self._load_configs()
    
    def get_port(self, component: str) -> Optional[int]:
        """
        Get port for a specific component by name.
        
        Args:
            component: Component name (case insensitive)
            
        Returns:
            Port number or None if component not found
        """
        component_lower = component.lower()
        
        # Map component names to config attributes
        component_map = {
            'hermes': self.hermes,
            'engram': self.engram,
            'rhetor': self.rhetor,
            'athena': self.athena,
            'apollo': self.apollo,
            'budget': self.budget,
        }
        
        config = component_map.get(component_lower)
        if config and hasattr(config, 'port'):
            return config.port
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all configurations to dictionary."""
        return {
            'hermes': self.hermes.model_dump(),
            'engram': self.engram.model_dump(),
            'rhetor': self.rhetor.model_dump(),
            'athena': self.athena.model_dump(),
            'apollo': self.apollo.model_dump(),
            'budget': self.budget.model_dump(),
            'tekton': self.tekton.model_dump(),
        }


# Global instance for convenient access
_global_component_config: Optional[ComponentConfig] = None


def get_component_config() -> ComponentConfig:
    """
    Get the global ComponentConfig instance (singleton).
    
    Returns:
        Global ComponentConfig instance
    """
    global _global_component_config
    if _global_component_config is None:
        _global_component_config = ComponentConfig()
    return _global_component_config


def get_tekton_config() -> TektonConfig:
    """
    Get global Tekton configuration.
    
    Returns:
        TektonConfig instance
    """
    return get_component_config().tekton