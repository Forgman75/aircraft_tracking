import pytest
from src.base_classes import APIAdapter, BaseStorage


def test_api_adapter_cannot_be_instantiated():
    with pytest.raises(TypeError):
        APIAdapter()


def test_base_storage_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseStorage()

