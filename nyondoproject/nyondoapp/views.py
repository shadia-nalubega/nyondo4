from urllib import request

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

# Create your views here.
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import date
from nyondoapp.models import Supplier, Payment, Scredit, Stock, Sale, Product, Customer, Deposit, Staff, ProductPricing

# AUTHENTICATION VIEWs

def login_view(request):
    # Show login page for GET requests
    if request.method != "POST":
        return render(request, "login.html")
    
    # Get form data
    username_or_email = request.POST.get("username")
    password = request.POST.get("password")
    
    # Try to login with username
    user = authenticate(request, username=username_or_email, password=password)
    
    # If that didn't work, check if they entered an email
    if user is None:
        # Look for user with their  email
        users = User.objects.filter(email=username_or_email)
        if users:
            # now authenticate with the username of the first user with that email
            user = authenticate(request, username=users[0].username, password=password)
    
    # If still no user, show error
    if user is None:
        return render(request, "login.html", {"error": "Invalid username/email or password"})
    
    # Login successful but the user might not have a staff record, so we check that in the next step before allowing access to dashboards
    login(request, user)
    
    # Find staff record to get role and since we are using a queryset of filter we shall use not coz the results are never none
    staff_list = Staff.objects.filter(user=user)
    if not staff_list:
        return render(request, "login.html", {"error": "No staff record found"})
    
    # Save role in session
    staff = staff_list[0]
    request.session["role"] = staff.role
    
    # Go to correct dashboard
    if staff.role == "admin":
        return redirect("dash")
    elif staff.role == "sales_attendant":
        return redirect("sales_dash")
    elif staff.role == "store_manager":
        return redirect("stock_dash")
    else:
        return render(request, "login.html", {"error": "Invalid user role"})
    



def logout_page(request):
    if request.method == 'POST':
        logout(request)
        request.session.flush()
        return render(request, 'logout.html')
    return render(request, 'logout.html')
def land(request):
    return render(request, "land.html")

# ADMIN DASHBOARD 
@never_cache



@never_cache
def dash(request):
    if request.session.get("role") != "admin":
        return redirect("login")
    
    today = date.today()
    
    # Stock added today
    total_stock_count = Stock.objects.filter(date=today).count()
    
    # Suppliers who supplied stock today – FIXED: use 'stocks'
    total_suppliers = Supplier.objects.count()
    
    # Sales made today
    today_sales = Sale.objects.filter(date=today)
    total_sales = today_sales.count()
    
    # Revenue from today's sales
    total_revenue = sum(sale.total_amount + sale.transport_fee for sale in today_sales)
    
    # For the table – show all suppliers (or you can leave as is)
    suppliers = Supplier.objects.all().order_by('-id')
    
    context = {
        'suppliers': suppliers,
        'total_stock_count': total_stock_count,
        'total_suppliers': total_suppliers,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
    }
    return render(request, 'account/dash.html', context)
    
@never_cache
def stock_dash(request):
    if request.session.get("role") != "store_manager":
        return redirect("login")
    
    all_stock = Stock.objects.select_related().order_by('-id')
    total_stock_count = Stock.objects.count()
    today = date.today()
    todays_stock_count = Stock.objects.filter(date=today).count()
    low_stock_count = Stock.objects.filter(quantity__lt=10).count()
    low_stock_items = Stock.objects.filter(quantity__lt=10)   # the actual records
    
    total_value = 0
    for item in all_stock:
        total_value += item.quantity * item.unit_price
    
    return render(request, 'stock/stock_dash.html', {
        'stock_items': all_stock,
        'total_stock': total_stock_count,
        'todays_stock': todays_stock_count,
        'low_stock': low_stock_count,
        'total_value': total_value,
        'low_stock_items': low_stock_items, 
    })

@never_cache
def sales_dash(request):
    if request.session.get("role") != "sales_attendant":
        return redirect("login")
    
    today = date.today()
    all_sales = Sale.objects.all().order_by('-id')
    today_sales_total = Sale.objects.filter(date=today).count()
    today_deposits_total = Deposit.objects.filter(deposit_date=today).count()
    complete_receipts = Sale.objects.count()
    pending_receipts = Deposit.objects.filter(status='Pending').count()
    
    
    return render(request, 'sales/sales_dash.html', {
        'new_sale': all_sales,
        'today_sales_total': today_sales_total,
        'today_deposits_total': today_deposits_total,
        'complete_receipts': complete_receipts,
        'pending_receipts': pending_receipts,
    })

# ==================== SUPPLIER ====================
def view_supplier_credit(request, id):
    credit = get_object_or_404(Scredit, id=id)
    return render(request, 'account/view_supplier_credit.html', {'credit': credit})

def update_supplier_credit(request, id):
    credit = get_object_or_404(Scredit, id=id)
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_name')
        credit.company_name = get_object_or_404(Supplier, id=supplier_id)
        credit.quantity = request.POST.get('quantity')
        credit.amount_owed = request.POST.get('amount_owed')
        credit.status = request.POST.get('status')
        credit.notes = request.POST.get('notes')
        credit.save()
        return redirect('supplier_credit_table')
    suppliers = Supplier.objects.all()
    return render(request, 'account/update_supplier_credit.html', {'credit': credit, 'suppliers': suppliers})

def delete_supplier_credit(request, id):
    credit = get_object_or_404(Scredit, id=id)
    if request.method == 'POST':
        credit.delete()
    return redirect('supplier_credit_table')


# def supplier_registration(request):
#     if request.method == 'POST':
#         supplier = Supplier.objects.create(
#             company_name=request.POST['company_name'],
#             location=request.POST['location'],
#             product_description=request.POST['product_description'],
#             phone=request.POST['phone'],
#             email=request.POST['email'],
#             TRN=request.POST['TRN'],
#             payment_option=request.POST['payment_option']
#         )
#         return redirect('supplier_list')
#     return render(request, 'account/supplier_registration.html')
def supplier_registration(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        TRN = request.POST.get('TRN', '').strip()
        location = request.POST.get('location', '').strip()
        email = request.POST.get('email', '').strip()
        product_description = request.POST.get('product_description', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment_option = request.POST.get('payment_option', '').strip()

     
        errors = {}

        if not company_name:
            errors['company_name'] = 'Company name is required.'
        if not TRN:
            errors['TRN'] = 'TRN is required.'
        elif Supplier.objects.filter(TRN=TRN).exists():
            errors['TRN'] = 'A supplier with this TRN already exists.'
        if not location:
            errors['location'] = 'Location is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        if not product_description:
            errors['product_description'] = 'Product description is required.'

      
        if errors:
            return render(request, 'account/supplier_registration.html', {
                'errors': errors,
                'company_name': company_name,
                'TRN': TRN,
                'location': location,
                'email': email,
                'phone': phone,
                'product_description': product_description,
                'payment_option': payment_option,
            })

      
        Supplier.objects.create(
            company_name=company_name,
            TRN=TRN,
            location=location,
            email=email,
            product_description=product_description,
            phone=phone,
            payment_option=payment_option,
        )
        return redirect('supplier_list')

    return render(request, 'account/supplier_registration.html')

def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-id')
    return render(request, 'account/supplier_list.html', {'suppliers': suppliers})

def supplier_credit_register(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_name')#we are creating the drop down options saying if the supplier name is selected then// also we are getting the id of the selected id in the drop
      
        supplier = Supplier.objects.get(id=supplier_id) # check the db and return the name of the supplier id selected in the table.
        Scredit.objects.create(
            company_name=supplier,# if not defined up it would give an errorsaying object undefined. at this point we are also creating the data in the db while collecting it from the form.
            quantity=request.POST.get('quantity', 0),
            amount_owed=request.POST.get('amount_owed', 0),
            status=request.POST.get('status', 'Pending'),
            notes=request.POST.get('notes', '')
        )
        return redirect('supplier_credit_table')
    suppliers = Supplier.objects.all()# we are fetching all the suppliers to be able to show them in the drop down options in the supplier credit registration form, this is because we want to link the credit to a specific supplier and also to avoid errors of misspelling the supplier name when registering a credit, so we are using the supplier names that are already in the db and showing them as options in the drop down menu in the form.
    return render(request, 'account/supplier_credit.html', {'suppliers': suppliers})

def supplier_credit_table(request):
    supplier = Scredit.objects.all().order_by('-id')# just quering the db to get all the data in the supplier credit table and showing it in the template, we are also ordering it by id in descending order to show the latest credit at the top of the table.
    return render(request, 'account/supplier_credit_table.html', {'supplier': supplier})

def view_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    return render(request, 'account/view_supplier.html', {'supplier': supplier})

def update_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        supplier.company_name = request.POST.get('company_name')
        supplier.email = request.POST.get('email')
        supplier.phone = request.POST.get('phone')
        supplier.TRN = request.POST.get('TRN')
        supplier.product_description = request.POST.get('product_description')
        supplier.payment_option = request.POST.get('payment_option')
        supplier.save()
        return redirect('supplier_list')
    return render(request, 'account/update_supplier.html', {'supplier': supplier})

def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')

#  PAYMENT 
def view_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    return render(request, 'account/view_payment.html', {'payment': payment})

def update_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    if request.method == 'POST':
        payment.supplier_name = request.POST.get('supplier_name')
        payment.product_description = request.POST.get('product_description')
        payment.payment_date = request.POST.get('payment_date')
        payment.amount_paid = request.POST.get('amount_paid')
        payment.balance_remaining = request.POST.get('balance_remaining')
        payment.comments = request.POST.get('comments')
        payment.save()
        return redirect('payment_table')
    return render(request, 'account/update_payment.html', {'payment': payment})

def delete_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    if request.method == 'POST':
        payment.delete()
    return redirect('payment_table')



def payment_register(request):
    if request.method == 'POST':
        Payment.objects.create(
            supplier_name=request.POST['supplier_name'],
            product_description=request.POST['product_description'],
            payment_date=request.POST['payment_date'],
            amount_paid=request.POST['amount_paid'],
            balance_remaining=request.POST['balance_remaining'],
            comments=request.POST['comments']
        )
        return redirect('payment_table')
    
    products = Product.objects.all().order_by('product_name')  # <-- fetch products
    return render(request, 'account/payment.html', {'products': products})  # <-- pass them
def payment_table(request):
    payment = Payment.objects.all().order_by('-id')
    return render(request, 'account/payment_table.html', {'payment': payment})

# STOCK 
# this view handles the stock get request until the user presses set prices, it halso gets the pdt name and the cost price into the next session
def stock_reg(request):
    if request.session.get("role") not in ["admin", "store_manager"]:
        return redirect("login")

    # HANDLE POST FROM "SET PRODUCT PRICES" BUTTON
    if request.method == "POST":
# here we are storing the data temporarily in the session so that we can access it in the price view and pre-fill the form with that data, this is
#  because we want to make it easy for the user to set the prices for a product they just added to stock without having to re-enter the product name
#  and cost price, so we are using the session to pass that data between the two views. we are also using get method to avoid errors in case some of 
# the fields are not filled in the form, for example if the user does not enter a cost price then we want to store 0 in the session instead of getting an error.
        request.session['temp_product_name'] = request.POST.get('temp_product_name')
        request.session['temp_product_id'] = request.POST.get('temp_product_id')
        request.session['temp_cost_price'] = request.POST.get('temp_cost_price')
        request.session['temp_quantity'] = request.POST.get('temp_quantity')

        return redirect('price')
    
    """Display stock registration form"""
    products = Product.objects.all().order_by('product_name')
    suppliers = Supplier.objects.all()
    
    # Get pricing data from session if it exists
    temp_pricing = request.session.get('temp_pricing', {})
    
    context = {
        'products': products,
        'suppliers': suppliers,
        'temp_pricing': temp_pricing,
    }
    
    return render(request, 'stock/stock_reg.html', context)
# this one handles the return of the user and the form submissions


def supplier_registration_stock(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        TRN = request.POST.get('TRN', '').strip()
        location = request.POST.get('location', '').strip()
        email = request.POST.get('email', '').strip()
        product_description = request.POST.get('product_description', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment_option = request.POST.get('payment_option', '').strip()

        errors = {}
        if not company_name:
            errors['company_name'] = 'Company name is required.'
        if not TRN:
            errors['TRN'] = 'TRN is required.'
        elif Supplier.objects.filter(TRN=TRN).exists():
            errors['TRN'] = 'A supplier with this TRN already exists.'
        if not location:
            errors['location'] = 'Location is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        if not product_description:
            errors['product_description'] = 'Product description is required.'

        if errors:
            return render(request, 'account/supplier_registration_stock.html', {
                'errors': errors,
                'company_name': company_name,
                'TRN': TRN,
                'location': location,
                'email': email,
                'phone': phone,
                'product_description': product_description,
                'payment_option': payment_option,
            })

        Supplier.objects.create(
            company_name=company_name,
            TRN=TRN,
            location=location,
            email=email,
            product_description=product_description,
            phone=phone,
            payment_option=payment_option,
        )
        return redirect('stock_page')

    return render(request, 'stock/supplier_registration_stock.html')
def stock_register(request):
    if request.session.get("role") not in ["admin", "store_manager"]:
        return redirect("login")
    if request.method == "POST":
        # Get basic stock information from the form
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('product_name')
        supplier_id = request.POST.get('supplier')
        units = request.POST.get('units', 'pieces')
        quantity = request.POST.get('quantity', 0)
        cost_price = request.POST.get('cost_price', 0)
        
        # Get pricing information from hidden form fields
        wholesaler_rate = request.POST.get('wholesale_rate', '0')
        wholesaler_price = request.POST.get('wholesale_price', '0')
        retailer_rate = request.POST.get('retail_rate', '0')
        retailer_price = request.POST.get('retail_price', '0')
        normal_rate = request.POST.get('normal_rate', '0')
        normal_price =  request.POST.get('normal_price', '0')
        # here we are converting them to numbers to be able to do calculations with them later on, we are also using try except to handle the case
        #  where the user does not enter a value for the quantity or cost price, in that case we want to store 0 in the database instead of getting an error.
        try:
            quantity = int(quantity) if quantity else 0
        except:
            quantity = 0
            
        # Convert cost price to number
        try:
            cost_price = int(cost_price) if cost_price else 0
        except:
            cost_price = 0
        
        # Convert all price values to numbers 
        #“I use a try-except block. Inside the try, I try to convert each value to an integer. If the value is empty,
        #  I use 0. If the conversion fails because of a letter or strange character, the except catches the error and sets the value to 0. This way the program never breaks.”
        try:
            wholesaler_rate = int(wholesaler_rate) if wholesaler_rate else 0
            wholesaler_price = int(wholesaler_price) if wholesaler_price else 0
            retailer_rate = int(retailer_rate) if retailer_rate else 0
            retailer_price = int(retailer_price) if retailer_price else 0
            normal_rate = int(normal_rate) if normal_rate else 0
            normal_price = int(normal_price) if normal_price else 0
        except:
            wholesaler_rate = wholesaler_price = retailer_rate = retailer_price = normal_rate = normal_price = 0
        
        # Check if supplier was selected we are clearly displaying all the suppliers, if none is selected, do the error
        if not supplier_id:
            suppliers = Supplier.objects.all()
            return render(request, 'stock/stock_reg.html', {'suppliers': suppliers, 'error': 'Please select a supplier'})
        #
        # Get the supplier from database, the one selected in the drop down menu in the form, .
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            suppliers = Supplier.objects.all()
            return render(request, 'stock/stock_reg.html', {'suppliers': suppliers, 'error': 'Selected supplier does not exist'})
        
        # Check if product already exists
       
    
    # this helps in a creating a new record for the newly updated existing pdtin the tab hence helping with viewing the threshold
        product = Product.objects.filter(product_name=product_name).first()

        if product:
            product.current_stock += quantity # if the product already exists we just update the current stock by adding the new quantity to the existing stock, 
            #this is because we want to keep track of the total stock for that product and not overwrite it with the new quantity, we also update the unit cost in case it has changed with the new stock addition, this is important for accurate pricing and profit calculations later on.
            product.unit_cost = cost_price
            product.save()
        else:
            product = Product.objects.create(# else crete a new record for the new pdt in the product table, this is important for data integrity and also for the functionality of the app, for example when we want to add stock for a product we need to have a product record to link the stock to, so we create the product record here if it does not exist when we are saving the stock data.
            product_name=product_name,
            unit_cost=cost_price,
            current_stock=quantity,
            threshold=10
    )
        
        # Save the pricing information
        
        pricing = ProductPricing.objects.filter(product_name=product_name).first()

        if pricing:
            pricing.wholesaler_rate = wholesaler_rate
            pricing.wholesaler_price = wholesaler_price
            pricing.retailer_rate = retailer_rate
            pricing.retailer_price = retailer_price
            pricing.normal_rate = normal_rate
            pricing.normal_price = normal_price
            pricing.save()
        else:
            ProductPricing.objects.create(
            product_name=product_name,
            wholesaler_rate=wholesaler_rate,
            wholesaler_price=wholesaler_price,
            retailer_rate=retailer_rate,
            retailer_price=retailer_price,
            normal_rate=normal_rate,
            normal_price=normal_price,
    )
        
        # Record the stock transaction here we are finally storing the data of that stock item being registered
        Stock.objects.create(
            description=product_name,
            quantity=quantity,
            units=units,
            unit_price=cost_price,
            supplier=supplier
)  
# for this part we are removing the data stored in the session so that after save of the stock item, it dissapears and therefore not interfer with the next session.
        for key in ['temp_wholesale_rate', 'temp_wholesale_price', 'temp_retail_rate',
            'temp_retail_price', 'temp_normal_rate', 'temp_normal_price',
            'temp_product_id', 'temp_product_name', 'temp_cost_price', 'temp_quantity']:
            request.session.pop(key, None)
        # Show success message and go to price list
        messages.success(request, f'Stock and prices for {product_name} added successfully!')
        return redirect('pricing_table')
    
    suppliers = Supplier.objects.all()
    return render(request, 'stock/stock_reg.html', {'suppliers': suppliers})



def stock_page(request):
    all_stock = Stock.objects.select_related().order_by('-id')
    return render(request, 'stock/stock_page.html', {'stock_items': all_stock})

def track(request):
    if request.session.get("role") not in ["admin", "store_manager", "sales_attendant"]:
        return redirect("login")
    products = Product.objects.all()
    total_products = products.count()
    total_units = 0
    low_stock_count = 0
    
    for product in products:
        total_units += product.current_stock
        if product.current_stock < product.threshold and product.current_stock > 0:
            low_stock_count += 1
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_units': total_units,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'stock/track.html', context)

def view_stock(request, pk):
    single_stock = get_object_or_404(Stock, id=pk)
    return render(request, 'stock/view_stock.html', {'item': single_stock})

def update_stock(request, pk):
    if request.session.get("role") not in ["admin", "store_manager"]:
        return redirect("login")  
    stock = get_object_or_404(Stock, id=pk)
    
    if request.method == 'POST':
        stock.product_id = request.POST.get('product_id')
        stock.description = request.POST.get('description')
        stock.quantity = request.POST.get('quantity')
        stock.unit_price = request.POST.get('unit_price')
        stock.supplier_id = request.POST.get('supplier')
        stock.buyer_type = request.POST.get('buyer_type')
        stock.save()
        messages.success(request, 'Stock updated successfully!')
        return redirect('stock_page')
    
    suppliers = Supplier.objects.all()
    return render(request, 'stock/update_stock.html', {
        'item': stock,
        'suppliers': suppliers
    })

def delete_stock(request, pk):
    if request.session.get("role") not in ["admin", "store_manager"]:
        return redirect("login")
    stock_item = get_object_or_404(Stock, id=pk)
    
    if request.method == 'POST':
        stock_item.delete()
        messages.success(request, 'Stock deleted successfully!')
        return redirect('stock_dash')
    
    return render(request, 'stock/delete_stock.html', {'stock': stock_item})

def stock_report(request):
    products = Product.objects.all()
    total_products = products.count()
    total_units = 0
    low_stock_count = 0
    out_of_stock = 0
    
    for product in products:
        total_units += product.current_stock
        if product.current_stock <= 0:
            out_of_stock += 1
        elif product.current_stock < product.threshold:
            low_stock_count += 1
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_units': total_units,
        'low_stock_count': low_stock_count,
        'out_of_stock': out_of_stock,
    }
    return render(request, 'stock/stock_report.html', context)

#
#  PRICING

def price(request):
    """Display pricing form for a selected product"""
    if request.session.get("role") not in ["admin", "store_manager", "sales_attendant"]:
        return redirect("login")
    
    # Check session first (when coming back from edit)
    temp_pricing = request.session.get('temp_pricing', {})
    
    # Get from URL or session
    product_name = request.GET.get('product_name', temp_pricing.get('product_name', ''))
    cost_price = request.GET.get('cost_price', temp_pricing.get('cost_price', ''))
    
    # If editing existing price
    pricing_id = request.GET.get('pricing_id', '')
    pricing_data = None
    
    if pricing_id:
        try:
            pricing_data = ProductPricing.objects.get(id=pricing_id)
            product_name = pricing_data.product_name
        except ProductPricing.DoesNotExist:
            pass
    
    context = {
        'product_name': product_name,
        'cost_price': cost_price,
        'pricing_data': pricing_data,
    }
    
    return render(request, 'stock/price.html', context)


# def save_pricing(request):
#     if request.session.get("role") not in ["admin", "store_manager"]:
#         return redirect("login")
    
    
#     if cost_price <= 0:
#             messages.error(request, "Cost price must be greater than zero.")
#             # Redirect back to the price form, preserving product name
#             return redirect(f"{reverse('price')}?product_name={product_name}")
    
#     """Save pricing data and redirect back to stock registration""" 
    
#     if request.method == 'POST':
#         product_name = request.POST.get('product_name')
#         cost_price = request.POST.get('cost_price')
        
#         wholesaler_rate = request.POST.get('wholesaler_rate', '0')
#         retailer_rate = request.POST.get('retailer_rate', '0')
#         normal_rate = request.POST.get('normal_rate', '0')
        
#         try:
#             cost_price = int(cost_price) if cost_price else 0
#             wholesaler_rate = int(wholesaler_rate) if wholesaler_rate else 0
#             retailer_rate = int(retailer_rate) if retailer_rate else 0
#             normal_rate = int(normal_rate) if normal_rate else 0
#         except (ValueError, TypeError):
#             return redirect('stock_reg')
#         # the rate logic flow
#         wholesaler_price = cost_price + (cost_price * wholesaler_rate // 100)
#         retailer_price = cost_price + (cost_price * retailer_rate // 100)
#         normal_price = cost_price + (cost_price * normal_rate // 100)
        
#         product = Product.objects.filter(product_name=product_name).first()
#         if not product:
#             product = Product.objects.create(#here we are creating the product in the product table if it does not exist when we are saving the pricing data, this
#                 # is because we want to make sure that every product that has pricing data also has a corresponding product record in the product table, this is important 
#                 # for data integrity and also for the functionality of the app, for example when we want to add stock for a product we need to have a product record to link 
#                 # the stock to, so we create the product record here if it does not exist when we are saving the pricing data.
#                 product_name=product_name,
#                 unit_cost=cost_price,
#                 current_stock=0,
#                 threshold=10
#             )
#         else:
#             product.unit_cost = cost_price
#             product.save()

#         pricing, created = ProductPricing.objects.update_or_create(#here we are saving this data in the save pricing table
#             product_name=product_name,
#             defaults={
#                 'product': product,
#                 'wholesaler_rate': wholesaler_rate,
#                 'wholesaler_price': wholesaler_price,
#                 'retailer_rate': retailer_rate,
#                 'retailer_price': retailer_price,
#                 'normal_rate': normal_rate,
#                 'normal_price': normal_price,
#             }
#         )
# # this is the part where the prices and rates in the pricing form are passed back into the stock reg form using the session. we are storing 
# # the prices and rates in the session so that we can access them in the stock registration view and pre-fill the hidden fields in the stock registration form with
# #  those values, this is because we want to make it easy for the user to add stock for a product they just set prices for without having to re-enter the prices and rates,         request.session['temp_wholesale_rate'] = wholesaler_rate
#         request.session['temp_wholesale_price'] = wholesaler_price
#         request.session['temp_retail_rate'] = retailer_rate
#         request.session['temp_retail_price'] = retailer_price
#         request.session['temp_normal_rate'] = normal_rate
#         request.session['temp_normal_price'] = normal_price
        
#         messages.success(request, f'Prices for {product_name} saved successfully!')
#         return redirect('stock_reg')
    
#     return redirect('price')

def save_pricing(request):
    if request.session.get("role") not in ["admin", "store_manager"]:
        return redirect("login")
    
    """Save pricing data and redirect back to stock registration""" 
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        cost_price = request.POST.get('cost_price')
        
        wholesaler_rate = request.POST.get('wholesaler_rate', '0')
        retailer_rate = request.POST.get('retailer_rate', '0')
        normal_rate = request.POST.get('normal_rate', '0')
        
        try:
            cost_price = int(cost_price) if cost_price else 0
            wholesaler_rate = int(wholesaler_rate) if wholesaler_rate else 0
            retailer_rate = int(retailer_rate) if retailer_rate else 0
            normal_rate = int(normal_rate) if normal_rate else 0
        except (ValueError, TypeError):
            return redirect('stock_reg')
        
        # VALIDATION MOVED HERE – after cost_price is converted
        if cost_price <= 0:
            messages.error(request, "Cost price must be greater than zero.")
            # Redirect back to the price form, preserving product name
            return redirect(f"{reverse('price')}?product_name={product_name}")
        
        # the rate logic flow
        wholesaler_price = cost_price + (cost_price * wholesaler_rate // 100)
        retailer_price = cost_price + (cost_price * retailer_rate // 100)
        normal_price = cost_price + (cost_price * normal_rate // 100)
        
        product = Product.objects.filter(product_name=product_name).first()
        if not product:
            product = Product.objects.create(#here we are creating the product in the product table if it does not exist when we are saving the pricing data, this
                # is because we want to make sure that every product that has pricing data also has a corresponding product record in the product table, this is important 
                # for data integrity and also for the functionality of the app, for example when we want to add stock for a product we need to have a product record to link 
                # the stock to, so we create the product record here if it does not exist when we are saving the pricing data.
                product_name=product_name,
                unit_cost=cost_price,
                current_stock=0,
                threshold=10
            )
        else:
            product.unit_cost = cost_price
            product.save()

        pricing, created = ProductPricing.objects.update_or_create(#here we are saving this data in the save pricing table
            product_name=product_name,
            defaults={
                'product': product,
                'wholesaler_rate': wholesaler_rate,
                'wholesaler_price': wholesaler_price,
                'retailer_rate': retailer_rate,
                'retailer_price': retailer_price,
                'normal_rate': normal_rate,
                'normal_price': normal_price,
            }
        )
        # this is the part where the prices and rates in the pricing form are passed back into the stock reg form using the session. we are storing 
        # the prices and rates in the session so that we can access them in the stock registration view and pre-fill the hidden fields in the stock registration form with
        # those values, this is because we want to make it easy for the user to add stock for a product they just set prices for without having to re-enter the prices and rates,
        request.session['temp_wholesale_rate'] = wholesaler_rate
        request.session['temp_wholesale_price'] = wholesaler_price
        request.session['temp_retail_rate'] = retailer_rate
        request.session['temp_retail_price'] = retailer_price
        request.session['temp_normal_rate'] = normal_rate
        request.session['temp_normal_price'] = normal_price
        
        messages.success(request, f'Prices for {product_name} saved successfully!')
        return redirect('stock_reg')
    
    return redirect('price')

def pricing_table(request):
    if request.session.get("role") not in ["admin", "store_manager", "sales_attendant"]:
        return redirect("login")
    all_pricing = ProductPricing.objects.all().order_by('-id')

    enriched = []

    for item in all_pricing:
        product = Product.objects.filter(product_name=item.product_name).first()

        enriched.append({
            "id": item.id,
            "product_id": product.id if product else None,
            "product_name": item.product_name,
            "unit_price": product.unit_cost if product else 0,

            "wholesaler_rate": item.wholesaler_rate,
            "wholesaler_price": item.wholesaler_price,
            "retailer_rate": item.retailer_rate,
            "retailer_price": item.retailer_price,
            "normal_rate": item.normal_rate,
            "normal_price": item.normal_price,
        })

    return render(request, 'stock/pricing_table.html', {
        'pricing_list': enriched
    })
def edit_price(request, pricing_id):
    pricing = get_object_or_404(ProductPricing, id=pricing_id)

    if request.method == 'POST':
        wholesaler_rate = request.POST.get('wholesaler_rate', '0')
        retailer_rate = request.POST.get('retailer_rate', '0')
        normal_rate = request.POST.get('normal_rate', '0')
        cost_price = request.POST.get('cost_price', '0')

        try:
            cost_price = int(cost_price)
            wholesaler_rate = int(wholesaler_rate)
            retailer_rate = int(retailer_rate)
            normal_rate = int(normal_rate)
        except (ValueError, TypeError):
            return redirect('pricing_table')

        wholesaler_price = cost_price + (cost_price * wholesaler_rate // 100)
        retailer_price = cost_price + (cost_price * retailer_rate // 100)
        normal_price = cost_price + (cost_price * normal_rate // 100)

        pricing.wholesaler_rate = wholesaler_rate
        pricing.wholesaler_price = wholesaler_price
        pricing.retailer_rate = retailer_rate
        pricing.retailer_price = retailer_price
        pricing.normal_rate = normal_rate
        pricing.normal_price = normal_price
        pricing.save()

        # Also update unit cost on the Product
        product = Product.objects.filter(product_name=pricing.product_name).first()
        if product:
            product.unit_cost = cost_price
            product.save()

        messages.success(request, 'Price updated successfully!')
        return redirect('pricing_table')

    # GET — fetch current cost price
    cost_price = 0
    product = Product.objects.filter(product_name=pricing.product_name).first()
    if product:
        cost_price = product.unit_cost  # fixed: was buying_price

    return render(request, 'stock/edit_price.html', {
        'pricing': pricing,
        'cost_price': cost_price,
    })


def delete_price(request, pricing_id):
    pricing = get_object_or_404(ProductPricing, id=pricing_id)
    if request.method == 'POST':
        product_name = pricing.product_name
        pricing.delete()
        messages.success(request, f'Price record for {product_name} deleted successfully!')
    return redirect('pricing_table')

def sales_reg(request):
    if request.method == "POST":
        cashier = request.POST['cashier']
        customer_name = request.POST['customer_name']
        customer_phone = request.POST.get('phone')
        payment = request.POST['payment']
     #we use a get list because we are collecting multiple values from the form for the same field, for example we are collecting multiple product names, 
     # quantities, selling prices and distances for each item in the sale, so we use getlist to get all the values for those fields as lists, 
     # and then we can loop through those lists to process each item in the sale.   e.g [cement, iron sheets] [2, 3] [50000, 75000] [5, 8] else we would get only the last items
        product_names = request.POST.getlist('product_name')
        quantities = request.POST.getlist('quantity')
        selling_prices = request.POST.getlist('selling_price')
        distances = request.POST.getlist('distance')
        
        subtotal = 0
        max_distance = 0
        
        for i in range(len(product_names)):# i is the number of items in the sale, we are looping through the lists of product names, quantities, selling prices 
            #and distances to calculate the subtotal and the maximum distance for the transport fee calculation,
            #  we are also converting the quantities, selling prices and distances to integers to be able to do the calculations. also len(product-names) is the number of             
            #  that particular product withthat given index index i to access all four lists at the same position.the index allows us to get all information aboutthat pdt
            qty = int(quantities[i])
            price = int(selling_prices[i])
            item_total = qty * price
            subtotal += item_total
            distance = int(distances[i])
            if distance > max_distance:
                max_distance = distance
        
        if max_distance <= 10 and subtotal <= 500000:
            transport_fee = 0
        elif max_distance < 10 and subtotal >= 5000000:
            transport_fee = 0
        else:
            transport_fee = 30000
        grand_total = subtotal + transport_fee
        
        for i in range(len(product_names)):# at this point we are creating the data and saving it in the db.
            Sale.objects.create(
                cashier=cashier,
                product_name=product_names[i],
                quantity=int(quantities[i]),
                selling_price=int(selling_prices[i]),
                distance=int(distances[i]),
                total_amount=int(quantities[i]) * int(selling_prices[i]),
                payment=payment,
                customer_name=customer_name,
                customer_phone=customer_phone,
                transport_fee=transport_fee,
                grand_total=grand_total
            )
        
        for i in range(len(product_names)):# this function gets the existing pdts and does the updates incase some stock is sold
            try:# we use try except to avoid errors in case the product name in the sale does not match any product in the db, 
                #this is just a safety measure to prevent the whole sale from failing if there is a mismatch, w.
                product = Product.objects.get(product_name=product_names[i])
                product.current_stock -= int(quantities[i])
                product.save()
            except Product.DoesNotExist:
                pass
        
        return redirect('sales_page')
    
    products = Product.objects.all()
    return render(request, 'sales/sales_reg.html', {'products': products})

def sales_page(request):
    today = date.today()# this is supposed to refresh data for the current day only, so we are using the date function to get the current date and then 
    #we are filtering the sales by that date to get only today's sales,.
    all_sales = Sale.objects.all().order_by('-date')# this is supposed to get all the sales from the db and display them ont the page by the latest date
    today_sales = Sale.objects.filter(date=today)# this one fetches those sales made that day in the cards
    today_total = sum(sale.total_amount for sale in today_sales)# this is one is getting the total mount got in the today's sale by looping thru and get in sum
    
    return render(request, 'sales/sales_page.html', {
        'new_sale': all_sales,
        'today_total': today_total
    })

def sales_report(request):
    sales = Sale.objects.all().order_by('-date')
    grand_total = sum(sale.total_amount for sale in sales)
    
    return render(request, 'sales/sales_report.html', {
        'sales': sales,
        'grand_total': grand_total,
    })

def receipt(request):
    latest_sale = Sale.objects.all().order_by('-id').first()
    
    if not latest_sale:
        messages.error(request, 'No sale found')
        return redirect('receipt')
    
    grand_total = latest_sale.total_amount + latest_sale.transport_fee
    
    return render(request, 'sales/receipt.html', {
        'sale': latest_sale,
        'grand_total': grand_total

    })

@login_required
def edit_sale(request, sale_id):
    # Get the sale object or return 404 if not found
    sale = get_object_or_404(Sale, id=sale_id)
    
    if request.method == 'POST':
        # Update all fields from the POST data
        sale.product_name = request.POST.get('product_name')
        sale.quantity = request.POST.get('quantity')
        sale.selling_price = request.POST.get('selling_price')
        sale.customer_name = request.POST.get('customer_name')
        sale.payment = request.POST.get('payment')
        sale.distance = request.POST.get('distance')
        sale.transport_fee = request.POST.get('transport_fee')
        
        # Recalculate total amount (quantity * selling_price)
        # Ensure values are numeric to avoid errors
        try:
            quantity = float(sale.quantity) if sale.quantity else 0
            price = float(sale.selling_price) if sale.selling_price else 0
            sale.total_amount = quantity * price
        except (TypeError, ValueError):
            sale.total_amount = 0
        
        # Save the updated sale
        sale.save()
        
        # Add success message (optional)
        messages.success(request, f'Sale record for {sale.product_name} updated successfully!')
        
        # Redirect back to the sales list page
        return redirect('sales_page')
    
    # GET request: display the edit form with pre-filled data
    return render(request, 'sales/edit_sale_form.html', {'sale': sale})

@login_required
def delete_sale(request, sale_id):
    if request.method == 'POST':
        sale = get_object_or_404(Sale, id=sale_id)
        sale.delete()
    return redirect('sales_page')

#  CUSTOMER & DEPOSIT 

def customer_deposit(request):
    if request.method == 'POST':
        customer = Customer.objects.create(#we are saving this data being collected from the form into the db
            customer_name=request.POST.get('customer_name'),
            phone=request.POST.get('phone'),
            product_name=request.POST.get('product_name'),
            nin=request.POST.get('nin'),
            location=request.POST.get('location'),
            total_price=request.POST.get('total_price')
        )
        
        deposit = Deposit.objects.create(
            Customer_name=customer,# this is the link to the customer page
            deposit_date=request.POST.get('deposit_date'),
            expected_completion=request.POST.get('expected_completion'),
            status=request.POST.get('status'),
            deposit_amount=request.POST.get('deposit_amount')
        )
        #preparing data to go into the receipt page, we are bascially turning them into intergers.
        total_price = int(customer.total_price)
        deposit_amount = int(deposit.deposit_amount)
        remaining_balance = total_price - deposit_amount
        # it is a dictionary with one key and many values, we are storing this data in the session to be used in the receipt page, note that the keys of this dictionary are what we will use to call the values in the receipt page
        request.session['deposit_receipt'] = {#here we create a key to store the values of this dictionary, note also that this data is coming from differentt fields
            'receipt_no': deposit.id,
            'date': request.POST.get('deposit_date'),
            'customer_name': customer.customer_name,
            'phone': customer.phone,
            'product_name': customer.product_name,
            'total_price': total_price,
            'deposit_amount': deposit_amount,# these were defined before when preparing the receipt data
            'remaining_balance': remaining_balance,
            'received_by': request.POST.get('received_by', 'Admin'),
            'status': deposit.status,
            'expected_completion': request.POST.get('expected_completion'),
        }
        
        return redirect('temp_receipt')
    
    return render(request, 'account/customer_deposit.html')

def customer_page(request):
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'account/customer_page.html', {'customers': customers})

def deposit_page(request):
    deposits = Deposit.objects.all().order_by('-deposit_date')
    customers = Customer.objects.all().order_by('-id')
    
    for deposit in deposits:
        total_price = int(deposit.Customer_name.total_price) if deposit.Customer_name.total_price else 0
        deposit_amount = int(deposit.deposit_amount) if deposit.deposit_amount else 0
        deposit.remaining_balance = total_price - deposit_amount
    
    context = {
        'deposits': deposits,
        'customers': customers,
    }
    return render(request, 'account/deposit_page.html', context)

def edit_deposit(request, deposit_id):
    deposit = get_object_or_404(Deposit, id=deposit_id)
    customer = deposit.Customer_name
    
    if request.method == 'POST':
        customer.customer_name = request.POST.get('customer_name')
        customer.phone = request.POST.get('phone')
        customer.product_name = request.POST.get('product_name')
        customer.nin = request.POST.get('nin')
        customer.location = request.POST.get('location')
        customer.total_price = request.POST.get('total_price')
        customer.save()
        
        deposit.deposit_amount = request.POST.get('deposit_amount')
        deposit.deposit_date = request.POST.get('deposit_date')
        deposit.expected_completion = request.POST.get('expected_completion')
        deposit.status = request.POST.get('status')
        deposit.save()
        
        return redirect('deposit_page')
    
    context = {
        'deposit': deposit,
        'customer': customer,
    }
    return render(request, 'account/edit_deposit.html', context)



def delete_deposit(request, deposit_id):
    deposit = get_object_or_404(Deposit, id=deposit_id)
    if request.method == 'POST':
        deposit.delete()
    return redirect('deposit_page')

def temp_receipt(request):
    deposit_data = request.session.get('deposit_receipt')
    request.session.pop('deposit_receipt', None) 
    if not deposit_data:
        return redirect('deposit_page')
    
    return render(request, 'account/temp_receipt.html', {'deposit': deposit_data})

# employee management views

def employee_table(request):
    if request.session.get("role") != "admin":
        return redirect("login")
    
    employees = Staff.objects.select_related('user').all().order_by('-id')
    return render(request, 'account/employee_table.html', {'employees': employees})

def create_staff(request):
    if request.session.get("role") != "admin":
        return redirect("login")
    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        employee_id = request.POST.get("employee_id")
        role = request.POST.get("role")
        password = request.POST.get("password")
# so after collecting this infor, we check and see, if the username exists in the table, we return an error and redirect them to the eemployee table        
        if User.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists")
            return redirect("employee_table")
 # here we are checking to see if the email also already exists       
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("employee_table")
 # here we are checking the empoyee id      
        if Staff.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already exists")
            return redirect("employee_table")
# if is a completely new record, then we create the user and the staff record in the db, note that we are creating the user first 
# because the staff record has a foreign key to the user table, so we need to have the user created first before we can create the staff record.        
        user = User.objects.create_user(# here we are creating a django authentication account for the employee, this is useful for authentication and authorization purposes, because we can use the user model to check the user's role and permissions, and also to allow the employee to log in to the system using their email and password.
            username=email,
            email=email,
            password=password, # password hashes
            first_name=name # stores the full name of the user
        )
        
        Staff.objects.create(
            user=user,# this connects to the django user model, so we can easily access the user information from the 
            # staff record, this is also useful for authentication and authorization purposes, because we can use the user model to check the user's role and permissions.
            employee_id=employee_id,
            role=role
        )
        
        messages.success(request, f"Employee {name} registered successfully!")
        return redirect("employee_table")
    
    return render(request, 'account/users.html')

def view_employee(request, id):
    employee = get_object_or_404(Staff, id=id)
    return render(request, 'account/view_employee.html', {'employee': employee})

def update_employee(request, id):
    staff = get_object_or_404(Staff, id=id)
    user = staff.user
    
    if request.method == 'POST':
        user.first_name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.username = request.POST.get('email')  # if username = email
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        user.save()
        
        staff.employee_id = request.POST.get('employee_id')
        staff.role = request.POST.get('role')
        staff.save()
        
        return redirect('employee_table')
    
    return render(request, 'account/update_employee.html', {'staff': staff})

def delete_employee(request, id):
    employee = get_object_or_404(Staff, id=id)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_table')
    return redirect('employee_table')


def get_product_price(request): # this is an ajax view that returns the price of a product based on the customer type,
    # we are using this in the sales registration form to dynamically update the price field based on the selected product and customer type, note that we are getting the product name and customer type from the url parameters,
    # # and then we are querying the ProductPricing table to get the price for that product and customer type, and then we are returning the price as a json response.


    product_name = request.GET.get('product_name')
    customer_type = request.GET.get('customer_type')
    pricing = ProductPricing.objects.filter(product_name=product_name).first()

    if customer_type == "wholesaler":
        price = pricing.wholesaler_price
    elif customer_type == "retailer":
        price = pricing.retailer_price
    else:
        price = pricing.normal_price

    return JsonResponse({"price": price})


def dashboard_redirect(request):
    role = request.session.get("role")

    if role == "admin":
        return redirect("dash")

    elif role == "store_manager":
        return redirect("stock_dash")

    elif role == "sales_attendant":
        return redirect("sales_dash")

    return redirect("login")


def view_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'account/view_customer.html', {'customer': customer})

def update_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.customer_name = request.POST.get('customer_name')
        customer.phone = request.POST.get('phone')
        customer.product_name = request.POST.get('product_name')
        customer.nin = request.POST.get('nin')
        customer.location = request.POST.get('location')
        customer.total_price = request.POST.get('total_price')
        customer.save()
        return redirect('customer_page')
    return render(request, 'account/update_customer.html', {'customer': customer})

def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_page')
    return redirect('customer_page')