from django.db import models


class CurrencyConfig(models.Model):

    base_currency = models.CharField(
        max_length=3,
        default="TZS"
    )

    usd_to_tzs_rate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=2600
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"1 USD = {self.usd_to_tzs_rate} TZS"