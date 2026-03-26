from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['category'].empty_label = 'Выберите категорию'
        self.fields['location'].empty_label = 'Не выбрано'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ваш комментарий...',
                'class': 'form-control'
            })
        }
        labels = {
            'text': 'Текст комментария'
        }