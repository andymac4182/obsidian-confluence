"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

ComponentInstance model implementation for the EuroTempl system.
"""
from django.utils import timezone
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator
import uuid
from enum import Enum

class ComponentStatus(str, Enum):
    """Enumeration of possible component instance statuses."""
    PLANNED = 'planned'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'
    OBSOLETE = 'obsolete'

    @classmethod
    def choices(cls):
        return [(status.value, status.name) for status in cls]

class ComponentInstance(gis_models.Model):
    """
    Represents specific implementations of EuroTempl components within a design.
    Maintains detailed information about each instance including spatial data,
    properties, and lifecycle status.
    """

    # Core fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Primary identifier for the instance"
    )

    internal_id = models.IntegerField(
        unique=True,
        db_index=True,
        help_text="Internal sequential identifier for performance optimization"
    )

    component = models.ForeignKey(
        'Component',
        on_delete=models.RESTRICT,
        help_text="Reference to parent Component"
    )

    # Spatial and geometric data
    spatial_data = gis_models.GeometryField(
        dim=3,
        spatial_index=True,
        help_text="3D geometric representation with SFCGAL support"
    )

    spatial_bbox = gis_models.PolygonField(
        null=True,
        help_text="Spatial bounding box for quick filtering"
    )

    # Properties and status
    instance_properties = JSONField(
        default=dict,
        help_text="Flexible instance-specific properties"
    )

    status = models.CharField(
        max_length=20,
        choices=ComponentStatus.choices(),
        default=ComponentStatus.PLANNED.value,
        help_text="Current status in lifecycle"
    )

    version = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Version number of the instance"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When instance was created"
    )

    modified_at = models.DateTimeField(
        auto_now=True,
        help_text="When instance was last modified"
    )

    status_changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When status was last changed"
    )

    class Meta:
        db_table = 'et_component_instance'
        indexes = [
            models.Index(fields=['internal_id']),
            models.Index(fields=['status']),
            models.Index(fields=['component']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        """Validate the component instance according to EuroTempl business rules."""
        self._validate_spatial_integrity()
        self._validate_grid_alignment()
        self._validate_property_schema()
        self._validate_temporal_consistency()

    def _validate_spatial_integrity(self):
        """Ensure geometric data is valid 3D objects."""
        if not self.spatial_data or not self.spatial_data.valid:
            raise ValidationError({
                'spatial_data': 'Must provide valid 3D geometric data'
            })

    def _validate_grid_alignment(self):
        """Validate alignment with 25mm base grid."""
        if not self.spatial_data:
            return

        coords = self.spatial_data.coords
        for coord in coords[0]:
            x, y, z = coord
            if any(c % 25 != 0 for c in (x, y)):
                raise ValidationError({
                    'spatial_data': 'Geometry must align with 25mm grid system'
                })

    def _validate_property_schema(self):
        """Validate instance properties conform to component-defined schemas."""
        if not isinstance(self.instance_properties, dict):
            raise ValidationError({
                'instance_properties': 'Properties must be a dictionary'
            })

        # Additional property validation should be implemented here
        # based on component-specific requirements

    def _validate_temporal_consistency(self):
        """Ensure temporal consistency of timestamps."""
        if self.modified_at and self.created_at and self.modified_at < self.created_at:
            raise ValidationError('Modified timestamp cannot be earlier than created timestamp')

    def update_status(self, new_status):
        """
        Update the instance status and record the timestamp.
        
        Args:
            new_status (str): New status value from ComponentStatus enum
        """
        valid_statuses = [status.value for status in ComponentStatus]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.save()

    def create_new_version(self):
        """Create a new version of this instance."""
        # Get the next available internal_id
        last_internal_id = ComponentInstance.objects.all().order_by('-internal_id').first()
        next_internal_id = (last_internal_id.internal_id + 1) if last_internal_id else 1
    
        new_instance = ComponentInstance.objects.create(
            component=self.component,
            spatial_data=self.spatial_data,
            spatial_bbox=self.spatial_bbox,
            instance_properties=self.instance_properties,
            version=self.version + 1,
            status=self.status,
            internal_id=next_internal_id 
        )
        return new_instance
    def calculate_bounding_box(self):
        """Calculate and update the spatial bounding box."""
        if self.spatial_data:
            self.spatial_bbox = self.spatial_data.envelope3d
            self.save(update_fields=['spatial_bbox'])

    def save(self, *args, **kwargs):
        """Override save to ensure validation, bounding box calculation, and internal_id."""
        self.full_clean()
        if self._state.adding:
            last_internal_id = ComponentInstance.objects.all().order_by('-internal_id').first()
            self.internal_id = (last_internal_id.internal_id + 1) if last_internal_id else 1
        if not self.spatial_bbox and self.spatial_data:
            self.calculate_bounding_box()
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the component instance."""
        return f"{self.component.name} Instance {self.internal_id} (v{self.version})"