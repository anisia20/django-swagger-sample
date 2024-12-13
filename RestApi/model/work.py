# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Work(models.Model):
    filename = models.CharField()
    file = models.FileField()