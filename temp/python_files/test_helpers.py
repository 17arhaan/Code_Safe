"""Test helper functions."""
import unittest
from typing import Any, Callable

def assert_raises(exception_class, func: Callable, *args, **kwargs):
    """Assert that function raises specific exception."""
    try:
        func(*args, **kwargs)
        assert False, f"Expected {exception_class.__name__} to be raised"
    except exception_class:
        pass

def mock_function(return_value: Any = None):
    """Create a mock function that returns specified value."""
    def mock(*args, **kwargs):
        return return_value
    return mock

class TestCase(unittest.TestCase):
    """Base test case with common utilities."""
    
    def assert_dict_contains(self, container: dict, subset: dict):
        """Assert that container dict contains subset dict."""
        for key, value in subset.items():
            self.assertIn(key, container)
            self.assertEqual(container[key], value)
