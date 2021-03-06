"""Account management handling forms"""
# pylint: disable=W0232, R0903
import logging

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token

from accounts.models import User
from common.forms import get_bootstrap_helper

LOGGER = logging.getLogger(__name__)


class RegistrationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    error_messages = {
        "duplicate_username": "用户名已存在，请换一个",
        "password_mismatch": "两次密码不一致，请确认是否打错",
    }
    username = forms.RegexField(
        label="用户名",
        max_length=30,
        regex=r"^[\w.@+-]+$",
        help_text=("最长30个字，可包含汉字、字母、数字"),
        error_messages={
            "invalid": (
                "用户名只能包含汉字、字母、数字，以及以下符号："
                "@ . + - _"
            )
        },
    )
    email = forms.EmailField(label="邮箱")
    password1 = forms.CharField(
        label="密码", widget=forms.PasswordInput, max_length=64
    )
    password2 = forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput,
        max_length=64,
        help_text="请再次输入上面输过的密码，以确保你没有打错",
    )

    class Meta:
        """Model and field definitions"""

        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = get_bootstrap_helper(
            ["username", "email", "password1", "password2"], "register", "注册"
        )

    def clean_username(self):
        """Check that no similar username exist in a case insensitive way"""
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        except User.MultipleObjectsReturned:
            LOGGER.warning("Mutiple users with username: %s", username)
        raise forms.ValidationError(self.error_messages["duplicate_username"])

    def clean_password2(self):
        """Check that passwords match"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages["password_mismatch"])
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        Token.objects.create(user=user)
        return user


class LoginForm(AuthenticationForm):
    """Subclass of AuthenticationForm with Bootstrap integration"""

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].label = "用户名"
        self.fields["password"].label = "密码"
        self.helper = get_bootstrap_helper(
            ["username", "password"], "signin", "登录"
        )


class ProfileForm(forms.ModelForm):
    """Form to edit profile information"""

    class Meta:
        """ModelForm configuration"""
        model = User
        fields = ("website", "avatar", "email")

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = get_bootstrap_helper(list(self.Meta.fields), "save", "保存")

    def save(self, commit=True):
        if "email" in self.changed_data:
            self.instance.email_confirmed = False
        return super(ProfileForm, self).save(commit=commit)


class ProfileDeleteForm(forms.Form):
    """Form to ask confirmation for account deletion"""
    confirm_delete = forms.BooleanField(
        label="我确定一定以及肯定要删除我的帐户（请勾选）"
    )

    def clean_confirm_delete(self):
        """Only delete if the user has checked the corresponding checkbox"""
        confirm_delete = self.cleaned_data["confirm_delete"]
        if not confirm_delete:
            raise forms.ValidationError("你没有确认，帐户未删除")
        return confirm_delete
