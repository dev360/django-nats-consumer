from typing import Any, Dict

from django.conf import settings

CONFIG_DEFAULTS = {
    "event_loop_policy": None,
}


def get_config(settings_name=None):
    if settings_name is None:
        settings_name = "NATS_CONSUMER"

    def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    return merge_dicts(CONFIG_DEFAULTS, getattr(settings, settings_name, {}))


config = get_config()
connect_args = config.get("connect_args", {})
default_durable_name = config.get("DEFAULT_DURABLE_NAME", "default")
