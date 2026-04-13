from django import forms


class CdrFilterForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone number",
        max_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search calling/called/redirect numbers",
            }
        ),
    )
    start_date = forms.DateField(
        label="Start date",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )
    end_date = forms.DateField(
        label="End date",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )
