from django import forms
from .models import Post, Comment, Category, Location


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location', 'pub_date', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_published=True)
        self.fields['location'].queryset = Location.objects.filter(is_published=True)
        self.fields['location'].empty_label = 'Не выбрано'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)