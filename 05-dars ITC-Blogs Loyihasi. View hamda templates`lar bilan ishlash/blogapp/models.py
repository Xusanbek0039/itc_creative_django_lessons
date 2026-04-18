from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.surname}"
    
    
class Blogs(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title