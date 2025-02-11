"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import uuid
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from datetime import timedelta
from core.models import ComponentInstance, Component, ComponentStatus
from .test_component import valid_component_data

@pytest.fixture
def valid_component(valid_component_data):
    """Fixture providing a valid component."""
    return Component.objects.create(**valid_component_data)

@pytest.fixture
def valid_instance_data(valid_component):
    """Fixture providing valid component instance data."""
    from django.contrib.gis.geos import GEOSGeometry
    
    wkt = 'POLYGON Z ((0 0 0, 0 25 0, 25 25 0, 25 0 0, 0 0 0))'
    geometry = GEOSGeometry(wkt, srid=4326)
    bbox = geometry.envelope
    
    return {
        'component': valid_component,
        'spatial_data': geometry,
        'spatial_bbox': bbox,
        'internal_id': 1,
        'instance_properties': {
            'material': 'steel',
            'finish': 'matte'
        },
        'status': ComponentStatus.PLANNED.value,
        'version': 1
    }
    
@pytest.mark.django_db
class TestComponentInstance:
    """Test suite for ComponentInstance model."""

    def test_create_valid_instance(self, valid_instance_data):
        """Test creating an instance with valid data."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        assert isinstance(instance.id, uuid.UUID)
        assert instance.internal_id > 0
        assert instance.spatial_bbox is not None

    def test_invalid_spatial_data(self, valid_instance_data):
        """Test validation of spatial data."""
        valid_instance_data['spatial_data'] = None
        with pytest.raises(ValidationError):
            ComponentInstance.objects.create(**valid_instance_data)

    def test_grid_alignment_validation(self, valid_instance_data):
        """Test 25mm grid alignment validation."""
        from django.contrib.gis.geos import GEOSGeometry
        
        misaligned_wkt = 'POLYGON Z ((0 0 0, 0 12.3 0, 12.3 12.3 0, 12.3 0 0, 0 0 0))'
        valid_instance_data['spatial_data'] = GEOSGeometry(misaligned_wkt, srid=4326)
        
        with pytest.raises(ValidationError):
            ComponentInstance.objects.create(**valid_instance_data)

    def test_status_update(self, valid_instance_data):
        """Test status update functionality."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        original_timestamp = instance.status_changed_at
        
        instance.update_status(ComponentStatus.IN_PROGRESS.value)  # Use value instead of name
        assert instance.status == ComponentStatus.IN_PROGRESS.value
        assert instance.status_changed_at > original_timestamp

    def test_version_creation(self, valid_instance_data):
        """Test creating new version of instance."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        new_version = instance.create_new_version()
        
        assert new_version.version == instance.version + 1
        assert new_version.component == instance.component
        assert new_version.spatial_data.equals(instance.spatial_data)

    def test_temporal_validation(self, valid_instance_data):
        """Test temporal consistency validation."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        instance.created_at = timezone.now()
        instance.modified_at = instance.created_at - timedelta(days=1)
        
        with pytest.raises(ValidationError):
            instance.full_clean()

    def test_bounding_box_calculation(self, valid_instance_data):
        """Test automatic bounding box calculation."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        assert instance.spatial_bbox is not None
        assert instance.spatial_bbox.contains(instance.spatial_data)

    def test_invalid_status_update(self, valid_instance_data):
        """Test invalid status update handling."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        with pytest.raises(ValueError):
            instance.update_status('invalid_status')

    def test_str_representation(self, valid_instance_data):
        """Test string representation of instance."""
        instance = ComponentInstance.objects.create(**valid_instance_data)
        expected = f"{instance.component.name} Instance {instance.internal_id} (v{instance.version})"
        assert str(instance) == expected

    def test_property_validation(self, valid_instance_data):
        """Test instance properties validation."""
        valid_instance_data['instance_properties'] = 'invalid'
        with pytest.raises(ValidationError):
            ComponentInstance.objects.create(**valid_instance_data)