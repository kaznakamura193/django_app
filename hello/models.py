from django.db import models
from django.core.validators import URLValidator

class Friend(models.Model):
    name = models.CharField(max_length=100,\
        validators=[URLValidator()])
    mail = models.EmailField(max_length=200)
    gender = models.BooleanField()
    age = models.IntegerField()
    birthday = models.DateField()
    
    def __str__(self):
        return '<Friend:id='+ str(self.id) + ', '+ \
            self.name + '(' + str(self.age) +')>'
           
           