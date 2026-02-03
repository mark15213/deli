# Subscription type registry
from typing import Dict, Type, Tuple, Optional, TYPE_CHECKING
from .base import BaseSubscriptionConfig, BaseFetcher
from .configs import RSSSubscriptionConfig, HFDailyPapersConfig, AuthorBlogConfig

# Lazy import fetchers to avoid circular dependencies
if TYPE_CHECKING:
    from .fetchers import RSSFetcher, HFDailyFetcher, AuthorBlogFetcher


class SubscriptionRegistry:
    """
    Registry for subscription types.
    Maps source types to their config classes and fetchers.
    """
    
    # Will be populated lazily
    _registry: Dict[str, Tuple[Type[BaseSubscriptionConfig], str]] = {
        "RSS_FEED": (RSSSubscriptionConfig, "RSSFetcher"),
        "HF_DAILY_PAPERS": (HFDailyPapersConfig, "HFDailyFetcher"),
        "AUTHOR_BLOG": (AuthorBlogConfig, "AuthorBlogFetcher"),
    }
    
    # Source types that are subscriptions
    _subscription_types = {"RSS_FEED", "HF_DAILY_PAPERS", "AUTHOR_BLOG"}
    
    # Cached fetcher classes
    _fetcher_classes: Dict[str, Type[BaseFetcher]] = {}
    
    @classmethod
    def _load_fetcher_class(cls, fetcher_name: str) -> Type[BaseFetcher]:
        """Lazy load fetcher class to avoid import issues."""
        if fetcher_name not in cls._fetcher_classes:
            from . import fetchers
            cls._fetcher_classes[fetcher_name] = getattr(fetchers, fetcher_name)
        return cls._fetcher_classes[fetcher_name]
    
    @classmethod
    def get_config_class(cls, source_type: str) -> Type[BaseSubscriptionConfig]:
        """Get the config class for a subscription type."""
        if source_type not in cls._registry:
            raise ValueError(f"Unknown subscription type: {source_type}")
        return cls._registry[source_type][0]
    
    @classmethod
    def get_fetcher_class(cls, source_type: str) -> Type[BaseFetcher]:
        """Get the fetcher class for a subscription type."""
        if source_type not in cls._registry:
            raise ValueError(f"Unknown subscription type: {source_type}")
        fetcher_name = cls._registry[source_type][1]
        return cls._load_fetcher_class(fetcher_name)
    
    @classmethod
    def create_fetcher(cls, source_type: str) -> BaseFetcher:
        """Create a fetcher instance for a subscription type."""
        fetcher_class = cls.get_fetcher_class(source_type)
        return fetcher_class()
    
    @classmethod
    def parse_config(cls, source_type: str, config_dict: dict) -> BaseSubscriptionConfig:
        """Parse a config dict into the appropriate config class."""
        config_class = cls.get_config_class(source_type)
        return config_class(**config_dict)
    
    @classmethod
    def get_form_schema(cls, source_type: str) -> dict:
        """
        Get the JSON Schema for frontend form generation.
        Returns Pydantic model's JSON schema.
        """
        config_class = cls.get_config_class(source_type)
        return config_class.model_json_schema()
    
    @classmethod
    def get_default_config(cls, source_type: str) -> dict:
        """Get default config values for a subscription type."""
        config_class = cls.get_config_class(source_type)
        return config_class().model_dump()
    
    @classmethod
    def is_subscription_type(cls, source_type: str) -> bool:
        """Check if a source type is a subscription type."""
        return source_type in cls._subscription_types
    
    @classmethod
    def get_all_subscription_types(cls) -> list:
        """Get list of all subscription type names."""
        return list(cls._subscription_types)


# Singleton instance for convenience
subscription_registry = SubscriptionRegistry()
