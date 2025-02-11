"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

Test suite for the Connection model implementation.
"""

import uuid
import random
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.gis.geos import GEOSGeometry, Polygon
from datetime import timedelta
from core.models import (
    Connection, 
    ComponentInstance, 
    ConnectionStatus,
    ConnectionType, 
    Component
)
from .test_instance import valid_instance_data
from .test_component import valid_component_data

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up the database before and after each test."""
    Connection.objects.all().delete()
    ComponentInstance.objects.all().delete()
    yield
    Connection.objects.all().delete()
    ComponentInstance.objects.all().delete()

@pytest.fixture
def valid_component(valid_component_data):
    """Fixture providing a valid component."""
    return Component.objects.create(**valid_component_data)

@pytest.fixture
def valid_component_instances(valid_instance_data):
    """Fixture providing two valid component instances for connection testing."""
    # Create deep copies of the data for each instance
    instance1_data = valid_instance_data.copy()
    instance2_data = valid_instance_data.copy()
    
    # Set deterministic unique internal IDs for each instance
    instance1_data['internal_id'] = 1
    instance2_data['internal_id'] = 2
    instance1_data['id'] = uuid.uuid4()
    instance2_data['id'] = uuid.uuid4()
    
    # Create instances with unique data
    instance1 = ComponentInstance.objects.create(**instance1_data)
    instance2 = ComponentInstance.objects.create(**instance2_data)
    
    return instance1, instance2

@pytest.fixture
def valid_connection_data(valid_component_instances):
    """Fixture providing valid connection data."""
    instance1, instance2 = valid_component_instances
    
    # Create a simple 3D polygon for testing
    test_id = random.randint(0,100)*25  # Add randomness to ensure unique geometries

    wkt = f'POLYGON Z (({test_id} 0 0, {test_id} 25 0, {test_id+25} 25 0, {test_id+25} 0 0, {test_id} 0 0))'
    geometry = GEOSGeometry(wkt, srid=4326)
    
    # Create the spatial bbox as a 2D polygon from the geometry's extent
    bbox = geometry.extent  # Returns (xmin, ymin, xmax, ymax)
    bbox_wkt = f'POLYGON (({bbox[0]} {bbox[1]}, {bbox[0]} {bbox[3]}, {bbox[2]} {bbox[3]}, {bbox[2]} {bbox[1]}, {bbox[0]} {bbox[1]}))'
    spatial_bbox = GEOSGeometry(bbox_wkt, srid=4326)
    
    return {
        'instance_1': instance1,
        'instance_2': instance2,
        'connection_type': ConnectionType.BOLTED,
        'spatial_relationship': geometry,
        'spatial_bbox': spatial_bbox,
        'status': ConnectionStatus.PLANNED,
        'connection_properties': {
            'fastener_type': 'M8',
            'torque_spec': '25Nm',
            'strength': 'high',
            'material': 'steel'
        }
    }
@pytest.mark.django_db
class TestConnection:
    """Test suite for Connection model."""
    def _create_fresh_instances(self, valid_instance_data):
        """Helper method to create fresh component instances."""
        # Create deep copies of the data for each instance
        instance1_data = valid_instance_data.copy()
        instance2_data = valid_instance_data.copy()
        
        # Set unique IDs for each instance
        instance1_data['internal_id'] = random.randint(0,9999999)
        instance2_data['internal_id'] = random.randint(0,9999999)
        instance1_data['id'] = uuid.uuid4()
        instance2_data['id'] = uuid.uuid4()
        
        # Create instances with unique data
        instance1 = ComponentInstance.objects.create(**instance1_data)
        instance2 = ComponentInstance.objects.create(**instance2_data)
        
        return instance1, instance2

    def _get_fresh_connection_data(self, valid_connection_data, valid_instance_data):
        """Helper method to get fresh connection data with new instances."""
        new_instances = self._create_fresh_instances(valid_instance_data)
        fresh_data = valid_connection_data.copy()
        fresh_data['instance_1'] = new_instances[0]
        fresh_data['instance_2'] = new_instances[1]
        return fresh_data

    def test_create_valid_connection(self, valid_connection_data, valid_instance_data):
        """Test creating a connection with valid data."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        connection = Connection.objects.create(**fresh_data)
        assert isinstance(connection.id, uuid.UUID)
        assert connection.spatial_bbox is not None
        assert connection.connection_type == ConnectionType.BOLTED.value

    def test_invalid_spatial_relationship(self, valid_connection_data, valid_instance_data):
        """Test validation of spatial relationship data."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        fresh_data['spatial_relationship'] = None
        with pytest.raises(ValidationError):
            Connection.objects.create(**fresh_data)

    def test_grid_alignment_validation(self, valid_connection_data, valid_instance_data):
        """Test 25mm grid alignment validation."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        # Create misaligned geometry
        wkt = 'POLYGON Z ((0 0 0, 0 12.3 0, 12.3 12.3 0, 12.3 0 0, 0 0 0))'
        fresh_data['spatial_relationship'] = GEOSGeometry(wkt, srid=4326)
        
        with pytest.raises(ValidationError):
            Connection.objects.create(**fresh_data)

    def test_connection_type_validation(self, valid_connection_data, valid_instance_data):
        """Test validation of connection type and required properties."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        fresh_data['connection_properties'] = {'emi_shielding': True}
        with pytest.raises(ValidationError):
            Connection.objects.create(**fresh_data)

    def test_emi_shielding_validation(self, valid_connection_data, valid_instance_data):
        """Test EMI shielding property validation."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        fresh_data['connection_properties']['emi_shielding'] = 'invalid'
        with pytest.raises(ValidationError):
            Connection.objects.create(**fresh_data)

    def test_status_update(self, valid_connection_data, valid_instance_data):
        """Test status update functionality."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        connection = Connection.objects.create(**fresh_data)
        original_timestamp = connection.status_changed_at
        
        connection.update_status(ConnectionStatus.IN_PROGRESS.value)
        assert connection.status == ConnectionStatus.IN_PROGRESS.value
        assert connection.status_changed_at > original_timestamp

    def test_temporal_validation(self, valid_connection_data, valid_instance_data):
        """Test temporal consistency validation."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        connection = Connection.objects.create(**fresh_data)
        connection.created_at = timezone.now()
        connection.modified_at = connection.created_at - timedelta(days=1)
        
        with pytest.raises(ValidationError):
            connection.full_clean()

    def test_bounding_box_calculation(self, valid_connection_data, valid_instance_data):
        """Test automatic bounding box calculation."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        connection = Connection.objects.create(**fresh_data)
        assert connection.spatial_bbox is not None
        assert connection.spatial_bbox.contains(connection.spatial_relationship)

    def test_invalid_status_update(self, valid_connection_data, valid_instance_data):
        """Test invalid status update handling."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        connection = Connection.objects.create(**fresh_data)
        with pytest.raises(ValueError):
            connection.update_status('invalid_status')

    def test_prevent_duplicate_connections(self, valid_connection_data, valid_instance_data):
        """Test prevention of duplicate connections between same instances."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        Connection.objects.create(**fresh_data)
        
        # Swap instances to test duplicate prevention
        fresh_data['instance_1'], fresh_data['instance_2'] = \
            fresh_data['instance_2'], fresh_data['instance_1']
            
        with pytest.raises(ValidationError):
            Connection.objects.create(**fresh_data)

    def test_hierarchical_connections(self, valid_connection_data, valid_instance_data):
        """Test parent-child connection relationships."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        parent = Connection.objects.create(**fresh_data)
        
        # Create new instances for child connection
        child_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        child_data['parent_connection'] = parent
        
        child = Connection.objects.create(**child_data)
        assert child.parent_connection == parent

    def test_str_representation(self, valid_connection_data, valid_instance_data):
        """Test string representation of connection."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        connection = Connection.objects.create(**fresh_data)
        expected = f"Connection {connection.id} ({connection.connection_type}) between {connection.instance_1.id} and {connection.instance_2.id}"
        assert str(connection) == expected

    def test_property_validation(self, valid_connection_data, valid_instance_data):
        """Test connection properties validation."""
        fresh_data = self._get_fresh_connection_data(valid_connection_data, valid_instance_data)
        fresh_data['connection_properties'] = 'invalid'
        with pytest.raises(ValidationError):
            Connection.objects.create(**fresh_data)