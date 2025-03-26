from django.db import models

class WordCount(models.Model):
    word = models.CharField(max_length=100, db_index=True)
    count = models.PositiveIntegerField(default=0)
    file_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('word', 'file_name')

    def __str__(self):
        return f"{self.word}: {self.count}"
# Create your models here.
