"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

Test suite for the ParameterValue model.
"""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import uuid
from core.models import ParameterValue, Parameter, ComponentInstance, Component
from .test_component import valid_component_data

@pytest.fixture
def valid_component(valid_component_data):
    """Fixture providing a valid component."""
    return Component.objects.create(**valid_component_data)

@pytest.fixture
def valid_parameter(valid_component):
    """Fixture providing a valid parameter."""
    return Parameter.objects.create(
        component=valid_component,
        name='wall_thickness',
        data_type='float',
        units='mm',
        valid_ranges={
            'min': 0,
            'max': 100,
            'step': 0.1
        },
        is_required=True,
        description='Wall thickness in millimeters'
    )

@pytest.fixture
def valid_instance(valid_component):
    """Fixture providing a valid component instance."""
    from django.contrib.gis.geos import GEOSGeometry
    
    # Create a simple 3D polygon for testing
    wkt = 'POLYGON Z ((0 0 0, 0 25 0, 25 25 0, 25 0 0, 0 0 0))'
    geometry = GEOSGeometry(wkt, srid=4326)
    
    return ComponentInstance.objects.create(
        component=valid_component,
        spatial_data=geometry,
        spatial_bbox=geometry.envelope,
        instance_properties={
            'test_property': 'test_value'  # Non-empty properties
        },
        internal_id=1,
        created_at=timezone.now()
    )

@pytest.fixture
def valid_parameter_value_data(valid_instance, valid_parameter, test_user):
    """Fixture providing valid parameter value data."""
    return {
        'instance': valid_instance,
        'parameter': valid_parameter,
        'value': {
            'value': 50.0,
            'unit': 'mm'
        },
        'validation_status': 'pending',
        'recorded_at': timezone.now(),
        'modified_by': test_user
    }

@pytest.fixture
def test_user():
    """Fixture providing a test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )    

@pytest.mark.django_db
class TestParameterValue:
    """Test suite for ParameterValue model."""

    def test_create_valid_parameter_value(self, valid_parameter_value_data):
        """Test creating a parameter value with valid data."""
        value = ParameterValue.objects.create(**valid_parameter_value_data)
        assert isinstance(value.id, uuid.UUID)
        assert value.get_value() == 50.0
        assert value.validation_status == 'valid'  # Should be validated on save

    def test_temporal_integrity(self, valid_parameter_value_data):
        """Test temporal integrity validation."""
        # Set recorded_at to before instance creation
        valid_parameter_value_data['recorded_at'] = (
            valid_parameter_value_data['instance'].created_at - timedelta(days=1)
        )
        with pytest.raises(ValidationError) as exc:
            ParameterValue.objects.create(**valid_parameter_value_data)
        assert 'recorded_at' in str(exc.value)

    def test_value_constraints(self, valid_parameter_value_data):
        """Test value constraint validation."""
        # Test value outside valid range
        valid_parameter_value_data['value']['value'] = 150.0  # Above max
        with pytest.raises(ValidationError):
            ParameterValue.objects.create(**valid_parameter_value_data)

        # Test invalid step
        valid_parameter_value_data['value']['value'] = 50.05  # Not a valid step
        with pytest.raises(ValidationError):
            ParameterValue.objects.create(**valid_parameter_value_data)

    def test_required_parameter(self, valid_parameter_value_data):
        """Test required parameter validation."""
        valid_parameter_value_data['value']['value'] = None
        with pytest.raises(ValidationError):
            ParameterValue.objects.create(**valid_parameter_value_data)

    def test_unit_validation(self, valid_parameter_value_data):
        """Test unit validation."""
        # Test invalid unit
        valid_parameter_value_data['value']['unit'] = 'cm'
        with pytest.raises(ValidationError):
            ParameterValue.objects.create(**valid_parameter_value_data)

        # Test missing unit
        valid_parameter_value_data['value'].pop('unit')
        with pytest.raises(ValidationError):
            ParameterValue.objects.create(**valid_parameter_value_data)

    def test_unique_constraint(self, valid_parameter_value_data):
        """Test unique constraint on instance and parameter."""
        ParameterValue.objects.create(**valid_parameter_value_data)
        with pytest.raises(ValidationError):
            ParameterValue.objects.create(**valid_parameter_value_data)

    def test_get_value(self, valid_parameter_value_data):
        """Test get_value method."""
        value = ParameterValue.objects.create(**valid_parameter_value_data)
        assert value.get_value() == 50.0

    def test_set_value(self, valid_parameter_value_data):
        """Test set_value method."""
        value = ParameterValue.objects.create(**valid_parameter_value_data)
        
        # Test valid value update
        value.set_value(75.0, 'mm')
        assert value.get_value() == 75.0
        assert value.validation_status == 'valid'

        # Test invalid value update
        with pytest.raises(ValidationError):
            value.set_value(150.0, 'mm')  # Above max

        # Test invalid unit update
        with pytest.raises(ValidationError):
            value.set_value(75.0, 'cm')

    def test_validation_status_updates(self, valid_parameter_value_data):
        """Test validation status updates."""
        value = ParameterValue.objects.create(**valid_parameter_value_data)
        assert value.validation_status == 'valid'

        # Simulate invalid update
        try:
            value.set_value(150.0, 'mm')  # Above max
        except ValidationError:
            pass
        assert value.validation_status == 'invalid'

    def test_str_representation(self, valid_parameter_value_data):
        """Test string representation."""
        value = ParameterValue.objects.create(**valid_parameter_value_data)
        expected = f"wall_thickness = 50.0 (valid)"
        assert str(value) == expected

    def test_audit_timestamps(self, valid_parameter_value_data):
        """Test automatic timestamp updates."""
        value = ParameterValue.objects.create(**valid_parameter_value_data)
        assert value.created_at
        assert value.modified_at
        
        original_modified = value.modified_at
        value.set_value(75.0, 'mm')
        assert value.modified_at > original_modified