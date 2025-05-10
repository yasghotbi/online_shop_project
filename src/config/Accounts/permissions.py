# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType
# from Vendors.models import Store
#

# owner_group = Group.objects.get_or_create(name='store_owner')[0]
# employee_group = Group.objects.get_or_create(name='employee')[0]
# admin_group = Group.objects.get_or_create(name='admin')[0]
# customer_group = Group.objects.get_or_create(name='customer')[0]
#

# content_type = ContentType.objects.get_for_model(Store)
# can_edit_store = Permission.objects.get_or_create(
#     codename='can_edit_store',
#     name='Can edit store',
#     content_type=content_type
# )[0]
#

# owner_group.permissions.add(can_edit_store)
# admin_group.permissions.add(can_edit_store)
