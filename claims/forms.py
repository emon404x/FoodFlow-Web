from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator
from .models import Claim


class ClaimForm(forms.Form):
    """
    Form used by verified Recipients to claim a quantity of food.
    """
    claimed_quantity = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'min': '0.01',
            'id': 'id_claimed_quantity',
            'placeholder': 'Enter quantity to claim'
        }),
        label="Quantity to Claim"
    )

    def __init__(self, *args, max_available=None, unit="units", **kwargs):
        super().__init__(*args, **kwargs)
        if max_available is not None:
            try:
                self.max_available = Decimal(str(max_available))
            except Exception:
                self.max_available = None
        else:
            self.max_available = None

        if self.max_available is not None:
            self.fields['claimed_quantity'].widget.attrs['max'] = str(self.max_available)
            self.fields['claimed_quantity'].help_text = f"Available to claim: up to {self.max_available} {unit}"

    def clean_claimed_quantity(self):
        qty = self.cleaned_data.get('claimed_quantity')
        if qty is None or not qty.is_finite() or qty <= Decimal('0.00'):
            raise forms.ValidationError("Please enter a valid quantity greater than zero.")
        if self.max_available is not None and qty > self.max_available:
            raise forms.ValidationError(f"Cannot claim more than the available quantity ({self.max_available}).")
        return qty


class PickupVerificationForm(forms.Form):
    """
    Form used by Donors to verify the 8-character pickup code presented by the recipient.
    """
    pickup_code = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-input code-input',
            'placeholder': '8-CHAR CODE (e.g. 4F9B2C1A)',
            'style': 'text-transform: uppercase; letter-spacing: 0.15em; font-family: monospace; font-size: 1.25rem; text-align: center;'
        }),
        label="Enter Recipient's Pickup Code"
    )

    def clean_pickup_code(self):
        code = self.cleaned_data.get('pickup_code', '').strip().upper()
        if len(code) != 8:
            raise forms.ValidationError("Pickup code must be exactly 8 characters long.")
        return code
