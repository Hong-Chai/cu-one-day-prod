from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Имя пользователя",
            "email": "Электронная почта",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Русские подписи для полей паролей
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Подтверждение пароля"
        
        # Русский help_text
        self.fields['username'].help_text = "Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_"
        self.fields['password1'].help_text = "Пароль должен содержать минимум 8 символов и не может состоять только из цифр."
        self.fields['password2'].help_text = ""
        
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"
