from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from account.models import CustomUser, Staff


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean(self):
        datas = super().clean()
        p1 = datas.get("password1")
        p2 = datas.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "your confirm password and password does not match")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admins
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ["nickname", "phonenumber", "email",
                  "password", "firstname", "lastname", "how_know_us", "is_active", "is_admin"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["nickname", "phonenumber", "firstname", "lastname", "how_know_us", "is_active", "is_admin"]
    search_field = ["phonenumber", "email"]
    list_filter = ["is_admin", "created"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["nickname", "phonenumber", "firstname", "lastname"]}),
        ("General info", {"fields": ["how_know_us"]}),
        ("Permissions", {"fields": ["is_active", "is_admin", "is_customer", "groups", "user_permissions"]}),
    ]
    # show_facets = admin.ShowFacets.ALWAYS
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["nickname", "phonenumber", "email", "firstname",
                           "lastname", "password1", "password2", "how_know_us"],
            },
        ),
    ]
    ordering = ["email", "created"]
    filter_horizontal = []


admin.site.register(Staff)

# Unregister the default Group admin
admin.site.unregister(Group)


class CustomGroupAdmin(GroupAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.user = None

    def has_permission(request):
        return request.user.is_authenticated and request.user.is_admin


# Now register the new UserAdmin...
admin.site.register(CustomUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# Register Group with the custom admin class
admin.site.register(Group)
