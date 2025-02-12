"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
import uuid
from core.models import Component

@pytest.fixture
def valid_component_data():
    """Fixture providing valid component data."""
    from django.contrib.gis.geos import GEOSGeometry
    
    # Create a 3D polygon using WKT format
    wkt = (
        'POLYGON Z ((0 0 0, 0 25 0, 25 25 0, 25 0 0, 0 0 0))'
    )
    geometry = GEOSGeometry(wkt, srid=4326)
    
    return {
        'classification': 'ET_AUD_PROC_AMP_001',
        'name': 'amplify-signal',
        'version': '1.0.0',
        'functional_properties': {
            'acoustic_rating': 'A',
            'emi_shield_level': '2'
        },
        'base_geometry': geometry,
        'core_mission': 'Amplify audio signal with minimal distortion'
    }

@pytest.mark.django_db
class TestComponent:
    """Test suite for Component model."""

    def test_create_valid_component(self, valid_component_data):
        """Test creating a component with valid data."""
        component = Component.objects.create(**valid_component_data)
        assert isinstance(component.id, uuid.UUID)
        assert component.classification == valid_component_data['classification']
        assert component.is_active is True

    def test_invalid_classification_format(self, valid_component_data):
        """Test validation of classification format."""
        valid_component_data['classification'] = 'INVALID_FORMAT'
        with pytest.raises(ValidationError):
            Component.objects.create(**valid_component_data)

    def test_version_semantic_validation(self, valid_component_data):
        """Test semantic versioning validation."""
        valid_component_data['version'] = 'invalid.version'
        with pytest.raises(ValidationError):
            Component.objects.create(**valid_component_data)

    def test_functional_properties_validation(self, valid_component_data):
        """Test required functional properties validation."""
        valid_component_data['functional_properties'] = {}
        with pytest.raises(ValidationError):
            Component.objects.create(**valid_component_data)

    def test_grid_alignment_validation(self, valid_component_data):
        """Test 25mm grid alignment validation."""
        from django.contrib.gis.geos import GEOSGeometry
        
        misaligned_wkt = (
            'POLYGON Z ((0 0 0, 0 12.3 0, 12.3 12.3 0, 12.3 0 0, 0 0 0))'
        )
        valid_component_data['base_geometry'] = GEOSGeometry(misaligned_wkt, srid=4326)
        
        with pytest.raises(ValidationError):
            Component.objects.create(**valid_component_data)
    def test_unique_classification_version(self, valid_component_data):
        """Test unique constraint on classification and version."""
        Component.objects.create(**valid_component_data)
        with pytest.raises(ValidationError):
            Component.objects.create(**valid_component_data)

    def test_component_str_representation(self, valid_component_data):
        """Test string representation of component."""
        component = Component.objects.create(**valid_component_data)
        expected = f"{valid_component_data['classification']} - {valid_component_data['name']} (v{valid_component_data['version']})"
        assert str(component) == expected

    def test_timestamps_auto_update(self, valid_component_data):
        """Test automatic timestamp updates."""
        component = Component.objects.create(**valid_component_data)
        assert component.created_at
        assert component.modified_at
        
        original_modified = component.modified_at
        component.name = "new-name"
        component.save()
        assert component.modified_at > original_modified

    @pytest.fixture
    def component_with_relations(valid_component_data):
        """Fixture providing a component with related objects."""
        component = Component.objects.create(**valid_component_data)
    
        # Create related objects
        Parameter.objects.create(
            component=component,
            name='input_voltage',
            value=12,
            unit='V'
        )
    
        MaterialRequirement.objects.create(
            component=component,
            material_code='PCB-001',
            quantity=1,
            unit='pcs'
        )
    
        Documentation.objects.create(
            component=component,
            title='Assembly Guide',
            content='Step 1...',
            document_type='manual'
        )
    
        return component

    @pytest.mark.parametrize('method_name', [
        'get_parameters',
        'get_material_requirements',
        'get_documentation'
    ])
    def test_relationship_methods(self, valid_component_data, method_name):
        """Test relationship accessor methods."""
        component = Component.objects.create(**valid_component_data)
        method = getattr(component, method_name)
        result = method()
        assert hasattr(result, 'all')

    def test_create_instance_method(self, valid_component_data):
        """Test component instance creation."""
        component = Component.objects.create(**valid_component_data)
        instance = component.create_instance()
        assert instance.component == component
        assert instance.spatial_data == component.base_geometry  # Changed from location
        assert instance.instance_properties == {'finish': 'matte'}  # Changed from properties