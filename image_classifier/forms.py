from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    labels = forms.CharField(label="Comma separated list of labels (Leave blank to use NCT-CRC-HE-100K colon labels)",
                             widget=forms.TextInput(attrs={
                                 'placeholder': 'colorectal adenocarcinoma epithelium, cancer-associated stroma,'
                                                'normal colon mucosa, lymphocytes, mucus, smooth muscle, adipose,'
                                                'background, debris'
                             }),
                             max_length=255, required=False)
    expected_label = forms.CharField(label="User-provided expected label for comparison (Optional)", max_length=255,
                                     required=False)
