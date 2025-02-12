from django.db import models

class MaterialRequirement(models.Model):
    component = models.ForeignKey('core.Component', on_delete=models.CASCADE)
    material_code = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['material_code']