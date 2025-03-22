from typing import Any, Union
from pprint import pformat
from .confighandler import ConfigHandler
from .schemavalidator import SchemaValidator


class BotConfig(ConfigHandler):
    """
    Specialized Configuration Handler for Bot Applications
    
    Extends ConfigHandler with specific validation for bot configurations
    including database, bot settings, guild information, and XP rewards.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a bot configuration handler"""
        super().__init__(*args, **kwargs)
        self._setup_schema()

    def _setup_schema(self):
        """Set up the schema for automatic validation"""
        # Define the expected structure and types
        self._schema = {
            'database': {
                'dev': SchemaValidator.is_bool,
                'url': SchemaValidator.is_str,
                'name': SchemaValidator.is_str
            },
            'bot': {
                'token': SchemaValidator.is_str,
                'prefix': SchemaValidator.is_str,
                'starboard': SchemaValidator.is_int
            },
            'guild': {
                'id': SchemaValidator.is_int,
                'roles': {
                    'admin': SchemaValidator.is_int,
                    'dev': SchemaValidator.is_int,
                    'reactions': {
                        'message': SchemaValidator.is_int,
                        # Dynamic key-value pairs with specific types
                        # 'dynamic_emoji_roles': (SchemaValidator.is_str, SchemaValidator.is_int)
                    }
                },
                'channels': {
                    'welcome': SchemaValidator.is_int,
                    'logs': SchemaValidator.is_int,
                    'drops': SchemaValidator.is_int,
                    'starboard': SchemaValidator.is_int,
                    'bump': {
                        'id': SchemaValidator.is_int,
                        'bot': SchemaValidator.is_int
                    }
                }
            },
            'xp': {
                'rewards': (SchemaValidator.is_numeric_str, SchemaValidator.is_int)
            }
        }

    def set_config(self, config_obj: Union[str, dict, Any]) -> None:
        """
        Set and validate bot configuration
        
        Args:
            config_obj: Configuration source (file path, dictionary, or ConfigHandler)
            
        Raises:
            ConfigError: If the configuration fails validation
        """
        config = self._verify_config_integrity(config_obj)
        self._verify_config(config)
        self._config = config

    def _verify_config(self, config: dict) -> None:
        """
        Validate bot-specific configuration using the schema
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigError: If any required configuration is missing or invalid
        """
        # Validate top-level sections
        for section in ['database', 'bot', 'guild', 'xp']:
            if section not in config:
                raise self.error.ConfigError(f"Missing '{section}' configuration section")
        
        # Perform schema validation
        self._validate_against_schema(config)
        
        # Handle special case validations not covered by the schema
        self._validate_special_cases(config)

    def _validate_against_schema(self, config: dict) -> None:
        """
        Validate configuration against the defined schema
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigError: If validation fails
        """
        # Skip schema validation if no schema is defined
        if not self._schema:
            return
            
        # Perform validation
        errors = SchemaValidator.validate_dict_with_types(config, self._schema)
        
        # Handle special case for roles.reactions (dynamic emoji keys)
        if 'guild' in config and 'roles' in config['guild'] and 'reactions' in config['guild']['roles']:
            reactions = config['guild']['roles']['reactions']
            for key, value in reactions.items():
                if key != 'message':  # Skip the message ID key
                    if not isinstance(value, int):
                        errors.append(f"Expected int for reaction role value at 'guild.roles.reactions.{key}', got {type(value).__name__}")
        
        # Handle special case for xp.rewards (level to role mapping)
        if 'xp' in config and 'rewards' in config['xp']:
            rewards = config['xp']['rewards']
            for level, role in rewards.items():
                if not isinstance(level, str) or not level.isdigit():
                    errors.append(f"Invalid reward level '{level}', must be a digit string")
                if not isinstance(role, int):
                    errors.append(f"Invalid reward role for level '{level}', must be an int")
        
        # Raise exception if any validation errors were found
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            raise self.error.ConfigError(error_message)

    def _validate_special_cases(self, config: dict) -> None:
        """
        Perform special case validations not covered by the schema
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigError: If special case validation fails
        """
        # Example of a special case validation
        if 'guild' in config and 'roles' in config['guild'] and 'reactions' in config['guild']['roles']:
            reactions = config['guild']['roles']['reactions']
            if 'message' not in reactions:
                raise self.error.ConfigError("Missing required key 'message' in 'guild.roles.reactions'")

    def __repr__(self) -> str:
        """String representation for debugging purposes"""
        return self.__str__()

    def __str__(self) -> str:
        """String representation of the configuration"""
        return pformat(self._config)
