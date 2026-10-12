from django.db import models


class Location(models.Model):
    """
    Location model to represent physical locations for Donors, Recipients, and Food Listings.
    Reused via get_or_create to prevent redundant location entries.
    """
    address = models.CharField(max_length=255, help_text="Street address or building details")
    area = models.CharField(max_length=100, db_index=True, help_text="Neighborhood or area name")
    city = models.CharField(max_length=100, db_index=True, help_text="City name")
    postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Postal / ZIP code")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        indexes = [
            models.Index(fields=['area'], name='loc_area_idx'),
            models.Index(fields=['city'], name='loc_city_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['address', 'area', 'city', 'postal_code'],
                name='unique_location_address'
            )
        ]

    def __str__(self):
        parts = [self.address, self.area, self.city]
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(filter(None, parts))

    @classmethod
    def get_or_create_location(cls, address, area, city, postal_code=None):
        """
        Safely retrieves or creates a Location instance, normalizing strings
        and preventing MultipleObjectsReturned issues with SQL NULL unique constraints.
        """
        clean_addr = (address or '').strip()
        clean_area = (area or '').strip()
        clean_city = (city or '').strip()
        clean_postal = (postal_code or '').strip() or None

        loc = cls.objects.filter(
            address__iexact=clean_addr,
            area__iexact=clean_area,
            city__iexact=clean_city,
            postal_code=clean_postal
        ).first()

        if not loc:
            loc = cls.objects.create(
                address=clean_addr,
                area=clean_area,
                city=clean_city,
                postal_code=clean_postal
            )
        return loc

