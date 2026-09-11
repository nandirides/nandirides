from django.db import models
from core.models import TimeStampedModel


class Country(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class State(TimeStampedModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="states",
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(TimeStampedModel):
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name="cities",
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Location(TimeStampedModel):
    address = models.CharField(max_length=500)

    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    def __str__(self):
        return self.address