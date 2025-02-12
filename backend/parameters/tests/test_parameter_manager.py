"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import pytest
from django.core.exceptions import ValidationError
from ..core.interfaces.parameter_manager import ParameterManager, Parameter, ParameterConstraint

@pytest.fixture
def manager():
    return ParameterManager()

@pytest.fixture
def sample_parameter():
    return Parameter(
        id="test_param",
        name="Test Parameter",
        type="length",
        value=100.0,
        constraints=ParameterConstraint(
            min_value=0.0,
            max_value=200.0,
            step=1.0,
            unit="mm"
        )
    )

class TestParameterManager:
    def test_add_parameter(self, manager, sample_parameter):
        manager.add_parameter(sample_parameter)
        assert sample_parameter.id in manager._parameters
        
    def test_add_parameter_with_invalid_value(self, manager):
        invalid_parameter = Parameter(
            id="invalid_param",
            name="Invalid Parameter",
            type="length",
            value=-10.0,
            constraints=ParameterConstraint(min_value=0.0)
        )
        with pytest.raises(ValidationError) as exc_info:
            manager.add_parameter(invalid_parameter)
        assert "below minimum" in str(exc_info.value)

    def test_update_parameter(self, manager, sample_parameter):
        manager.add_parameter(sample_parameter)
        affected = manager.update_parameter("test_param", 150.0)
        assert isinstance(affected, list)
        assert sample_parameter.value == 150.0


    def test_update_nonexistent_parameter(self, manager):
        with pytest.raises(KeyError) as exc_info:
            manager.update_parameter("nonexistent", 100.0)
        assert "not found" in str(exc_info.value)

    def test_update_parameter_invalid_value(self, manager, sample_parameter):
        manager.add_parameter(sample_parameter)
        with pytest.raises(ValidationError) as exc_info:
            manager.update_parameter("test_param", 250.0)
        assert "above maximum" in str(exc_info.value)

    def test_parameter_dependencies(self, manager):
        # Create two dependent parameters
        param1 = Parameter(
            id="width",
            name="Width",
            type="length",
            value=100.0,
            constraints=ParameterConstraint(min_value=0.0)
        )
        param2 = Parameter(
            id="area",
            name="Area",
            type="area",
            value=10000.0,
            constraints=ParameterConstraint(min_value=0.0)
        )
        
        manager.add_parameter(param1)
        manager.add_parameter(param2)
        
        # Add dependency in the graph
        manager._graph.add_dependency("width", "area", "multiplication")
        
        # Test that updating width affects area
        affected = manager.update_parameter("width", 150.0)
        assert "area" in affected

    @pytest.mark.asyncio
    async def test_concurrent_updates(self, manager, sample_parameter):
        manager.add_parameter(sample_parameter)
        
        # Test multiple concurrent updates
        import asyncio
        update_values = [50.0, 75.0, 100.0, 125.0]
        
        async def update_param(value):
            return manager.update_parameter("test_param", value)
        
        tasks = [update_param(value) for value in update_values]
        results = await asyncio.gather(*tasks)
        
        # Verify all updates completed
        assert all(isinstance(result, list) for result in results)
        assert sample_parameter.value in update_values

    def test_parameter_validation_with_step(self, manager):
        param = Parameter(
            id="stepped_param",
            name="Stepped Parameter",
            type="length",
            value=10.5,
            constraints=ParameterConstraint(
                min_value=0.0,
                max_value=20.0,
                step=1.0
            )
        )
        
        with pytest.raises(ValidationError) as exc_info:
            manager.add_parameter(param)
        assert "must be a multiple of step" in str(exc_info.value)
