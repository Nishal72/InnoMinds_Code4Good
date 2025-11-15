from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Business(models.Model):
    name = models.CharField(max_length=255)
    waste = models.TextField()
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="businesses")

    def __str__(self):
        return self.name


class BusinessImage(models.Model):
    business = models.ForeignKey(
        Business,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='business_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name} image"
    


