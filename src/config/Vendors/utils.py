from Vendors.models import Employee, Store


def get_user_store(user):
    user_id = getattr(user, 'id', None)
    if not user_id:
        return None
    store = Store.objects.filter(owner_id=user_id, is_deleted=False).first()
    if store:
        return store
    employee = Employee.objects.filter(user_id=user_id, is_deleted=False).first()
    if employee:
        return employee.store
    return None
