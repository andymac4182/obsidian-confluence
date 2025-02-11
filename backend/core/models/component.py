from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import uuid
import semver
from django.contrib.gis.db import models as gis_models

class Component(gis_models.Model):
    """
    The Component model represents the foundational entity in the EuroTempl system.
    It defines the core characteristics and properties of modular components that can
    be instantiated in actual designs.
    """

    # Core fields with unique constraints and validation
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the component"
    )

    classification = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^ET_[A-Z]{3}_[A-Z]{4}_[A-Z]{3}_\d{3}(_[rv]\d+)?$',
                message="Classification must follow EuroTempl format: ET_XXX_XXXX_XXX_000"
            )
        ],
        help_text="Hierarchical classification following EuroTempl naming convention"
    )

    name = models.CharField(
        max_length=100,
        help_text="Verb-noun pair describing component purpose"
    )

    version = models.CharField(
        max_length=20,
        help_text="Component version following semantic versioning"
    )

    # Complex property storage using JSONB
    functional_properties = JSONField(
        default=dict,
        help_text="Stores acoustic, EMI, and other functional characteristics"
    )

    # Spatial data field for geometric representation
    base_geometry = gis_models.GeometryField(
        dim=3,
        spatial_index=True,
        help_text="Base geometric definition using PostGIS"
    )

    core_mission = models.CharField(
        max_length=200,
        help_text="Single core mission as per EuroTempl principles"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if component is currently active"
    )

    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'et_component'
        indexes = [
            models.Index(fields=['classification']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['classification', 'version'],
                name='unique_component_version'
            )
        ]

    def clean(self):
        """
        Validate the component according to EuroTempl business rules.
        """
        # Validate version follows semantic versioning
        try:
            semver.VersionInfo.parse(self.version.lstrip('v'))
        except ValueError:
            raise ValidationError({
                'version': 'Version must follow semantic versioning (MAJOR.MINOR.PATCH)'
            })
    
        # Validate functional properties contain required characteristics
        required_properties = {'acoustic_rating', 'emi_shield_level'}
        if not all(prop in self.functional_properties for prop in required_properties):
            raise ValidationError({
                'functional_properties': 'Must include acoustic_rating and emi_shield_level'
            })
    
        # Validate base geometry is 3D
        if self.base_geometry:
            if not hasattr(self.base_geometry, 'coords') or not self.base_geometry.coords:
                raise ValidationError({
                    'base_geometry': 'Geometry must be three-dimensional'
                })
            self._validate_grid_alignment()
    
    def _validate_grid_alignment(self):
        """
        Validate that the geometry aligns with the 25mm base grid system.
        """
        if not self.base_geometry:
            return
            
        coords = self.base_geometry.coords
        for coord in coords[0]:  # Check first ring coordinates
            x, y, z = coord
            if any(c % 25 != 0 for c in (x, y)):  # Only check x,y alignment !
                raise ValidationError({
                    'base_geometry': 'Geometry must align with 25mm grid system'
                })

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is always performed.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.classification} - {self.name} (v{self.version})"

    # Model methods for component operations
    def create_instance(self):
        """Create a new ComponentInstance from this component definition."""
        from .instance import ComponentInstance, ComponentStatus  # Avoid circular import
        
        # Get next internal_id
        last_internal_id = ComponentInstance.objects.all().order_by('-internal_id').first()
        next_internal_id = (last_internal_id.internal_id + 1) if last_internal_id else 1
        
        # Create instance with all required fields
        instance = ComponentInstance.objects.create(
            component=self,
            spatial_data=self.base_geometry,
            spatial_bbox=self.base_geometry.envelope,
            instance_properties={"finish": "matte"},
            status=ComponentStatus.PLANNED.value,
            version=1,
            internal_id=next_internal_id
        )
        return instance

    def get_parameters(self):
        """
        Retrieve all parameters associated with this component.
        """
        return self.parameter_set.all()

    def get_material_requirements(self):
        """
        Retrieve all material requirements for this component.
        """
        return self.materialrequirement_set.all()

    def get_documentation(self):
        """
        Retrieve all documentation associated with this component.
        """
        return self.documentation_set.all()