from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    labels = forms.CharField(label="Comma separated list of labels (Leaving blank defaults to colon tissue"
                                   " classifications)", max_length=255, required=False)
