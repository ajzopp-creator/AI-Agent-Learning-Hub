"""Custom exceptions for hub_lib.

All hub_lib exceptions inherit from HubLibError so callers can catch the
whole family with a single except clause if they want.
"""


class HubLibError(Exception):
    """Base exception for all hub_lib errors."""


class ConfigError(HubLibError):
    """Configuration is missing or invalid (e.g. missing API key, bad task name)."""


class ModelUnavailableError(HubLibError):
    """A model failed its health check or is unreachable.

    Raised by health_check.verify_health(). The caller decides whether to
    abort the run or fall back to another task.
    """


class ProviderError(HubLibError):
    """A provider returned an error during generate().

    Wraps the underlying SDK exception so callers don't need to import
    each provider's exception types.
    """
