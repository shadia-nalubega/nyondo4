from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


def validate_ug_phone(value):
    pattern = r'^(?:\+256|0)(7\d{8})$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid Ugandan phone number (e.g., 07XXXXXXXX or +2567XXXXXXXX)")



# NIN validation (Uganda NIN is 13 characters)
def validate_nin(value):
    if len(value) != 14:
        raise ValidationError("NIN must be 14 characters")

class Supplier(models.Model):
    company_name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=100, blank=False)
    TRN = models.CharField(max_length=50, blank=False, unique=True)
    phone = models.CharField(max_length=15, validators=[validate_ug_phone])
    product_description = models.TextField(blank=False)
    payment_option = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.company_name

 

class Scredit(models.Model):
    ACTIVITY =[
        ("pending", "pending"),
        ("active", "active"),
        ("overdue", "overdue")
    ]
    company_name = models.ForeignKey(Supplier ,on_delete=models.CASCADE)# we gave a single credit to be called item, so to access the variable we will say item.company_name and the name of the field in the supplier credit form
    quantity = models.IntegerField(blank=False)
    amount_owed = models.IntegerField(blank=False)
    status = models.CharField(max_length=20, choices=ACTIVITY)
    notes = models.TextField(blank=True)

class Payment(models.Model):
    supplier_name = models.CharField(blank=False, max_length=255, unique=True)
    product_description = models.CharField(blank=False, max_length=255)
    amount_paid = models.IntegerField(blank=False)
    payment_date = models.DateField(auto_now_add=True)
    balance_remaining = models.IntegerField(blank=False)
    comments = models.TextField()


class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    unit_cost = models.IntegerField()
    current_stock = models.IntegerField(default=0)
    threshold = models.IntegerField(default=10)
    last_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.product_name


class Stock(models.Model):

    description = models.TextField()
    quantity = models.IntegerField()
    units = models.CharField(max_length=20)    
    unit_price = models.IntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='stocks')
    date = models.DateField(auto_now_add=True)


class Sale(models.Model):
    cashier = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)  # Store the name directly
    quantity = models.IntegerField()
    selling_price = models.IntegerField()  # Store the price at time of sale
    distance = models.IntegerField(default=0)
    total_amount = models.IntegerField()
    transport_fee = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    payment = models.CharField(max_length=50)  # Cash, Mobile Money, etc.
    customer_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.date}"


    
class Customer(models.Model):
    customer_name = models.CharField(max_length=30, blank=False)
    phone = models.CharField(max_length=15, validators=[validate_ug_phone])
    product_name = models.CharField(max_length=100, blank=False)
    nin = models.CharField(max_length=14, validators=[validate_nin])
    location = models.CharField(max_length=100)
    total_price = models.IntegerField()


class Deposit(models.Model):
    STATUS = [
        ("Active","Active"),
        ("Pending","Pending"),
        ("Finished","Finished")
    ]
    PRODUCT = [
        ("cement","cement"),
        ("iron sheets","iron sheets"),
        ("iron bars","iron bars"),

    ]   
    
    Customer_name = models.ForeignKey(Customer, on_delete=models.CASCADE)
    deposit_date = models.DateField(auto_now_add=True)
    deposit_amount = models.IntegerField()
    expected_completion = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS)
    product_name = models.CharField(max_length=100, choices=PRODUCT)


class Staff(models.Model):
    ROLES =[
        ("admin","admin"),
        ("sales_attendant","sales_attendant"),
        ("store_manager","store_manager")
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50)
    role = models.CharField(max_length=50, choices=ROLES)


class ProductPricing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, unique=True)  
    wholesaler_rate = models.IntegerField(default=0)
    wholesaler_price = models.IntegerField(default=0)
    retailer_rate = models.IntegerField(default=0)
    retailer_price = models.IntegerField(default=0)
    normal_rate = models.IntegerField(default=0)
    normal_price = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.product_name} - Pricing"



