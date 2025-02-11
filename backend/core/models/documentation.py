from django.db import models

class Documentation(models.Model):
    component = models.ForeignKey('core.Component', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    document_type = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['title']
        verbose_name_plural = 'documentation'