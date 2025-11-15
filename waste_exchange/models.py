from django.db import models

class Business(models.Model):
    name = models.CharField(max_length=255)
    waste = models.TextField()
    image = models.ImageField(upload_to='business_images/')
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name
