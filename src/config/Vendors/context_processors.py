from Vendors.models import Store, Employee

def user_store(request):
    user = request.user
    if user.is_authenticated:
        store = Store.objects.filter(owner=user).first()
        if not store:
            employee = Employee.objects.filter(user=user).first()
            if employee:
                store = employee.store
        return {'store': store}
    return {'store': None}