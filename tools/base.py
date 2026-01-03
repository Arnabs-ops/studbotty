from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given arguments."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """Return the input schema for the tool."""
        pass
