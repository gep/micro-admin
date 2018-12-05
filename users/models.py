from django.db import models


class CustomMicroUser(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._persist_hash = ''

    name = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def set_persist_hash(self, hash):
        self._persist_hash = hash

    def get_persist_hash(self):
        return self._persist_hash