from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user
from .models import Product

# Register your models here.


@admin.register(Product)
class ProductAdmin(GuardedModelAdmin):
    list_display = ('name',)

    # determining whether a module should appear on the index page for a user
    def has_module_permission(self, request):
        if super().has_module_permission(request):  # super().has_module_permission(request) will return true or false
            return True
        # if user does have OLP in the model then this would return true
        return self.get_model_objects(request).exists()

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        data = self.get_model_objects(request)
        return data

    # get all the rows of data that the user does have
    # permission to access and we're utilizing get_objects_for_user
    # from guardian to help us perform this operation
    def get_model_objects(self, request, action=None, klass=None):
        opts = self.opts  # access meta data
        actions = [action] if action else ['view', 'edit', 'delete']
        klass = klass if klass else opts.model
        model_name = klass._meta.model_name
        print("From get_objects_for_user: ", opts,
              actions, klass, model_name, request.user)
        return get_objects_for_user(user=request.user, perms=[f'{perm}_{model_name}' for perm in actions], klass=klass, any_perm=True)

    # funtion to check whether user has permission to crud for particular obj
    def has_permission(self, request, obj, action):
        opts = self.opts
        print("From has par------------: ", opts, action, obj)
        code_name = f'{action}_{opts.model_name}'
        if obj:
            return request.user.has_perm(f'{opts.app_label}.{code_name}', obj)
        else:
            return self.get_model_objects(request).exists()

    def has_view_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'view')

    def has_change_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'change')

    def has_delete_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'delete')
