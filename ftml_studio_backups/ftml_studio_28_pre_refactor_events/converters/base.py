# src/ftml_studio/converters/base.py
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """Abstract base class for all format converters"""

    @abstractmethod
    def convert(self, content):
        """
        Convert content between formats

        Args:
            content (str): Content to convert

        Returns:
            str: Converted content
        """
        pass

    def can_convert(self, source_format, target_format):
        """
        Check if this converter can handle the specified formats

        Args:
            source_format (str): Source format identifier
            target_format (str): Target format identifier

        Returns:
            bool: True if conversion is supported, False otherwise
        """
        return False
