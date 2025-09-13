from django.db import models

class Estate(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    size = models.CharField(max_length=100, help_text="e.g., 5 acres", null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Block(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estate.name} - {self.name}"

class Apartment(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    size = models.DecimalField(max_digits=5, decimal_places=2, null=True, help_text="Size in square meters")
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    number_of_rooms = models.IntegerField(null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amenities = models.ManyToManyField('Amenity', blank=True)
    furnishings = models.ManyToManyField('Furnishing', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.block.estate.name} - {self.block.name} - {self.number}"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name

class Furnishing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('owner', 'Owner'), ('manager', 'Manager'), ('tenant', 'Tenant')], default='tenant')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"