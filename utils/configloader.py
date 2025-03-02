import os
import json
from typing import Any, override
from pprint import pformat


class ConfigHandler:
    class error:
        class ConfigError(Exception):
            pass

    def __init__(self):
        self._config = {}

    @property
    def config(self) -> dict:
        return self._config

    def set_config(self, config_obj: str | dict | Any) -> None:
        config = self._verify_config_integrity(config_obj)
        self._config = config

    def get(self, *args) -> Any:
        result = self._config
        for arg in args:
            result = result[arg]
        return result

    def set(self, *args, value: Any) -> None:
        if not args:
            raise self.error.ConfigError("At least one key must be provided")

        last_key = args[-1]
        config = self._config

        for key in args[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[last_key] = value

    def _verify_config_integrity(self, config_obj: str | dict | Any) -> dict:
        if isinstance(config_obj, dict):
            return config_obj
        elif isinstance(config_obj, ConfigHandler):
            return config_obj.config
        if not os.path.exists(config_obj):
            raise self.error.ConfigError("Configuration file not found")
        with open(config_obj, 'r') as f:
            config = json.load(f)
        return config


class BotConfig(ConfigHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def set_config(self, config_obj: str | dict | Any) -> None:
        config = self._verify_config_integrity(config_obj)
        self._verify_config(config)
        self._config = config

    def _verify_config(self, config: dict):
        # Verify database configuration
        database = config.get('database')
        if not database:
            raise self.error.ConfigError("Missing 'database' configuration")
        if 'dev' not in database or not isinstance(database['dev'], bool):
            raise self.error.ConfigError("Missing or invalid 'database.dev'")
        if 'url' not in database or not isinstance(database['url'], str):
            raise self.error.ConfigError("Missing or invalid 'database.url'")
        if 'name' not in database or not isinstance(database['name'], str):
            raise self.error.ConfigError("Missing or invalid 'database.name'")


        # Verify bot configuration
        bot = config.get('bot')
        if not bot:
            raise self.error.ConfigError("Missing 'bot' configuration")
        if 'token' not in bot or not isinstance(bot['token'], str):
            raise self.error.ConfigError("Missing or invalid 'bot.token'")
        if 'prefix' not in bot or not isinstance(bot['prefix'], str):
            raise self.error.ConfigError("Missing or invalid 'bot.prefix'")
        if 'starboard' not in bot or not isinstance(bot['starboard'], int):
            raise self.error.ConfigError("Missing or invalid 'bot.starboard'")

        # Verify guild configuration
        guild = config.get('guild')
        if not guild:
            raise self.error.ConfigError("Missing 'guild' configuration")
        if 'id' not in guild or not isinstance(guild['id'], int):
            raise self.error.ConfigError("Missing or invalid 'guild.id'")


        roles = guild.get('roles')
        if not roles:
            raise self.error.ConfigError("Missing or invalid 'guild.roles.admin'")
        elif 'admin' not in roles or not isinstance(roles['admin'], int):
            raise self.error.ConfigError("Missing or invalid 'guild.roles.admin'")

        channels = guild.get('channels')
        if not channels:
            raise self.error.ConfigError("Missing 'guild.channels' configuration")

        required_channels = ['welcome', 'logs', 'drops', 'starboard']
        for channel in required_channels:
            if channel not in channels or not isinstance(channels[channel], int):
                raise self.error.ConfigError(f"Missing or invalid 'guild.channels.{channel}'")

        # Verify XP rewards configuration
        xp = config.get('xp')
        if not xp:
            raise self.error.ConfigError("Missing 'xp' configuration")

        rewards = xp.get('rewards')
        if not rewards or not isinstance(rewards, dict) or not rewards:
            raise self.error.ConfigError("Missing or invalid 'xp.rewards'")

        for level, role in rewards.items():
            if not isinstance(level, str) or not level.isdigit():
                raise self.error.ConfigError(f"Invalid reward level '{level}', must be a digit string")
            if not isinstance(role, int):
                raise self.error.ConfigError(f"Invalid reward role for level '{level}', must be an int")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return pformat(self._config)
