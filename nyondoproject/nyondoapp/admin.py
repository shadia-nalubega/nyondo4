
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (Product, ProductPricing, Stock, Supplier, Sale,Staff, Scredit, Payment, Customer, Deposit,
)
 


# admin.site.register(ProductPricing)
# admin.site.register(Stock)
# admin.site.register(Supplier)
# admin.site.register(Sale)
# admin.site.register(Staff)
# admin.site.register(Scredit)
# admin.site.register(Payment)
# admin.site.register(Customer)
# admin.site.register(Deposit)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Product, ProductPricing, Stock, Supplier, Sale,
    Staff, Scredit, Payment, Customer, Deposit,
)

# Inline Staff inside User
class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = "Staff Details"
    fk_name = "user"

# Custom User Admin with inline Staff
class CustomUserAdmin(UserAdmin):
    inlines = [StaffInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register all models
admin.site.register(Product)
admin.site.register(ProductPricing)
admin.site.register(Stock)
admin.site.register(Supplier)
admin.site.register(Sale)
admin.site.register(Staff)
admin.site.register(Scredit)
admin.site.register(Payment)
admin.site.register(Customer)
admin.site.register(Deposit)