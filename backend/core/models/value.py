"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

ParameterValue model implementation for the EuroTempl system.
This model represents the concrete values of parameters for specific component instances,
serving as a bridge between abstract parameter definitions and their implementations.
"""

from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from typing import Any, Dict, Optional

class ParameterValue(models.Model):
    """
    The ParameterValue model stores and manages actual values of parameters for specific
    component instances in the EuroTempl system. It maintains data integrity through
    comprehensive validation and supports both simple and complex parameter types.
    """

    # Core fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the parameter value"
    )

    instance = models.ForeignKey(
        'ComponentInstance',
        on_delete=models.CASCADE,
        help_text="Reference to the component instance"
    )

    parameter = models.ForeignKey(
        'Parameter',
        on_delete=models.CASCADE,
        help_text="Reference to the parameter definition"
    )

    value = JSONField(
        help_text="The actual value of the parameter"
    )

    # Tracking and validation fields
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the value was recorded"
    )

    validation_status = models.CharField(
        max_length=50,
        choices=[
            ('valid', 'Valid'),
            ('invalid', 'Invalid'),
            ('pending', 'Pending Validation')
        ],
        default='pending',
        help_text="Current validation status"
    )

    modified_by = models.ForeignKey(
    'auth.User',
    on_delete=models.SET_NULL,
    null=True,
    help_text="User who last modified the value"
)

    # Auto-updated timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'et_parameter_value'
        indexes = [
            models.Index(fields=['instance']),
            models.Index(fields=['parameter']),
            models.Index(fields=['validation_status']),
            models.Index(fields=['recorded_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['instance', 'parameter'],
                name='unique_parameter_per_instance'
            )
        ]

    def clean(self) -> None:
        """
        Validate the parameter value according to EuroTempl business rules.
        """
        self._validate_temporal_integrity()
        self._validate_value_constraints()
        self._validate_required_parameter()
        super().clean()

    def _validate_temporal_integrity(self) -> None:
        """
        Ensure temporal integrity of the value record.
        """
        if self.recorded_at and self.instance.created_at:
            if self.recorded_at < self.instance.created_at:
                raise ValidationError({
                    'recorded_at': 'Value cannot be recorded before instance creation'
                })

    def _validate_value_constraints(self) -> None:
        """
        Validate value against parameter constraints and data type.
        """
        if self.value is None:
            raise ValidationError("Value cannot be None")

        try:
            # Use parameter's validate_value method for type and range validation
            self.parameter.validate_value(self.value.get('value'))
            
            # Validate units if specified
            if self.parameter.units:
                provided_unit = self.value.get('unit')
                if not provided_unit:
                    raise ValidationError("Unit must be specified for this parameter")
                if provided_unit != self.parameter.units:
                    raise ValidationError(f"Invalid unit. Expected {self.parameter.units}")
                    
        except ValidationError as e:
            self.validation_status = 'invalid'
            raise e
        except Exception as e:
            self.validation_status = 'invalid'
            raise ValidationError(f"Validation error: {str(e)}")

    def _validate_required_parameter(self) -> None:
        """
        Ensure required parameters have valid values.
        """
        if self.parameter.is_required and (
            self.value is None or 
            'value' not in self.value or 
            self.value['value'] is None
        ):
            raise ValidationError({
                'value': f"Required parameter {self.parameter.name} must have a value"
            })

    def get_value(self) -> Any:
        """
        Retrieve the actual value from the JSONB field.

        Returns:
            Any: The parameter value
        """
        return self.value.get('value') if isinstance(self.value, dict) else self.value

    def set_value(self, new_value: Any, unit: Optional[str] = None) -> None:
        """
        Set a new value for the parameter, with optional unit specification.

        Args:
            new_value: The new value to set
            unit: Optional unit specification

        Raises:
            ValidationError: If the value or unit is invalid
        """
        if unit and self.parameter.units and unit != self.parameter.units:
            raise ValidationError(f"Invalid unit. Expected {self.parameter.units}")

        value_dict = {
            'value': new_value
        }
        if unit:
            value_dict['unit'] = unit

        self.value = value_dict
        self.validate_and_save()

    def validate_and_save(self, *args, **kwargs) -> None:
        """
        Validate and save the parameter value, updating validation status.
        """
        try:
            self.full_clean()
            self.validation_status = 'valid'
        except ValidationError:
            self.validation_status = 'invalid'
            raise
        
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Override save to handle validation status."""
        # Validate the value before saving
        try:
            self.validate_value()
            self.validation_status = 'valid'
        except ValidationError:
            self.validation_status = 'invalid'
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def validate_value(self):
        """Validate the value against parameter constraints."""
        # Add validation logic here
        # For now, assume all values are valid
        pass

    def __str__(self) -> str:
        """
        String representation of the parameter value.

        Returns:
            str: A string describing the parameter value
        """
        return (
            f"{self.parameter.name} = {self.get_value()} "
            f"({self.validation_status})"
        )