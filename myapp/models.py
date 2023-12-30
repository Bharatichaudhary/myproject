from django.db import models
from app1.models import CustomUser
from django.db.models import Avg

class destination(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    description = models.TextField()
    keywords = models.TextField(default='Popular')
    image = models.CharField(max_length=500)

    def count_ratings(self):
        return Rating.objects.filter(location=self).count()

    def average_rating(self):
        ratings = Rating.objects.filter(location=self)
        return ratings.aggregate(Avg('rating'))['rating__avg'] or 0

# Assuming your Rating model looks something like this:
class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    location = models.ForeignKey(destination, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f"{self.user.username} - {self.location.name} - {self.rating}"
