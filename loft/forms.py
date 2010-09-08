from django import forms
from models import Category

class CategoryAdminForm(forms.ModelForm):

    class Meta:
        model = Category
    
    def __init__(self, *args, **kwargs):
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs={'class':'vLargeTextField'}