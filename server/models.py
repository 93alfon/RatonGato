from __future__ import unicode_literals
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Game(models.Model):
	catUser = models.ForeignKey(User, related_name='gamecatUsers')
	mouseUser = models.ForeignKey(User, null=True, related_name='gamemouseUsers')
	cat1 = models.IntegerField(default=0, validators=[MaxValueValidator(63), MinValueValidator(0)])
	cat2 = models.IntegerField(default=2, validators=[MaxValueValidator(63), MinValueValidator(0)])
	cat3 = models.IntegerField(default=4, validators=[MaxValueValidator(63), MinValueValidator(0)])
	cat4 = models.IntegerField(default=6, validators=[MaxValueValidator(63), MinValueValidator(0)])
	mouse = models.IntegerField(default=59, validators=[MaxValueValidator(63), MinValueValidator(0)])
	catTurn = models.BooleanField(default=True);

class Move(models.Model):
	origin = models.IntegerField(validators=[MaxValueValidator(63), MinValueValidator(0)])
	target = models.IntegerField(validators=[MaxValueValidator(63), MinValueValidator(0)])
	game = models.ForeignKey(Game, related_name='game')

class Counter(models.Model):
	counter = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=False)