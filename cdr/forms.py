from django import forms


class CdrFilterForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone number(s)",
        max_length=512,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search one or more numbers: 996555123456, 996312123123",
            }
        ),
        help_text="Separate multiple numbers with commas, spaces, or new lines.",
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

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if not phone_number:
            return []

        separators = [",", "\n", "\r", "\t"]
        normalized_value = phone_number
        for separator in separators:
            normalized_value = normalized_value.replace(separator, " ")

        return normalized_value.split()

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
