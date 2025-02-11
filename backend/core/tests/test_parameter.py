"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

Test suite for the Parameter model.
"""

import pytest
from django.core.exceptions import ValidationError
import uuid
from core.models import Parameter, Component
from .test_component import valid_component_data

@pytest.fixture
def valid_component(valid_component_data):
    """Fixture providing a valid component."""
    return Component.objects.create(**valid_component_data)

@pytest.fixture
def valid_parameter_data(valid_component):
    """Fixture providing valid parameter data."""
    return {
        'component': valid_component,
        'name': 'wall_thickness',
        'data_type': 'float',
        'units': 'mm',
        'valid_ranges': {
            'min': 0,
            'max': 100,
            'step': 0.1
        },
        'is_required': True,
        'description': 'Wall thickness in millimeters'
    }

@pytest.mark.django_db
class TestParameter:
    """Test suite for Parameter model."""

    def test_create_valid_parameter(self, valid_parameter_data):
        """Test creating a parameter with valid data."""
        parameter = Parameter.objects.create(**valid_parameter_data)
        assert isinstance(parameter.id, uuid.UUID)
        assert parameter.name == valid_parameter_data['name']
        assert parameter.units == valid_parameter_data['units']

    def test_units_validation(self, valid_parameter_data):
        """Test validation of units for numeric parameters."""
        valid_parameter_data['units'] = None
        with pytest.raises(ValidationError):
            Parameter.objects.create(**valid_parameter_data)

    def test_valid_ranges_validation(self, valid_parameter_data):
        """Test validation of valid_ranges field."""
        # Test invalid type
        valid_parameter_data['valid_ranges'] = []
        with pytest.raises(ValidationError):
            Parameter.objects.create(**valid_parameter_data)

        # Test missing required keys
        valid_parameter_data['valid_ranges'] = {'min': 0}  # missing 'max'
        with pytest.raises(ValidationError):
            Parameter.objects.create(**valid_parameter_data)

    def test_validate_value_numeric(self, valid_parameter_data):
        """Test value validation for numeric parameters."""
        parameter = Parameter.objects.create(**valid_parameter_data)

        # Test valid value
        assert parameter.validate_value(50.0) is True

        # Test value below minimum
        with pytest.raises(ValidationError):
            parameter.validate_value(-1)

        # Test value above maximum
        with pytest.raises(ValidationError):
            parameter.validate_value(101)

        # Test step validation
        with pytest.raises(ValidationError):
            parameter.validate_value(50.05)  # not a valid step

    def test_validate_value_required(self, valid_parameter_data):
        """Test validation of required parameters."""
        parameter = Parameter.objects.create(**valid_parameter_data)
        
        with pytest.raises(ValidationError):
            parameter.validate_value(None)

    def test_validate_value_types(self, valid_parameter_data):
        """Test validation of different data types."""
        # Test boolean parameter
        valid_parameter_data.update({
            'data_type': 'boolean',
            'valid_ranges': {},
            'units': None
        })
        bool_param = Parameter.objects.create(**valid_parameter_data)
        
        assert bool_param.validate_value(True) is True
        with pytest.raises(ValidationError):
            bool_param.validate_value("true")

        # Test JSON parameter
        valid_parameter_data.update({
            'data_type': 'json',
            'name': 'config'
        })
        json_param = Parameter.objects.create(**valid_parameter_data)
        
        assert json_param.validate_value({'key': 'value'}) is True
        with pytest.raises(ValidationError):
            json_param.validate_value([1, 2, 3])

    def test_unique_constraint(self, valid_parameter_data):
        """Test unique constraint on component and name."""
        Parameter.objects.create(**valid_parameter_data)
        with pytest.raises(ValidationError):
            Parameter.objects.create(**valid_parameter_data)

    def test_parameter_str_representation(self, valid_parameter_data):
        """Test string representation of parameter."""
        parameter = Parameter.objects.create(**valid_parameter_data)
        expected = f"{parameter.component.name} - {parameter.name} ({parameter.data_type})"
        assert str(parameter) == expected

    def test_timestamps_auto_update(self, valid_parameter_data):
        """Test automatic timestamp updates."""
        parameter = Parameter.objects.create(**valid_parameter_data)
        assert parameter.created_at
        assert parameter.modified_at
        
        original_modified = parameter.modified_at
        parameter.description = "Updated description"
        parameter.save()
        assert parameter.modified_at > original_modified

    def test_get_values(self, valid_parameter_data):
        """Test retrieving parameter values."""
        parameter = Parameter.objects.create(**valid_parameter_data)
        values = parameter.get_values()
        assert hasattr(values, 'all')  # Verify it returns a QuerySet