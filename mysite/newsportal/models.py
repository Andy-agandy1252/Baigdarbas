from django.db import models
from django.urls import reverse

# Create your models here.
class Article(models.Model):
    antraste = models.CharField('Antraste', max_length=100)
    kategorija = models.CharField('Kategorija', max_length=30)
    autorius = models.CharField('Autorius', max_length=50)
    naujiena = models.TextField('Jusu naujiena')
    paskelbimo_data = models.TimeField()

    def __str__(self):
        return f'{self.antraste} {self.kategorija} {self.autorius} {self.naujiena} {self.paskelbimo_data}'
    
class Reklama(models.Model):
    nuotrauka = models.ImageField(upload_to='Reklamos_images/', blank=True, null=True)
    papildoma_info = models.TextField('Rusu reklamos textas')


    def __str__(self):
        return f'{self.nuotrauka} {self.papildoma_info}'
