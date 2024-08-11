from itertools import product
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Product,UserItem,sold,Order,mrentry,mrentryrecord,returnn,Customer,dailyreport,paybillcatogory,temppaybill,paybill,bill,mrentryrecord,supplier,Customerbalacesheet,corportepay,supplierbalancesheet,plreport
from .filters import OrderFilter,soldfilter,dailyreportfilter,expensefilter,paybillfilter,mrfilter,returnfilter,billfilter,Customerbalacesheetfilter,corportepayfilter,supplierbalanecesheetfilter,plreportfilter
from django.db.models import Count, F, Value
from django.db import connection
from core.form import soldformm, useritem,GeeksForm,mrr,returnnform,billfrom,dailyreportt,tempbilformm,mreditformm,CorportepayForm,tempform,ProductForm,CustomerForm,SupplierForm,PayBillCategoryForm,CorpoCategoryForm,PaybillForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import (get_object_or_404,
                              render,
                              HttpResponseRedirect)
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q                              
from django.db.models import Sum
from num2words import num2words
import datetime
from twilio.rest import Client 
from django.shortcuts import render
from django.views import View
from django.db.models import Avg
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import  ListView
from django.urls import reverse
from dal import autocomplete
from django.db.models import F

from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer
from rest_framework import status
import datetime
import pytz
from datetime import datetime as dt_datetime
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from datetime import timedelta

@login_required
def cart(request):
    
    a =UserItem.objects.filter(user=request.user).last()
    form = useritem(request.POST or None, request.FILES or None)
    form2 = GeeksForm(request.POST or None, request.FILES or None,instance = a)
    shopcart =UserItem.objects.filter(user=request.user)
    user_products = UserItem.objects.filter(user=request.user,groupproduct =False)
   
    total=0
    total1=0
    for gs in user_products:
        total+=gs.price1 * gs.quantity
    for gs in user_products:
        total1+=gs.price1 * gs.quantity    
      
    
    if request.method=='POST' and 'btnform1' in request.POST: 
      if form2.is_valid() :
        fs = form2.save(commit=False)
        fs.user= request.user 
    
        fs.groupproduct=False
        fs.save()
        obj = get_object_or_404(Product, id = fs.product_id)
        products = Product.objects.all().filter(groupname=obj.groupname).exclude(groupname='')
       
        for rs in products: 
          item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.subpartquantity * fs.quantity

          )

        return HttpResponseRedirect("/")
     

    # for rs in shopcart:
    #     product = Product.objects.get(id=rs.product_id)
    #     if product.quantity < rs.quantity and rs.credit =='noncredit':
    #                 outstock=0   


    dhaka_timezone = pytz.timezone('Asia/Dhaka')

# Get the current time in the Asia/Dhaka timezone
    current_time_dhaka = datetime.datetime.now(dhaka_timezone)

# Define the desired format
    date_time_format = "%d%m%y-%I%M"

# Format and print the current date and time in Asia/Dhaka timezone
    formatted_date_time = current_time_dhaka.strftime(date_time_format)


    if request.method=='POST' and 'btnform2' in request.POST and shopcart.exists(): 
     if form.is_valid() :



        for rs in shopcart: 
           product = Product.objects.get(id=rs.product_id)
           if int(rs.quantity) > int(product.quantity) :
              messages.error(request, 'Do not have group product quanitity that quantity')
              return redirect('cart') 
        fs= form.save(commit=False)
        fs.user= request.user
        fs.totalprice=total-fs.discount
        fs.totalprice1=total1-fs.discount
        fs.due=total-(fs.paid+fs.discount)
     
        formatted_date_time = fs.datetime.strftime(date_time_format)
        
        # Assign the formatted date time to the invoice number
        fs.invoicenumber = formatted_date_time
        
        
        fs.save()
        if fs.customer !=None:
          cus =Customer.objects.filter(id=fs.customer_id).first()
          cus.balance +=fs.due
        
          cus.save()   
          cus =Customer.objects.filter(id=fs.customer_id).first()     
          item, created =Customerbalacesheet.objects.get_or_create(
            datetime=fs.datetime,
            order_id=fs.id,
            customer=cus,
            balance=cus.balance,
            duebalanceadd =fs.due
        )
          

        
        obj = dailyreport.objects.all().last()
        item, created =dailyreport.objects.get_or_create(
            order_id=fs.id,
            datetime=fs.datetime,
            ammount=obj.ammount+fs.paid,
            petteyCash=obj.petteyCash,
            reporttype='INVOICE'
            
        )



        after_report =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime').first()


        if after_report : 
                    #insert_position = after_report.id
                    print(1)
                    
                    

                    try:
                        # Get the last object
                        last_report = dailyreport.objects.latest('id')
                        previous_report =dailyreport.objects.filter(datetime__lt=fs.datetime).order_by('-datetime').first()
                        print(previous_report)
                        print(last_report)
                        last_report.ammount= previous_report.ammount + last_report.order.paid
                        last_report.save()

                        daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                    # daily report ammount update
                        for i in  daily_reports_after_id:
                            i.ammount = i.ammount + last_report.order.paid
                            i.save()

                        
                        
                    except ObjectDoesNotExist:
                        # Handle the case where there are no objects in the database
                        print("No objects found in the database.")
                        last_report = None    

       

        for rs in shopcart:
                detail = sold()
                detail.customer    = fs.customer
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.order_id     = fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.remarks =rs.remarks
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct
                detail.datetime=fs.datetime
                
                shopcart.delete()    
                user_products.delete()
                product = Product.objects.get(id=rs.product_id)
                product.quantity -= rs.quantity
                detail.exchange_ammount=rs.exchange_ammount
                detail.costprice=product.price

                item, created =plreport.objects.get_or_create(
                     product_id=rs.product_id,
                     order_id=fs.id,
                     datetime=fs.datetime,
                     costprice= product.price,
                     price1=rs.price1,
                     price2=rs.price2,
                     reporttype="invoice",
                     stockquantity=product.quantity,
                     changequanitity = rs.quantity,
                     user=request.user,
                    )
                detail.save()
                product.save()


                
                

                
        
          
            
        return HttpResponseRedirect("/soldlist")

      
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    mother = request.GET.get('mother', '')

    if category and search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif category and search:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category)
        )
    elif category and mother:
        products = Product.objects.filter(
            Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(mother=mother)
        )
    elif category:
        products = Product.objects.filter(Q(productcatagory__icontains=category))
    elif search:
        products = Product.objects.filter(Q(name__icontains=search))
    elif mother:
        products = Product.objects.filter(Q(mother=mother))
    else:
        products = Product.objects.all()

  
    #products = Product.objects.filter(Q(productcatagory__icontains=category))
  

    
    
    # myFilter = OrderFilter(request.GET, queryset=products)
    # products = myFilter.qs 

    # p = Paginator(products, 5)  # creating a paginator object
    # # getting the desired page number from url
    # page_number = request.GET.get('page')
    # try:
    #     page_obj = p.get_page(page_number)  # returns the desired page object
    # except PageNotAnInteger:
    #     # if page_number is not an integer then assign the first page
    #     page_obj = p.page(1)
    # except EmptyPage:
    #     # if page is empty then return last page
    #     page_obj = p.page(p.num_pages)

    
    
    # products=page_obj  
    
    paginator = Paginator(products, 12) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    pro = paginator.get_page(page_number)

    category=  Product.objects.values('productcatagory').distinct().order_by('productcatagory')
   
    
    context = {'category':category,'products': products,'form':form,'user_products':user_products,'pro':pro,'total':total,'form2':form2}
    return render(request, 'core/cart.html', context)






@login_required
def productreport(request):
    
    a =UserItem.objects.filter(user=request.user).last()
    form = useritem(request.POST or None, request.FILES or None)
    form2 = GeeksForm(request.POST or None, request.FILES or None,instance = a)
    shopcart =UserItem.objects.filter(user=request.user)
    user_products = UserItem.objects.filter(user=request.user,groupproduct =False)
   
    total=0
    total1=0
    for gs in user_products:
        total+=gs.price1 * gs.quantity
    for gs in user_products:
        total1+=gs.price1 * gs.quantity    
      
    
    if request.method=='POST' and 'btnform1' in request.POST: 
      if form2.is_valid() :
        fs = form2.save(commit=False)
        fs.user= request.user 
    
        fs.groupproduct=False
        fs.save()
        obj = get_object_or_404(Product, id = fs.product_id)
        products = Product.objects.all().filter(groupname=obj.groupname).exclude(groupname='')
       
        for rs in products: 
          item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.subpartquantity * fs.quantity

          )

        return HttpResponseRedirect("/")
     

    # for rs in shopcart:
    #     product = Product.objects.get(id=rs.product_id)
    #     if product.quantity < rs.quantity and rs.credit =='noncredit':
    #                 outstock=0   


    dhaka_timezone = pytz.timezone('Asia/Dhaka')

# Get the current time in the Asia/Dhaka timezone
    current_time_dhaka = datetime.datetime.now(dhaka_timezone)

# Define the desired format
    date_time_format = "%d%m%y-%I%M"

# Format and print the current date and time in Asia/Dhaka timezone
    formatted_date_time = current_time_dhaka.strftime(date_time_format)


    if request.method=='POST' and 'btnform2' in request.POST and shopcart.exists(): 
     if form.is_valid() :



        for rs in shopcart: 
           product = Product.objects.get(id=rs.product_id)
           if int(rs.quantity) > int(product.quantity) :
              messages.error(request, 'Do not have group product quanitity that quantity')
              return redirect('cart') 
        fs= form.save(commit=False)
        fs.user= request.user
        fs.totalprice=total-fs.discount
        fs.totalprice1=total1-fs.discount
        fs.due=total-(fs.paid+fs.discount)
     
        fs.invoicenumber = formatted_date_time 

        
        fs.save()
        if fs.customer !=None:
          cus =Customer.objects.filter(id=fs.customer_id).first()
          cus.balance +=fs.due
        
          cus.save()   
          cus =Customer.objects.filter(id=fs.customer_id).first()     
          item, created =Customerbalacesheet.objects.get_or_create(
            datetime=fs.datetime,
            order_id=fs.id,
            customer=cus,
            balance=cus.balance,
            duebalanceadd =fs.due
        )
          

        
        obj = dailyreport.objects.all().last()
        item, created =dailyreport.objects.get_or_create(
            order_id=fs.id,
            datetime=fs.datetime,
            ammount=obj.ammount+fs.paid,
            petteyCash=obj.petteyCash,
            reporttype='INVOICE'
            
        )



        after_report =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime').first()


        if after_report : 
                    #insert_position = after_report.id
                    print(1)
                    
                    

                    try:
                        # Get the last object
                        last_report = dailyreport.objects.latest('id')
                        previous_report =dailyreport.objects.filter(datetime__lt=fs.datetime).order_by('-datetime').first()
                        print(previous_report)
                        print(last_report)
                        last_report.ammount= previous_report.ammount + last_report.order.paid
                        last_report.save()

                        daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                    # daily report ammount update
                        for i in  daily_reports_after_id:
                            i.ammount = i.ammount + last_report.order.paid
                            i.save()

                        
                        
                    except ObjectDoesNotExist:
                        # Handle the case where there are no objects in the database
                        print("No objects found in the database.")
                        last_report = None    

       

        for rs in shopcart:
                detail = sold()
                detail.customer    = fs.customer
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.order_id     = fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.remarks =rs.remarks
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct
                
                
                shopcart.delete()    
                user_products.delete()
                product = Product.objects.get(id=rs.product_id)
                product.quantity -= rs.quantity
                detail.exchange_ammount=rs.exchange_ammount
                detail.costprice=product.price

                item, created =plreport.objects.get_or_create(
                     product_id=rs.product_id,
                     order_id=fs.id,
                     datetime=fs.datetime,
                     costprice= product.price,
                     price1=rs.price1,
                     price2=rs.price2,
                     reporttype="invoice",
                     stockquantity=product.quantity,
                     changequanitity = rs.quantity,
                     user=request.user,
                    )
                detail.save()
                product.save()


                
                

                
        
          
            
        return HttpResponseRedirect("/soldlist")

      
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    mother = request.GET.get('mother', '')

    if category and search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif category and search:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category)
        )
    elif category and mother:
        products = Product.objects.filter(
            Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(mother=mother)
        )
    elif category:
        products = Product.objects.filter(Q(productcatagory__icontains=category))
    elif search:
        products = Product.objects.filter(Q(name__icontains=search))
    elif mother:
        products = Product.objects.filter(Q(mother=mother))
    else:
        products = Product.objects.all()

  
    #products = Product.objects.filter(Q(productcatagory__icontains=category))
  

    
    
    # myFilter = OrderFilter(request.GET, queryset=products)
    # products = myFilter.qs 

    # p = Paginator(products, 5)  # creating a paginator object
    # # getting the desired page number from url
    # page_number = request.GET.get('page')
    # try:
    #     page_obj = p.get_page(page_number)  # returns the desired page object
    # except PageNotAnInteger:
    #     # if page_number is not an integer then assign the first page
    #     page_obj = p.page(1)
    # except EmptyPage:
    #     # if page is empty then return last page
    #     page_obj = p.page(p.num_pages)

    
    
    # products=page_obj  
    
    paginator = Paginator(products, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    pro = paginator.get_page(page_number)

    category=  Product.objects.values('productcatagory').distinct()
    
    context = {'category':category,'products': products,'form':form,'user_products':user_products,'pro':pro,'total':total,'form2':form2}
    return render(request, 'core/productreport.html', context)







@login_required
def soldlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        orders = Order.objects.all().order_by('-datetime')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = soldfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs


        

# Orders without customers  
        orders_without_customers = Order.objects.filter(customer__isnull=True)
        without_customers = orders_without_customers.aggregate(Sum('due'))['due__sum'] or 0

        

        with_customers = Customer.objects.all()
        with_customers =  with_customers.aggregate(Sum('balance'))['balance__sum'] or 0
        # Pagination
        paginator = Paginator(filtered_orders, 10)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,
            'without_customers' :  without_customers ,
            'with_customers' :  with_customers ,
              # Pass the filter for the template
        }

        
       


        return render(request, 'core/soldlist.html',context)







@login_required
def plreportlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        orders = plreport.objects.all().order_by('-datetime')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = plreportfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/plreport.html',context)





@login_required
def customerbalancesheetlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        orders = Customerbalacesheet.objects.all().order_by('-datetime')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = Customerbalacesheetfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/cusblsheet.html',context)







@login_required
def supplierbalancesheetlist(request):
      

        orders = supplierbalancesheet.objects.all().order_by('datetime')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = supplierbalanecesheetfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/supblsheet.html',context)





@login_required
def returnlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         returns=returnn.objects.all().order_by('datetime')
         myFilter =returnfilter(request.GET, queryset=returns)
         returns = myFilter.qs 


         paginator = Paginator(returns, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         returns= paginator.get_page(page_number)
        
         context = {#'category': category,
               'returns': returns,
               'myFilter':myFilter
               }


         return render(request, 'core/returnlist.html',context)




@login_required
def bill_list(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         returns=bill.objects.all().order_by('-datetime')
         myFilter =billfilter(request.GET, queryset=returns)
         returns = myFilter.qs 


         paginator = Paginator(returns, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         returns= paginator.get_page(page_number)
        
         context = {#'category': category,
               'returns': returns,
               'myFilter':myFilter
               }


         return render(request, 'core/bill_list.html',context)






@login_required
def supplierbill_list(request):
    #   cursor = connection['db.sqlite3'].cursor()
    #   user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
    #   cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
    #   with connection.cursor() as cursor:
    #    cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
    #     cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
    #     cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
    #     row = cursor.fetchone()

         returns=corportepay.objects.all().order_by('-id')
         myFilter =corportepayfilter(request.GET, queryset=returns)
         returns = myFilter.qs 


         paginator = Paginator(returns, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         returns= paginator.get_page(page_number)
        
         context = {#'category': category,
               'returns': returns,
               'myFilter':myFilter
               }


         return render(request, 'core/bill_list.html',context)


def mrlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=mrentry.objects.all().order_by('-id')
         #myFilter =soldfilter(request.GET, queryset=orders)
         #orders = myFilter.qs 
        
         context = {#'category': category,
               'orders': orders,
               #'myFilter':myFilter
               }


         return render(request, 'core/mrlist.html',context)
				  
def update_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct = False
        )
    shopcart =UserItem.objects.filter(user=request.user,product_id=id).first()
    obj = get_object_or_404(Product, id = id)
    products = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
   
    
    

    
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
        fs.save()
        if fs.enginecomplete =="complete":
            products.quantity = products.quantity-1
            products.save()
        return HttpResponseRedirect("/")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)



def addproduct(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct = False
        )

    #obj = get_object_or_404(Product, id = id,mother=True)
   

      
    
   
    
    return HttpResponseRedirect("/") 

  

def addproductgroup(request,id):
    # dictionary for initial data with
    # field names as keys
    

    #obj = get_object_or_404(Product, id = id,mother=True)
    obj = get_object_or_404(Product, id = id)
    products = Product.objects.all().filter(groupname=obj.groupname)
    for rs in products: 
        item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.quantity

        )

      
    
   
    
    return HttpResponseRedirect("/") 



def expenseform(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = temppaybill.objects.get_or_create(
            user_id=request.user.id,
            paybillcatogory_id=id,
           
        )
    shopcart =temppaybill.objects.filter(user=request.user,paybillcatogory_id=id).first()
    # obj = get_object_or_404(Product, id = id)
   
   
    
    

    
    # pass the object as instance in form
    form = tempbilformm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
        fs.save()
        
        return HttpResponseRedirect("/expense")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)





def groupupdate_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct=True
        )
    shopcart =UserItem.objects.filter(user=request.user,product_id=id).first()

    obj = get_object_or_404(Product, id = id)
    products = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
    
    mother =UserItem.objects.filter(user=request.user,product_id=products.id).first()


   
   

    
    
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
       
        
        
        fs.save()
        
        if fs.enginecomplete =="complete":
            products.quantity = products.quantity-1
        products.save()


        product = Product.objects.get(pk=id)
    
    # Get the group name of the selected product
        group_name = product.groupname
    
    # Filter products from the same group where mother is equal to 1
        mother_products = Product.objects.filter(groupname=group_name, mother=True)
    
    # Assuming there's only one mother product, you can get its ID
        if mother_products.exists():
            mother_product_id = mother_products.first().id
            # Redirect to the 'group' URL with mother product ID in the URL
            return HttpResponseRedirect(f"/{mother_product_id}/group")
        else:
        # If there's no mother product, simply redirect to the 'group' URL without including the ID parameter.
           return HttpResponseRedirect(f"/{id}/group")
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)    



def mrupdate_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
        )
    shopcart =UserItem.objects.filter(user=request.user,product_id=id).first()
    
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/mr")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)


def ggroup(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
 
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = obj)
   
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        
        return HttpResponseRedirect("/")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)	




@login_required
def group(request,id):
    form = useritem(request.POST or None, request.FILES or None)
    #shopcart =UserItem.objects.filter(user=request.user)
    obj = get_object_or_404(Product, id = id)
    user_products = UserItem.objects.filter(user=request.user, product__groupname=obj.groupname)
    user_products = user_products.exclude(product_id=obj.id)
    if form.is_valid():
        fs= form.save(commit=False)
        fs.user= request.user
        fs.save()
        

        # for rs in shopcart:
        #         detail = sold()
        #         detail.customer    = fs.customer # Order Id
        #         detail.product_id  = rs.product_id
        #         detail.user  = request.user
        #         detail.quantity  = rs.quantity
        #         detail.added  = rs.added
        #         detail.left = fs.left
        #         detail.discount = fs.discount
        #         detail.save()
        #         product = Product.objects.get(id=rs.product_id)
        #         if rs.credit =='noncredit':    
        #              product.quantity -= rs.quantity
        #              product.save()

     
    total=0
    for rs in user_products:
            total+=rs.product.price * rs.quantity


    total1=0
    for rs in user_products:
            total1+=rs.price1 * rs.quantity        
        
    
    #shopcart =UserItem.objects.filter(user=request.user,product=obj.product)
    products = Product.objects.filter(groupname=obj.groupname).exclude(id=id)
    
    
    
	  
    context = {'products': products, 'user_products': user_products, 'total': total,'total1': total1}
    return render(request, 'core/group.html', context)



@login_required
def cashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False).exclude(quantity=0)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         text= text.replace(',', '')
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/cashmemo1.html',context)








@login_required
def cashmemo1(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False).exclude(quantity=0)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price2 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         text= text.replace(',', '')
         due=total- date.paid

         if date.paid - date.totalprice ==0 :
             due = 0
             date.paid= total1
           
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
                'due' :due
               }


         return render(request, 'core/cashmemo2.html',context)






@login_required
def bothcashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False).exclude(quantity=0)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         text= text.replace(',', '')
         due=total- date.paid

         if date.paid - date.totalprice ==0 :
             due = 0
             date.paid= total1
           
         #total = sum(product.total_price for product in self.user_products)
         total2=0
         for rs in orders:
            total2+=rs.price2 * rs.quantity

         total3=total2-date.discount
         text2=num2words(total3) 
         text2= text.replace(',', '')
         due2=total2- date.paid

         if date.paid - date.totalprice ==0 :
             due2 = 0
             date.paid= total1    
           
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               
               'text': text,
               'date': date,
               'ordere_de': ordere_de,
               'total':total,
               'total1':total1,
               'due' :due,


                'total2':total2,
               'total3':total3,
                'due2' :due2,
                'text2' : text2,



               }


         return render(request, 'core/bothcashmemo.html',context)





@login_required
def billreport(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         bills=bill.objects.all().filter(id=id).last()


         text=num2words(bills.ammount)   
         text= text.replace(',', '')
         

 
           
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'bills': bills,
               'text' :text,
               
               }


         return render(request, 'core/billreport.html',context)


@login_required
def chalan(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price2 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/chalan.html',context)    

@login_required
def mrcashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=mrentryrecord.objects.all().filter(mrentry_id=id,groupproduct =False)
         ordere_de=mrentry.objects.all().filter(id=id)
         date=mrentry.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/mrcashmemo.html',context)


@login_required
def mreditcashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        #  orders=sold.objects.all().filter(order_id=id)
        #  ordere_de=Order.objects.all().filter(id=id)
        #  date=sold.objects.all().filter(order_id=id).last()

         orders=mrentryrecord.objects.all().filter(mrentry_id=id)
         ordere_de=mrentry.objects.all().filter(id=id)
         date=mrentry.objects.all().filter(id=id).last()

         total=0
        #  for rs in orders:
        #     total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         products = Product.objects.all()
   
    
         myFilter = OrderFilter(request.GET, queryset=products)
         products = myFilter.qs 
         orderr =mrentry.objects.get(id=id)

         form = mrr(request.POST or None, request.FILES or None, instance = orderr)
         shopcart =UserItem.objects.filter(user=request.user)
         user_products = UserItem.objects.filter(user=request.user)
        



         a=mrentryrecord.objects.all().filter(mrentry_id=id,groupproduct =False)
      
         for gs in  a  :
           total+=gs.price1 * gs.quantity


         old=total   

         for i in user_products:  
            total+=i.price1 * i.quantity


         total1=0
         
         for gs in user_products:
           total1+=gs.price1 * gs.quantity   

         daily =dailyreport.objects.get(mrentry_id=id)
         paginator = Paginator(products, 20) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         pro = paginator.get_page(page_number) 

         if orderr.supplier:
           oldid= orderr.supplier.id

         if form.is_valid():
           fs= form.save(commit=False)
           fs.user= request.user
           
           fs.invoice_id=fs.datetime
           fs.totalprice=total-fs.discount
           fs.totalprice1=total1-fs.discount
           fs.due=total-(fs.paid+fs.discount)
           fs.invoice_id=fs.added


           daily.ammount = (daily.ammount+daily.mrentry.paid) - fs.paid
           daily.save()
           fs.save()  
            
           daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                # daily report ammount update
           for i in  daily_reports_after_id:
                i.ammount = i.ammount - daily.mrentry.paid
                i.save()
           for i in  daily_reports_after_id:
                i.ammount = i.ammount + fs.paid  
                i.save()
        
          
           for rs in shopcart:
                detail = mrentryrecord()
                detail.supplier    = fs.supplier
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.mrentry_id     =fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.left = fs.left
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct
                detail.datetime=fs.datetime
                detail.save()
                
                shopcart.delete()    
                product = Product.objects.get(id=rs.product_id)

                if rs.credit == 'noncredit':
                    # Increment the product's quantity
                    product.quantity += rs.quantity
                    
                    # Filter items in the shopping cart that match the product ID
                    matching_items = shopcart.filter(product_id=rs.product_id)
                    
                    if matching_items.exists():
                        # Calculate the average price of matching items
                        avg_price = matching_items.aggregate(Avg('price1'))['price1__avg']
                    else:
                        # If there are no matching items, use rs.price1
                        avg_price = rs.price1
                    
                    # Set the product's price to the calculated average if avg_price is not 0
                    if avg_price != 0:
                        product.price = avg_price
                    
                    # Save the updated product
                    product.save()


                item, created =plreport.objects.get_or_create(
                     product_id=rs.product_id,
                     mrentry_id=fs.id,
                     datetime=fs.datetime,
                     costprice= product.price,
                     price1=rs.price1,
                     price2=rs.price2,
                     reporttype="MR INVOICE ADD",
                     stockquantity=product.quantity,
                     changequanitity = rs.quantity,
                     user=request.user,
                    )     


           if fs.supplier:
                if fs.supplier.id != oldid :
                    print("Updating customer balance...")  # Informative print statement

            # Update customer balance if customer changed for the order
                    cus =supplier.objects.filter(id=oldid).first()
                    cus.balance -=fs.due
            
                    cus.save()

                    order_creation_date = orderr.datetime

            # Efficiently update related CustomerBalanceSheet objects
                    supplierbalancesheet.objects.filter(
                        datetime__gte=order_creation_date, supplier=orderr.supplier
                    ).update(balance=F('balance') - orderr.due)
                    
                   
                    
                      # F() expression for in-place update

            # Delete existing CustomerBalanceSheet objects associated with the previous order
                    supplierbalancesheet.objects.filter(mrentry=orderr).delete()


                    cus =supplier.objects.filter(id=fs.supplier_id).first()
                    cus.balance +=fs.due
            
                    cus.save()        
                    item, created =supplierbalancesheet.objects.get_or_create(
                        datetime=fs.datetime,
                        mrentry_id=fs.id,
                        supplier=cus,
                        balance=cus.balance,
                        duebalanceadd =fs.due
                    )

                    

                else:
            # Handle the case where the customer remains the same (optional logic)
                    print("Customer did not change for the order.")
       
        # Complete form saving after all checks and updates
    # Save the form data to create the model instance
                    if fs.supplier:
                        cus =supplier.objects.filter(id=daily.mrentry.supplier_id).first()

                        olddue=old - daily.mrentry.paid
                        newdue=total - fs.paid
                    

        # Update the customer's balance
                    
                        cus.balance = (cus.balance - olddue) +newdue

            # Save the updated customer object
                        cus.save()

                        order_creation_date = orderr.datetime
                        balance_sheets = supplierbalancesheet.objects.filter(datetime__gte=order_creation_date, supplier=fs.supplier) 
                        
                        for i in balance_sheets:
                            
                            # if(newdue-olddue)>0 :
                            #     i.balance = i.balance - (newdue-olddue)
                            #     i.save()
                            # else :
                                
                                i.balance = (i.balance-olddue)+newdue
                                i.save()     

         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               'products': products,
               'myFilter':myFilter,
               'form':form,
               'user_products':user_products,
               'pro':pro

               }


         return render(request, 'core/mreditcashmemo.html',context)   






# @login_required
# def mrfianaleditcashmemo(request,id):
#     context ={}
#     shopcart =mrentryrecord.objects.get(id=id)
    

#     # pass the object as instance in form
#     form = mreditformm(request.POST or None, instance = shopcart)
#     productnew = Product.objects.get(id=shopcart.product_id)
#     qua=productnew.quantity - shopcart.quantity
#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         fs= form.save(commit=False)
#         form.save()
#         #productnew.quantity  += shopcart.quantity
        
        
#         productnew.quantity  = qua + fs.quantity
#         productnew.save()

#         item, created =plreport.objects.get_or_create(
#                      product_id=shopcart.product_id,
#                      mrentry_id=shopcart.mrentry_id,
#                      datetime=fs.datetime,
#                      costprice= fs.price1,
#                      price1=fs.price1,
#                      price2=0,
#                      reporttype="mrcashmemo edit",
#                      stockquantity=qua + fs.quantity,
#                      changequanitity = fs.quantity,
#                      user=request.user,
#                     )
       
   

        
        
 
#     # add form dictionary to context
    
#     context["form"] = form
 
#     return render(request, "core/update_view.html", context)





@login_required
def mrfianaleditcashmemo(request, id):
    context ={}
    shopcart =mrentryrecord.objects.get(id=id)
    

    # pass the object as instance in form
    form = mreditformm(request.POST or None, instance = shopcart)
    productnew = Product.objects.get(id=shopcart.product_id)
    qua=productnew.quantity - shopcart.quantity
    orders = mrentry.objects.get(id=shopcart.mrentry_id)
    omitprice1=orders.totalprice - (shopcart.price1 * shopcart.quantity)
    # omitprice2=orders.totalprice1 - (shopcart.price2 *  shopcart.quantity)
    if form.is_valid():
        fs = form.save(commit=False)

        # Check if the resulting quantity is negative
        # if qua - fs.quantity < 0:
        #     messages.error(request, 'Do not have that quantity')
        #     return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        

        # Update product quantity
        productnew.quantity = qua + fs.quantity
        productnew.price=fs.price1
      

        orders.totalprice = omitprice1 +(fs.quantity *fs.price1)
        # orders.totalprice1 = omitprice2 +(fs.quantity *fs.price2)
        orders.due = orders.totalprice -  orders.paid




        if shopcart.supplier:
            print(111111)  # Debugging step
            cus = supplier.objects.filter(id=shopcart.supplier_id).first()
            if cus:
                print(cus)  # Debugging step
                
                   
                newprice = (orders.totalprice - shopcart.price1) + fs.price1

                newdue=newprice- orders.paid
                    
                if newdue> shopcart.mrentry.due:
# Remove or comment out the print statements once you have confirmed the logic works correctly
                   

                # Update the customer's balance
                    b=(cus.balance - shopcart.mrentry.due) + newdue
                    cus.balance = b
                    cus.save()



                    # Confirm the balance was updated
                    print(f"Updated customer balance: {cus.balance}")

                    order_creation_date = shopcart.datetime
                    balance_sheets = supplierbalancesheet.objects.filter(datetime__gte=order_creation_date,  supplier=shopcart.supplier)

                    for i in balance_sheets:
                        # Update balance sheet
                        
                        c=(i.balance -shopcart.mrentry.due) + newdue
                        i.balance =c
                        i.save()

                        # Confirm the balance sheet was updated
                        print(f"Updated balance sheet for {i.id} to {i.balance}")


                else:
# Remove or comment out the print statements once you have confirmed the logic works correctly
                   

                # Update the customer's balance
                     b=(cus.balance - shopcart.mrentry.due) - newdue
                     cus.balance = b
                     cus.save()



                    # Confirm the balance was updated
                     print(f"Updated customer balance: {cus.balance}")

                     order_creation_date = shopcart.datetime
                     balance_sheets = supplierbalancesheet.objects.filter(datetime__gte=order_creation_date,  supplier=shopcart.supplier)

                     for i in balance_sheets:
                        # Update balance sheet
                        
                        c=(i.balance -shopcart.mrentry.due) - newdue
                        i.balance =c
                        i.save()

                        # Confirm the balance sheet was updated
                        print(f"Updated balance sheet for {i.id} to {i.balance}") 

                # Save the updated customer object
                

          



        item, created =plreport.objects.get_or_create(
                     product_id=shopcart.product_id,
                     mrentry_id=shopcart.mrentry_id,
                     datetime=fs.datetime,
                     costprice= fs.price1,
                     price1=fs.price1,
                     price2=0,
                     reporttype="mrcashmemo edit",
                     stockquantity=qua + fs.quantity,
                     changequanitity = fs.quantity,
                     user=request.user,
                    )
       

        productnew.save()
        orders.save()
        fs.save()

        messages.success(request, 'Form submitted successfully')

        # Redirect to the updated URL
        return redirect('editcashmemo', id=shopcart.mrentry.id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "core/update_view.html", context)








@login_required
def returnno(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id)
         ordere_de=Order.objects.all().filter(id=id)
         date=sold.objects.all().filter(order_id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/return.html',context)




def get_total(self):
        self.total = sum(product.total_price for product in self.user_products)

                                  
def productlist(request):
    return render(request, 'core/productlist.html', {
        'products': Product.objects.all(),
    })

def mrinvoicelist(request):
         orders=mrentry.objects.all().order_by('-id')
         myFilter = mrfilter(request.GET, queryset=orders)
         filtered_orders = myFilter.qs
        
        # Pagination
         paginator = Paginator(filtered_orders, 10)  # Show 5 orders per page
         page_number = request.GET.get('page')
         page_orders = paginator.get_page(page_number)

         context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }


         return render(request, 'core/mrinvoicelist.html',context)

# @login_required
# def cart(request):
    
#     a =UserItem.objects.filter(user=request.user).last()
#     form = useritem(request.POST or None, request.FILES or None)
#     form2 = GeeksForm(request.POST or None, request.FILES or None,instance = a)
#     shopcart =UserItem.objects.filter(user=request.user)
#     user_products = UserItem.objects.filter(user=request.user,groupproduct =False)
   
#     total=0
#     total1=0
#     for gs in user_products:
#         total+=gs.price1 * gs.quantity
#     for gs in user_products:
#         total1+=gs.price1 * gs.quantity    
#     outstock=1    
    
#     if request.method=='POST' and 'btnform1' in request.POST: 
#       if form2.is_valid() :
#         fs = form2.save(commit=False)
#         fs.user= request.user 
    
#         fs.groupproduct=False
#         fs.save()
#         obj = get_object_or_404(Product, id = fs.product_id)
#         products = Product.objects.all().filter(groupname=obj.groupname).exclude(groupname='')
       
#         for rs in products: 
#           item, created = UserItem.objects.get_or_create(
#             user_id=request.user.id,
#             product_id=rs.id,
#             groupproduct = True,
#             quantity=rs.subpartquantity * fs.quantity

#           )

#         return HttpResponseRedirect("/")
     

#     # for rs in shopcart:
#     #     product = Product.objects.get(id=rs.product_id)
#     #     if product.quantity < rs.quantity and rs.credit =='noncredit':
#     #                 outstock=0   
#     if request.method=='POST' and 'btnform2' in request.POST: 
#      if form.is_valid() and outstock==1:
#         fs= form.save(commit=False)
#         fs.user= request.user
#         fs.totalprice=total-fs.discount
#         fs.totalprice1=total1-fs.discount
#         fs.due=total-(fs.paid+fs.discount)
#         fs.invoice_id=fs.added

        
#         fs.save()
#         if fs.customer !=None:
#           cus =Customer.objects.filter(id=fs.customer_id).first()
#           cus.balance +=fs.due
#           cus.save()
        
#         obj = dailyreport.objects.all().last()
#         item, created =dailyreport.objects.get_or_create(
#             order_id=fs.id,
#             ammount=obj.ammount+fs.paid,
#             petteyCash=obj.petteyCash,
#             reporttype='INVOICE'
            
#         )
           
        

#         for rs in shopcart:
#                 detail = sold()
#                 detail.customer    = fs.customer
#                  # Order Id
                 
#                 detail.product_id  = rs.product_id
#                 detail.order_id     = fs.id 
#                 detail.user  = request.user
#                 detail.quantity  = rs.quantity
#                 detail.added  = rs.added
#                 detail.left = fs.left
#                 detail.discount = fs.discount
#                 detail.price1 = rs.price1
#                 detail.price2 = rs.price2
#                 detail.engine_no=rs.engine_no
#                 detail.Phone=fs.Phone
#                 detail.name=fs.name
#                 detail.remarks =rs.remarks
#                 detail.sparename =rs.sparename 
#                 detail.groupproduct = rs.groupproduct
                
                
#                 shopcart.delete()    
#                 user_products.delete()
#                 product = Product.objects.get(id=rs.product_id)
#                 product.quantity -= rs.quantity
#                 detail.exchange_ammount=rs.exchange_ammount
#                 detail.costprice=product.price
#                 detail.save()
#                 product.save()
                

                
        
          
            
#         return HttpResponseRedirect("/soldlist")

def mr(request):
    form = mrr(request.POST or None, request.FILES or None)
    shopcart =UserItem.objects.filter(user=request.user)
    user_products = UserItem.objects.filter(user=request.user,groupproduct =False)


    total=0
    for gs in user_products:
        total+=gs.price1 * gs.quantity



    if form.is_valid():
        fs= form.save(commit=False)
        fs.user= request.user
        fs.totalprice=total-fs.discount
        #fs.totalprice1=total1-fs.discount
        fs.due=total-(fs.paid+fs.discount)
        fs.invoice_id=fs.added

        
        fs.save()
        if fs.supplier !=None:
            sup =supplier.objects.filter(id=fs.supplier_id).first()
            sup.balance +=fs.due
            sup.save()


            item, created =supplierbalancesheet.objects.get_or_create(
            datetime=fs.datetime,
            mrentry_id=fs.id,
            supplier=sup,
            balance=sup.balance,
            duebalanceadd =fs.due
        )
        
        

        for rs in shopcart:
                detail =mrentryrecord()
                detail.supplier= fs.supplier
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.mrentry_id    = fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.left = fs.left
                detail.price1=rs.price1
                detail.discount = fs.discount
                detail.groupproduct = rs.groupproduct
                detail.datetime = fs.datetime
                detail.save()
                
                shopcart.delete()    
                product = Product.objects.get(id=rs.product_id)

                if rs.credit == 'noncredit':
                    # Increment the product's quantity
                    product.quantity += rs.quantity
                    pre=(product.price * product.quantity)+ (rs.price1* rs.quantity)
                    product.avg_price=add/(product.quantity+rs.quantity)
                    
                    # Filter items in the shopping cart that match the product ID
                    matching_items = shopcart.filter(product_id=rs.product_id)
                    
                    if matching_items.exists():
                        # Calculate the average price of matching items
                        avg_price = matching_items.aggregate(Avg('price1'))['price1__avg']
                    else:
                        # If there are no matching items, use rs.price1
                        avg_price = rs.price1
                    
                    # Set the product's price to the calculated average if avg_price is not 0
                    if avg_price != 0:
                        product.price = avg_price
                    
                    # Save the updated product
                    product.save()



                item, created =plreport.objects.get_or_create(
                     product_id=rs.product_id,
                     mrentry_id=fs.id,
                     datetime=fs.datetime,
                     costprice= product.price,
                     price1=rs.price1,
                     price2=rs.price2,
                     reporttype="MR INVOICE",
                     stockquantity=product.quantity,
                     changequanitity = rs.quantity,
                     user=request.user,
                    )


        obj = dailyreport.objects.all().last()
        item, created =dailyreport.objects.get_or_create(
            datetime=fs.datetime,
            mrentry_id=fs.id,
            ammount=obj.ammount-fs.paid,
            petteyCash=obj.petteyCash,
            reporttype='MR ENTRY'
            
        )        
        return HttpResponseRedirect("/mrinvoicelist")



        
    
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    mother = request.GET.get('mother', '')

    if category and search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif category and search:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category)
        )
    elif category and mother:
        products = Product.objects.filter(
            Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(mother=mother)
        )
    elif category:
        products = Product.objects.filter(Q(productcatagory__icontains=category))
    elif search:
        products = Product.objects.filter(Q(name__icontains=search))
    elif mother:
        products = Product.objects.filter(Q(mother=mother))
    else:
        products = Product.objects.all()
  
    #products = Product.objects.filter(Q(productcatagory__icontains=category))
    

  
    # myFilter = OrderFilter(request.GET, queryset=products)
    # products = myFilter.qs 

    # p = Paginator(products, 5)  # creating a paginator object
    # # getting the desired page number from url
    # page_number = request.GET.get('page')
    # try:
    #     page_obj = p.get_page(page_number)  # returns the desired page object
    # except PageNotAnInteger:
    #     # if page_number is not an integer then assign the first page
    #     page_obj = p.page(1)
    # except EmptyPage:
    #     # if page is empty then return last page
    #     page_obj = p.page(p.num_pages)

    
    
    # products=page_obj  
    
    paginator = Paginator(products, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    pro = paginator.get_page(page_number)

    category=  Product.objects.values('productcatagory').distinct()
    
    context = {'category':category,'products': products,'form':form,'user_products':user_products,'pro':pro,'total':total}
    return render(request, 'core/mr.html', context)
   
    
   

 


def returnreasonn(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    # item, created = returnn.objects.get_or_create(
    #        sold_id=id,
    #     )
    # shopcart =returnn.objects.filter(sold_id=id).first()
    
    # pass the object as instance in form
    form = returnnform(request.POST or None, instance = None)
 
    # save the data from the form and
    # redirect to detail_view
    #sold = sold.objects.get(id=id)
    solds = get_object_or_404(sold, id = id)
    product = Product.objects.get(id=solds.product_id)
    if form.is_valid():
        fs= form.save(commit=False)
        if solds.returnquantity >= solds.quantity:
            # Add an error to the form
           
            
            messages.error(request, 'Do not have that quantity available')
            return redirect('returnreasonn', id=id) 
        
        else:
            fs.customer=solds.customer
            fs.returnprice=fs.cashreturnprice + fs.duereturnprice 
            
            product.quantity += fs.quantity
            product.save()
            fs.sold=solds
            fs.save()  
            solds.returnquantity = solds.returnquantity + fs.quantity
            solds.save()
            
            item, created =plreport.objects.get_or_create(
                     product_id=solds.product_id,
                     order_id=solds.order_id,
                     datetime=fs.datetime,
                     costprice= product.price,
                     price1=solds.price1,
                     price2=solds.price2,
                     reporttype="RETUERN",
                     stockquantity=product.quantity,
                     changequanitity = fs.quantity,
                     user=request.user,
                    )


            obj = dailyreport.objects.all().last()
            if fs.status == "CASH RETURN":
                item, created =dailyreport.objects.get_or_create(
                    datetime=fs.datetime,
                    returnn_id=fs.id,
                    ammount=obj.ammount-fs.returnprice,
                    returnprice=fs.cashreturnprice ,
                    returncostprice = solds.costprice
                )


                after_report =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime').first()


                if after_report : 
                    #insert_position = after_report.id
                    print(1)
                    
                    

                    try:
                        # Get the last object
                        last_report = dailyreport.objects.latest('id')
                        previous_report =dailyreport.objects.filter(datetime__lt=fs.datetime).order_by('-datetime').first()
                        print(previous_report)
                        print(last_report)
                        last_report.ammount= previous_report.ammount + last_report.returnn.cashreturnprice
                        last_report.save()

                        daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                    # daily report ammount update
                        for i in  daily_reports_after_id:
                            i.ammount = i.ammount + last_report.returnn.cashreturnprice
                            i.save()

                        
                        
                    except ObjectDoesNotExist:
                        # Handle the case where there are no objects in the database
                        print("No objects found in the database.")
                        last_report = None   






                messages.success(request, 'Return successfully processed!')
                return redirect('returnreasonn', id=id) 


            elif fs.status == "DUE RUTURN": 
                item, created =dailyreport.objects.get_or_create(
                    datetime=fs.datetime,
                    returnn_id=fs.id,
                    ammount=obj.ammount,
                    returnprice=fs.duereturnprice


                ) 

                solds.order.due -= fs.duereturnprice 
                solds.order.save()

                
                if solds.order.customer !=None:
                    solds.customer.balance -= fs.duereturnprice 
                    solds.customer.save()
                


                    item, created =Customerbalacesheet.objects.get_or_create(
                    datetime=fs.datetime,
                    order_id=solds.order.id,
                    customer=solds.order.customer,
                    balance=solds.customer.balance,
                    returnn_id=fs.id
                
                )  
                messages.success(request, 'Return successfully processed!')
                return redirect('returnreasonn', id=id)      


                

            else :  
                    item, created =dailyreport.objects.get_or_create(
                        datetime=fs.datetime,
                        returnn_id=fs.id,
                        ammount=obj.ammount,
                        returnprice=fs.cashreturnprice + fs.duereturnprice
                    ) 

                    solds.order.due -= fs.duereturnprice 
                    solds.order.save()


                    after_report =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime').first()


                    if after_report : 
                    #insert_position = after_report.id
                        print(1)
                        
                        

                        try:
                            # Get the last object
                            last_report = dailyreport.objects.latest('id')
                            previous_report =dailyreport.objects.filter(datetime__lt=fs.datetime).order_by('-datetime').first()
                            print(previous_report)
                            print(last_report)
                            last_report.ammount= previous_report.ammount + last_report.returnn.cashreturnprice
                            last_report.save()

                            daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                        # daily report ammount update
                            for i in  daily_reports_after_id:
                                i.ammount = i.ammount + last_report.returnn.cashreturnprice
                                i.save()

                        
                        
                        except ObjectDoesNotExist:
                            # Handle the case where there are no objects in the database
                            print("No objects found in the database.")
                            last_report = None  

                    if solds.order.customer !=None:
                        solds.customer.balance -= fs.duereturnprice 
                        solds.customer.save()
                    


                        item, created =Customerbalacesheet.objects.get_or_create(
                        datetime=fs.datetime,
                        order_id=solds.order.id,
                        customer=solds.order.customer,
                        balance=solds.customer.balance,
                        returnn_id=fs.id
                
                )  

            
                    messages.success(request, 'Return successfully processed!')
                    return redirect('returnreasonn', id=id) 
            
    # add form dictionary to context
    context = {#'category': category,
               'form': form,
               'solds': solds,
               

               }
    
   
    
    return render(request, "core/retuernform.html", context)


@login_required
def editcashmemo(request,id):
    
         orders=sold.objects.all().filter(order_id=id)
         ordere_de=Order.objects.all().filter(id=id)
         date=sold.objects.all().filter(order_id=id).last()
         total=0
        #  for rs in orders:
        #     total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         products = Product.objects.all()
   
    
         myFilter = OrderFilter(request.GET, queryset=products)
         products = myFilter.qs 
         orderr =Order.objects.get(id=id)



         daily =dailyreport.objects.get(order_id=id)

         


         form = useritem(request.POST or None, request.FILES or None, instance = orderr)

         shopcart =UserItem.objects.filter(user=request.user)
         user_products = UserItem.objects.filter(user=request.user)
         total=0
         a=sold.objects.all().filter(order_id=id)
         for gs in  a  :
           total+=gs.price1 * gs.quantity
         old=total

         for i in user_products:  
            total+=i.price1 * i.quantity

         total1=0

         for gs in  a  :
           total1+=gs.price2 * gs.quantity

         for i in user_products:  
            total1+=i.price2 * i.quantity

         
        

         paginator = Paginator(products, 20) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         pro = paginator.get_page(page_number) 
         balancecusold=0
         if orderr.customer:
           oldid= orderr.customer.id
           balancecusold= orderr.customer
         if form.is_valid():
            fs = form.save(commit=False)
            
            fs.user= request.user
           
            fs.invoice_id=fs.datetime
            fs.totalprice=total-fs.discount
            fs.totalprice1=total1-fs.discount
            fs.due=(total)-(fs.paid+fs.discount)
            fs.invoice_id=fs.added
            #current daily report paid
            daily.ammount = (daily.ammount-daily.order.paid) + fs.paid
            daily.save()
            fs.save()  
            
            daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')


            for i in  daily_reports_after_id:
                i.ammount = i.ammount + fs.paid  
                i.save()
                # daily report ammount update
            for i in  daily_reports_after_id:
                i.ammount = i.ammount - daily.order.paid
                i.save()
            
            

            for rs in shopcart:
                detail = sold()
                detail.customer    = fs.customer
                 # Order Id
                
                detail.product_id = rs.product_id
                detail.order_id     =fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
               
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct

                detail.save()
                
                shopcart.delete()    
                product = Product.objects.get(id=rs.product_id)
                   
                product.quantity -= rs.quantity
                product.save()


                item, created =plreport.objects.get_or_create(
                     product_id=rs.product_id,
                     order_id=fs.id,
                     datetime=fs.datetime,
                     costprice= product.price,
                     price1=rs.price1,
                     price2=rs.price2,
                     reporttype="invoice add",
                     stockquantity=product.quantity,
                     changequanitity = rs.quantity,
                     user=request.user,
                    )


            if fs.customer:
              if fs.customer.id != oldid :
                print("Updating customer balance...")  # Informative print statement

        # Update customer balance if customer changed for the order
                cus =Customer.objects.filter(id=oldid).first()
                cus.balance -=fs.due
        
                cus.save()

                order_creation_date = orderr.datetime

        # Efficiently update related CustomerBalanceSheet objects
                Customerbalacesheet.objects.filter(
                    datetime__gt=order_creation_date, customer=orderr.customer
                ).update(balance=F('balance') - orderr.due)  # F() expression for in-place update

        # Delete existing CustomerBalanceSheet objects associated with the previous order
                Customerbalacesheet.objects.filter(order=orderr).delete()


                cus =Customer.objects.filter(id=fs.customer_id).first()
                cus.balance +=fs.due
        
                cus.save()        
                item, created =Customerbalacesheet.objects.get_or_create(
                    datetime=fs.datetime,
                    order_id=fs.id,
                    customer=cus,
                    balance=cus.balance,
                    duebalanceadd =fs.due
                )

                

              else:
        # Handle the case where the customer remains the same (optional logic)
                print("Customer did not change for the order.")

    # Complete form saving after all checks and updates
 # Save the form data to create the model instance
                if fs.customer:
                    cus =Customer.objects.filter(id=daily.order.customer_id).first()

                    olddue=old - daily.order.paid
                    newdue=total - fs.paid
                

    # Update the customer's balance
                
                    cus.balance = (cus.balance - olddue) +newdue

        # Save the updated customer object
                    cus.save()

                    order_creation_date = orderr.datetime
                    balance_sheets = Customerbalacesheet.objects.filter(datetime__gte=order_creation_date, customer=fs.customer) 
                    
                    for i in balance_sheets:
                        
                        # if(newdue-olddue)>0 :
                        #     i.balance = i.balance - (newdue-olddue)
                        #     i.save()
                        # else :
                            
                            i.balance = (i.balance-olddue)+ (newdue)
                            i.save()


             
             


           
               
                
               
               
            messages.success(request, 'Form submitted successfully') 

         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               'products': products,
               'myFilter':myFilter,
               'form':form,
               'user_products':user_products,
               'pro':pro

               }


         return render(request, 'core/editcashmemo.html',context)    


from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def fianaleditcashmemo(request, id):
    context = {}
    shopcart = sold.objects.get(id=id)

    # pass the object as an instance in form
    form = soldformm(request.POST or None, instance=shopcart)
    productnew = Product.objects.get(id=shopcart.product_id)
    qua = productnew.quantity + shopcart.quantity
    orders = Order.objects.get(id=shopcart.order_id)
    omitprice1=orders.totalprice - (shopcart.price1 * shopcart.quantity)
    omitprice2=orders.totalprice1 - (shopcart.price2 *  shopcart.quantity)
    if form.is_valid():
        fs = form.save(commit=False)

        # Check if the resulting quantity is negative
        if qua - fs.quantity < 0:
            messages.error(request, 'Do not have that quantity')
            return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        

        # Update product quantity
        productnew.quantity = qua - fs.quantity
      

        orders.totalprice = omitprice1 +(fs.quantity *fs.price1)
        orders.totalprice1 = omitprice2 +(fs.quantity *fs.price2)
        orders.due = orders.totalprice -  orders.paid




        if shopcart.customer:
            print(111111)  # Debugging step
            cus = Customer.objects.filter(id=shopcart.customer_id).first()
            if cus:
                print(cus)  # Debugging step
                
                   
                newprice = (orders.totalprice - shopcart.price1) + fs.price1

                newdue=newprice- orders.paid
                    
                if newdue> shopcart.order.due:
# Remove or comment out the print statements once you have confirmed the logic works correctly
                   

                # Update the customer's balance
                    b=(cus.balance - shopcart.order.due) + newdue
                    cus.balance = b
                    cus.save()



                    # Confirm the balance was updated
                    print(f"Updated customer balance: {cus.balance}")

                    order_creation_date = shopcart.datetime
                    balance_sheets = Customerbalacesheet.objects.filter(datetime__gte=order_creation_date, customer=shopcart.customer)

                    for i in balance_sheets:
                        # Update balance sheet
                        
                        c=(i.balance -shopcart.order.due) + newdue
                        i.balance =c
                        i.save()

                        # Confirm the balance sheet was updated
                        print(f"Updated balance sheet for {i.id} to {i.balance}")


                elif newdue < shopcart.order.due:
# Remove or comment out the print statements once you have confirmed the logic works correctly
                   

                # Update the customer's balance
                     b=(cus.balance + shopcart.order.due) - newdue
                     cus.balance = b
                     cus.save()



                    # Confirm the balance was updated
                     print(f"Updated customer balance: {cus.balance}")

                     order_creation_date = shopcart.datetime
                     balance_sheets = Customerbalacesheet.objects.filter(datetime__gte=order_creation_date, customer=shopcart.customer)

                     for i in balance_sheets:
                        # Update balance sheet
                        
                        c=(i.balance + shopcart.order.due) - newdue
                        i.balance =c
                        i.save()

                        # Confirm the balance sheet was updated
                        print(f"Updated balance sheet for {i.id} to {i.balance}") 

                # Save the updated customer object
                

          



        item, created =plreport.objects.get_or_create(
                     product_id=shopcart.product_id,
                     order_id=shopcart.order_id,
                     datetime=fs.datetime,
                     costprice= productnew.price,
                     price1=fs.price1,
                     price2=fs.price2,
                     reporttype="cashmemo edit",
                     stockquantity=qua - fs.quantity,
                     changequanitity = fs.quantity,
                     user=request.user,
                    )

        productnew.save()
        orders.save()
        fs.save()

        messages.success(request, 'Form submitted successfully')

        # Redirect to the updated URL
        return redirect('editcashmemo', id=shopcart.order.id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "core/update_view.html", context)





@login_required
def billt(request,id):
  context ={}
  form = billfrom(request.POST or None, request.FILES or None)

  if form.is_valid():
           fs= form.save(commit=False)
           fs.order_id= id
           fs.save() 
           obj = dailyreport.objects.all().last()

           

           order = Order.objects.get(id=id)
           order.due=order.due-fs.ammount
           if order.due < 0:  # Correcting 'bellow' to 'below'
                messages.error(request, 'Error: The due amount cannot be less than zero.')
           else:
                order.save()
                
                item, created =dailyreport.objects.get_or_create(
                    reporttype="BILL",
                    datetime=fs.datetime,
                    bill_id=fs.id,
                    ammount=obj.ammount+fs.ammount
                    
                    )
           



                after_report =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime').first()


                if after_report : 
                            #insert_position = after_report.id
                            print(1)
                            
                            

                            try:
                                # Get the last object
                                last_report = dailyreport.objects.latest('id')
                                previous_report =dailyreport.objects.filter(datetime__lt=fs.datetime).order_by('-datetime').first()
                                print(previous_report)
                                print(last_report)
                                last_report.ammount= previous_report.ammount + last_report.bill.ammount
                                last_report.save()

                                daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                            # daily report ammount update
                                for i in  daily_reports_after_id:
                                    i.ammount = i.ammount + last_report.bill.ammount
                                    i.save()

                                
                                
                            except ObjectDoesNotExist:
                                # Handle the case where there are no objects in the database
                                print("No objects found in the database.")
                                last_report = None   


                messages.success(request, 'Form submission successful')                

  context["form"] = form
  return render(request, "core/update_view.html", context)



@login_required
def customerlist(request):
    user_list = Customer.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/customerlist.html', { 'users': users })
        
      
  

def search(request):

    results = []

    if request.method == "GET":

        query = request.GET.get('search')

        if query == '':

            query = 'None'

        results = Customer.objects.filter(Q(name__icontains=query)  )

    return render(request, 'core/search_results.html', {'query': query, 'users': results})
        
      

@login_required
def customersolddeatails(request):
    user_list = Customer.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 3)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/customerlist.html', { 'users': users })   






@login_required
def suplierlist(request):
    user_list = supplier.objects.all().order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 20)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/supplierlist.html', { 'users': users })




@login_required
def billcustomer(request,id):
  context ={}
  form = billfrom(request.POST or None, request.FILES or None)
  cus = Customer.objects.get(id=id)

  if form.is_valid():
           fs= form.save(commit=False)
           fs.customer_id=id
           fs.save() 
           cus.balance  -= fs.ammount
           cus.save()
           obj = dailyreport.objects.all().last()
           item, created =dailyreport.objects.get_or_create(
            datetime=fs.datetime,
            bill_id=fs.id,
            ammount=obj.ammount+fs.ammount
            
            )
           



           after_report =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime').first()


           if after_report : 
                    #insert_position = after_report.id
                    print(1)
                    
                    

                    try:
                        # Get the last object
                        last_report = dailyreport.objects.latest('id')
                        previous_report =dailyreport.objects.filter(datetime__lt=fs.datetime).order_by('-datetime').first()
                        print(previous_report)
                        print(last_report)
                        last_report.ammount= previous_report.ammount + last_report.bill.ammount
                        last_report.save()

                        daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs.datetime).order_by('datetime')
                    # daily report ammount update
                        for i in  daily_reports_after_id:
                            i.ammount = i.ammount + last_report.bill.ammount
                            i.save()

                        
                        
                    except ObjectDoesNotExist:
                        # Handle the case where there are no objects in the database
                        print("No objects found in the database.")
                        last_report = None    
           
           item, created =Customerbalacesheet.objects.get_or_create(
            datetime=fs.datetime,
            bill_id=fs.id,
            customer=cus,
            balance=cus.balance,
          
        )
           
           messages.success(request, 'Form submission successful')

  context["form"] = form
  return render(request, "core/update_view.html", context)


def dalyreport(request):

         orders=dailyreport.objects.all().order_by('datetime')
         myFilter =dailyreportfilter(request.GET, queryset=orders)
         orders = myFilter.qs 

         
        #  paginator = Paginator(orders, 15) # Show 25 contacts per page.

        #  page_number = request.GET.get('page')
        #  orders = paginator.get_page(page_number)
         cashsale=0
         duesale=0
         netsale=0
         salesreturn=0
         collection=0
         expense=0
         returnprice=0
        
         orderlist=Order.objects.all()
         mrlist=mrentry.objects.all()
         mrsale=0


         for rs in orders:
           for invoice in orderlist:
                if invoice.id == rs.order_id:
                    cashsale += invoice.paid
                    duesale += invoice.due

           for mrentri in mrlist:  
                 if mrentri.id == rs.mrentry_id:      
                    mrsale += mrentri.totalprice
           returnprice += rs.returnprice
    
           if rs.bill and rs.bill.ammount is not None:
                collection += rs.bill.ammount
           else:
                collection += 0  # Adding 0 when rs.bill.amount is None
           expense  =  expense +  rs.billexpense
        
             



          



        
         context = {#'category': category,
               'orders': orders,
               'myFilter':myFilter,
                'cashsale':cashsale,
                'duesale':duesale,
                'netsale':cashsale + duesale ,
                'mrsale' : mrsale,
                'returnprice':returnprice,
                'collection':collection,
                'expense' :expense,
               }


         return render(request, 'core/daily-report.html',context)



def dalyreportsearch(request):
    
    return render(request, "core/a.html")    

def expense(request):

         orders=dailyreport.objects.all().order_by('datetime').last()
         lastpaybill=paybill.objects.all().last()
         #myFilter =dailyreportfilter(request.GET,queryset=orders)
         user_products = temppaybill.objects.filter(user=request.user)
         form = dailyreportt(request.POST or None, request.FILES or None)
         total=0
        
         for gs in user_products:
           total+=gs.ammount 
         if request.method=='POST' and 'btnform1' in request.POST:
           
           if form.is_valid() :
           
             fs = form.save(commit=False)
             item, created =paybill.objects.get_or_create(
             datetime =fs.datetime,
             pettycashbalance=orders.petteyCash +fs.petteyCash,
             reloadpetteycash=fs.petteyCash,
             typecat="receive"
             )
             fs.billexpense = fs.petteyCash
             fs.ammount =orders.ammount -fs.petteyCash
             print(fs.petteyCash)
             fs.petteyCash =fs.petteyCash +orders.petteyCash
             fs.reporttype='FUND TRANSFER'
             
             
             fs.save()
             messages.success(request, 'FUND TRANSFERFER COMPLETE')
             return HttpResponseRedirect("/expense")
         
         form2 = CorportepayForm(request.POST or None, request.FILES or None)

         if request.method=='POST' and 'btnform2' in request.POST:
           if form2.is_valid() :
           
             fs1 = form2.save(commit=False)
            #  fs1.billexpense = fs1.petteyCash
            #  fs1.ammount =orders.ammount -fs1.petteyCash
            #  fs1.petteyCash =orders.petteyCash
            #  fs1.reporttype='CORPORATE'
             fs1.save()
             item, created = dailyreport.objects.get_or_create(
            billexpense=fs1.ammount,
            datetime = fs1.datetime,
            ammount=orders.ammount - fs1.ammount,
            petteyCash=orders.petteyCash,
            reporttype = 'CORPORATE'
             )
             if fs1.supplier : 
                supplier_id = fs1.supplier.id  #

    # Query the supplier from the Supplier model
                #supplier = supplier.objects.get(pk=supplier_id)

                supp=supplier.objects.filter(id=supplier_id).first()
                
    # Assuming there is a balance field in the Supplier model, deduct the balance
                
                supp.balance = supp.balance -fs1.ammount
                supp.save()



                item, created =supplierbalancesheet.objects.get_or_create(
           
            supplier=supp,
            balance=supp.balance,
            corportepay=fs1
        )
                

                after_report =dailyreport.objects.filter(datetime__gt=fs1.datetime).order_by('datetime').first()


                if after_report : 
                    #insert_position = after_report.id
                    print(1)
                    
                    

                    try:
                        # Get the last object
                        last_report = dailyreport.objects.latest('id')
                        previous_report =dailyreport.objects.filter(datetime__lt=fs1.datetime).order_by('-datetime').first()
                        print(previous_report)
                        print(last_report)
                        last_report.ammount= previous_report.ammount - last_report.billexpense
                        last_report.save()

                        daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs1.datetime).order_by('datetime')
                    # daily report ammount update
                        for i in  daily_reports_after_id:
                            i.ammount = i.ammount -last_report.billexpense
                            i.save()

                        
                        
                    except ObjectDoesNotExist:
                        # Handle the case where there are no objects in the database
                        print("No objects found in the database.")
                        last_report = None     



                
             messages.success(request, 'Form submitted successfully')
             return HttpResponseRedirect("/expense")

         form3 = dailyreportt(request.POST or None, request.FILES or None)

         if request.method=='POST' and 'btnform3' in request.POST:
            if form3.is_valid() :
           
             fs1 = form3.save(commit=False)
             fs1.billexpense = fs1.petteyCash
             fs1.ammount =orders.ammount -fs1.petteyCash
             fs1.petteyCash =orders.petteyCash
             
             print(fs1.id)
             fs1.save()
            
             reports = dailyreport.objects.order_by('id')


             after_report =dailyreport.objects.filter(datetime__gt=fs1.datetime).order_by('datetime').first()


             if after_report : 
                #insert_position = after_report.id
                print(1)
                
                

                try:
                    # Get the last object
                    
                    last_report = dailyreport.objects.latest('id')
                    previous_report =dailyreport.objects.filter(datetime__lt=fs1.datetime).order_by('-datetime').first()
                    print(previous_report)
                    print(last_report)
                    last_report.ammount= previous_report.ammount - last_report.billexpense
                    last_report.save()

                    daily_reports_after_id =dailyreport.objects.filter(datetime__gt=fs1.datetime).order_by('datetime')
                # daily report ammount update
                    for i in  daily_reports_after_id:
                        i.ammount = i.ammount -last_report.billexpense
                        i.save()

                    
                    
                except ObjectDoesNotExist:
                    # Handle the case where there are no objects in the database
                    print("No objects found in the database.")
                    last_report = None

               

            messages.success(request, 'Form submitted successfully')
            return HttpResponseRedirect("/expense")   
            
        #  if request.method=='POST' and 'btnform5' in request.POST:
        #     if form3.is_valid() :
           
        #      fs1 = form3.save(commit=False)
        #      fs1.billexpense = fs1.petteyCash
        #      fs1.ammount =orders.ammount -fs1.petteyCash
        #      fs1.petteyCash =orders.petteyCash
        #      fs1.reporttype='Discount'
        #      fs1.save()
        #      messages.success(request, 'Form submitted successfully')
        #      return HttpResponseRedirect("/expense")    

              

               
         







         form4 = tempform (request.POST or None, request.FILES or None)



         if request.method=='POST' and 'btnform5' in request.POST:
            if  form4.is_valid() :



               
                petteyCash_total = orders.petteyCash-total
                if petteyCash_total < 0:
                    messages.error(request, " The petty cash total is less than zero.")
                    return HttpResponseRedirect("/expense")  # replace with your actual URL for redirection
    
  


                fs1 = form4.save(commit=False)
                #myFilter =dailyreportfilter(request.GET,queryset=orders)
                user_products = temppaybill.objects.filter(user=request.user)
                
                total=0
                total1=0
                for gs in user_products:
                   total+=gs.ammount 

                item, created =dailyreport.objects.get_or_create(
                    datetime=fs1.datetime,
                    petteyCash=orders.petteyCash-total,
                    billexpense=total,
                    ammount=orders.ammount,
                    reporttype="office expense"
                    )   

                

                for rs in  user_products:
                        detail = paybill()
                        detail.paybillcatogory =rs.paybillcatogory
                        paybilllast=paybill.objects.all().last()
                        # Order Id
                        detail.pettycashbalance=paybilllast.pettycashbalance-rs.ammount
                        detail.ammount  = rs.ammount 
                        detail.remarks    = rs.remarks
                        detail.user  = request.user
                        detail.typecat="payment"
                        detail.datetime = rs.datetime 


                        if paybilllast.datetime == rs.datetime:
                            detail.datetime = rs.datetime + timedelta(minutes=1)
                        else:
                            detail.datetime = rs.datetime 
                        detail.save()

                       
                        after_report =paybill.objects.filter(datetime__gt=fs1.datetime).order_by('datetime').first()
                        

                        if after_report : 
                            #insert_position = after_report.id
                            print(1)
                            
                            

                            try:
                                # Get the last object
                                last_report = paybill.objects.latest('id')
                                previous_report =paybill.objects.filter(datetime__lte=fs1.datetime).order_by('datetime').last()
                                print(previous_report)
                                print(last_report)
                                last_report.pettycashbalance= previous_report.pettycashbalance - last_report.ammount
                                last_report.save()


                                

                                daily_reports_after_id =paybill.objects.filter(datetime__gt=fs1.datetime).order_by('datetime')
                            # daily report ammount update
                                for i in  daily_reports_after_id:
                                    i.pettycashbalance = i.pettycashbalance -last_report.ammount
                                    i.save()

                            except ObjectDoesNotExist:
                    # Handle the case where there are no objects in the database
                                print("No objects found in the database.")
                                last_report = None            



                        
                user_products.delete()

                      
                        

                return HttpResponseRedirect("/expense")
         





         


         products =  paybillcatogory.objects.all()
         myFilter = expensefilter(request.GET, queryset=products)
         products = myFilter.qs    
         orders=dailyreport.objects.all().order_by('datetime').last()
         context = {#'category': category,
               'orders': orders,
               'form':form,
               'myFilter':myFilter,
               'pro':products,
               'user_products':user_products,
               'total':total,
               'form2':form2,
               'form3':form3,
               'form4' :form4,
               }


         return render(request, 'core/expense.html',context)

def expensestore(request):

         orders=dailyreport.objects.all().last()
         #myFilter =dailyreportfilter(request.GET,queryset=orders)
         user_products = temppaybill.objects.filter(user=request.user)
         
         total=0
         total1=0
         for gs in user_products:
           total+=gs.ammount 

         

         for rs in  user_products:
                detail = paybill()
                detail.paybillcatogory =rs.paybillcatogory
                paybilllast=paybill.objects.all().last()
                 # Order Id
                detail.pettycashbalance=paybilllast.pettycashbalance-rs.ammount
                detail.ammount  = rs.ammount 
                detail.remarks    = rs.remarks
                detail.user  = request.user
                detail.typecat="payment"
                detail.save()
                
                user_products.delete()

         item, created =dailyreport.objects.get_or_create(
            
            petteyCash=orders.petteyCash-total,
            billexpense=total,
            ammount=orders.ammount,
            reporttype="office expense"
            )      
                 

         return HttpResponseRedirect("/expense")



def delete_item(request,id):
        item = UserItem.objects.get(id=id)
        #item1 = sold.objects.get(pk=product_pk)
        item.delete()         
        return HttpResponseRedirect(reverse('cart'))

def delete_itemgroup(request, id):
    # Assuming UserItem has a field called 'product_id' which stores the ID of the product
    items = UserItem.objects.filter(product_id=id)
    
    # Delete the items associated with the given product ID
    items.delete()

    product = Product.objects.get(pk=id)
    
    # Get the group name of the selected product
    group_name = product.groupname
    
    # Filter products from the same group where mother is equal to 1
    mother_products = Product.objects.filter(groupname=group_name, mother=True)
    
    # Assuming there's only one mother product, you can get its ID
    if mother_products.exists():
        mother_product_id = mother_products.first().id
        # Redirect to the 'group' URL with mother product ID in the URL
        return HttpResponseRedirect(f"/{mother_product_id}/group")
    else:
        # If there's no mother product, simply redirect to the 'group' URL without including the ID parameter.
        return HttpResponseRedirect(f"/{id}/group")
    



def deletexpense(request, id):
    # Assuming UserItem has a field called 'product_id' which stores the ID of the product
    items = temppaybill.objects.filter(paybillcatogory_id=id)
    
    # Delete the items associated with the given product ID
    items.delete()

    # product = Product.objects.get(pk=id)
    
    # Get the group name of the selected product
    
        # If there's no mother product, simply redirect to the 'group' URL without including the ID parameter.
    return HttpResponseRedirect("/expense")





def deleteinvoice(request, id):

    item = sold.objects.filter(order_id=id)
    orders=Order.objects.filter(id=id).last()
    updates = {}
    dhaka_timezone = pytz.timezone('Asia/Dhaka')

# Get the current time in the Asia/Dhaka timezone
    current_time_dhaka = datetime.datetime.now(dhaka_timezone)
    for a in item:
        # Use F() expression to update the quantity directly in the database
        Product.objects.filter(id=a.product.id).update(quantity=F('quantity') + a.quantity)

        pro=Product.objects.filter(id=a.product.id).last()
        item5, created =plreport.objects.get_or_create(
                     product_id=pro.id,
                     
                     datetime=current_time_dhaka ,
                     costprice= pro.price,
                     price1=a.price1,
                     price2=a.price2,
                     reporttype="delete invoice",
                     stockquantity=pro.quantity,
                     changequanitity = a.quantity,
                     user=request.user,
                    )

    
    item.delete()      

    item1 = get_object_or_404(Order, id=id)

    daily_reports_after_id =dailyreport.objects.filter(datetime__gt=orders.datetime).order_by('datetime')
    # daily_reports_after_id = dailyreport.objects.filter(order_id__gt=id)
    
    # Daily report amount update
    for i in daily_reports_after_id:
        i.ammount -= item1.paid
        i.save()

    if item1.customer != None:
        item1.customer.balance -= item1.due
        item1.customer.save()
        order = Order.objects.get(id=id)
        order_creation_date = order.added
        
        # Query all balance sheet entries created after the order's creation date
        balance_sheets = Customerbalacesheet.objects.filter(added__gt=order_creation_date, customer=order.customer) 
            
        for i in balance_sheets:
            i.balance -= order.due
            i.save()
    
    item1.delete() 
    messages.success(request, 'invoice deleted  successfully')
    return HttpResponseRedirect("/soldlist")


class CountryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Product.objects.none()

        qs = Product.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs        

def sms(request):
    # Data to pass in the context

    current_date = dt_datetime.now().strftime("%Y-%m-%d")
    orders=dailyreport.objects.all().last()
    orders_not_sent = Order.objects.filter(smssend=False)

# Calculate the sum of totalprice, due, and paid
    total_sale = orders_not_sent.aggregate(total_totalprice=Sum('totalprice'))['total_totalprice'] or 0
    cash_sale = orders_not_sent.aggregate(total_paid=Sum('paid'))['total_paid'] or 0
    bill_receive = bill.objects.filter(smssend=False).aggregate(total_amount=Sum('ammount'))['total_amount'] or 0
    closing_balance = orders.ammount

# Construct the message including the current date
    message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"

     #message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"

    context = {
    'message': message,
    # Include other context variables here if needed
}
    # Render the template with context data
    return render(request, "core/sms_template.html", context)    



import requests
def smssend(request):
    # Data to pass in the context

    current_date = dt_datetime.now().strftime("%Y-%m-%d")
    orders=dailyreport.objects.all().last()
    orders_not_sent = Order.objects.filter(smssend=False)

# Calculate the sum of totalprice, due, and paid
    total_sale = orders_not_sent.aggregate(total_totalprice=Sum('totalprice'))['total_totalprice'] or 0
    cash_sale = orders_not_sent.aggregate(total_paid=Sum('paid'))['total_paid'] or 0
    bill_receive = bill.objects.filter(smssend=False).aggregate(total_amount=Sum('ammount'))['total_amount'] or 0
    closing_balance = orders.ammount

# Construct the message including the current date
    message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"

     #message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"
    




    

    url = 'https://login.esms.com.bd/api/v3/sms/send'
    headers = {
    'Authorization': 'Bearer 297|fOiAZt4BLS5eL1MTjmk4UZvWlHPaOnsIhpW7ivqq',
    'Content-Type': 'application/json'
}
    recipients = ["8801814392710","8801922542456","8801815644860"]
    sender_id = "8809601001296"
    #

    for recipient in recipients:
        data = {
            "recipient": recipient,
            "sender_id": sender_id,
            "type": "plain",
            "message": message
        }

        response = requests.post(url, headers=headers, json=data)

        print(f"Recipient: {recipient}")
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        print()

#recipients = ['8801311848771', '8801814392710']
        data = {
            "recipient": "8801814392710",
            "sender_id": "8809601001296",
            "type": "plain",
            "message": "Rohan is fucking madarchud!"
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # If there's an error, redirect with an error message
            return HttpResponseRedirect("/sms?error=Error occurred while sending SMS. Please try again later.")
        
        orders_not_sent.update(smssend=True)
        all_bills = bill.objects.all()

# Loop through each bill object and set smssend to True
        for bill_obj in all_bills:
            bill_obj.smssend = True
            bill_obj.save()

    # If all SMS sent successfully, redirect with a success message
    return HttpResponseRedirect("/sms?success=SMS sent successfully.")  




def salesreport(request):
         start_date = request.GET.get('start_date')
         end_date = request.GET.get('end_date')
         if not end_date:
           
           end_date =dt_datetime.now().strftime('%Y-%m-%d')

         
   
         orders=dailyreport.objects.all().order_by('id')
         myFilter =dailyreportfilter(request.GET, queryset=orders)
         orders = myFilter.qs
         s=0
         c=0
         e=0
         profit=0
         l=0
         open=0
        
         cash=0
         dew=0
         open2=0
         corporrateex=0
         discount=0
         billa=bill.objects.all()
         closeblance=0
         comm=0
         returnprice=0
         returncostprice=0
         soldlist=sold.objects.all().filter(groupproduct =False)
         orderlist=Order.objects.all()
         officeexpense=0
         pettycashtransfer = 0
         for rs in orders :
            
            # if l==0:
            #   open=rs.ammount
            #   l=l+1
            
            if rs.reporttype == 'office expense':
               officeexpense=rs.billexpense+officeexpense
            returnprice=returnprice+rs.returnprice
            returncostprice=returncostprice+rs.returncostprice
            corporrateex=rs.billexpense+ corporrateex
            if rs.reporttype == "COMMISSION":
               comm=comm+rs.billexpense  
            if rs.reporttype == "Discount":     
               discount=rs.billexpense +discount     

            if rs.reporttype == "FUND TRANSFER":     
               pettycashtransfer=rs.billexpense +pettycashtransfer     

            for b in soldlist: 
              if b.order_id == rs.order_id and rs.order_id  is not None:
                 s=b.total_price+s
                 c=b.total_costprice+c
                 e=b.exchange_ammount+e
                 profit=profit+b.totalprofit

            for  t in orderlist:      
               if t.id == rs.order_id and rs.order_id  is not None:
                  cash=t.paid+cash
                  
            for  ac in billa:      
               if ac.order_id == rs.order_id and rs.order_id  is not None:
                  dew=ac.ammount+dew    

         
         #soldlist=sold.objects.filter(order_id__in=s)
         
         
         paginator = Paginator(orders, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         orders = paginator.get_page(page_number)
         

         for x in list(reversed(list(orders)))[0:1]:
            closeblance=x.ammount
        
         if open is not None and  cash is not None and  dew is not None:
           open2= open +dew+cash
         withoutex=s-e
         aftercommmision=closeblance+corporrateex
         totalcost=comm+discount+c+ returnprice
         netsale =s-returnprice
         grossprofit=s-totalcost
         netprofit=grossprofit- officeexpense
         if c == 0 :
             percentageprofit=0
         if c != 0 :   
            percentageprofit=(grossprofit/c ) *100
         duesales=withoutex-cash
         pettycashreportbalnce=closeblance+corporrateex
         commisiondisreportbalnce=pettycashreportbalnce+pettycashtransfer
         cashreturnbalance=commisiondisreportbalnce+comm+discount
         collentionbalance= cashreturnbalance+returnprice
         openbalance=collentionbalance-(cash+dew)
         #newreturncost =returnprice - returncostprice



        #for calculating previous time duration  order 
         

         orders_within_time_range = dailyreport.objects.filter(
    added__range=(start_date, end_date)
)

# Retrieve returnn instances within the same time range
         returnn_within_time_range = returnn.objects.filter(
    sold__order__added__range=(start_date, end_date)
)

# Exclude dailyreport instances where associated returnn objects fall within the time range
         orders_not_in_range = orders_within_time_range.exclude(
    id__in=returnn_within_time_range.values_list('sold__order__id', flat=True)
)           
         oldreturnpricet=0
         oldreturncostt=0
         for rs in orders_not_in_range :
              
             oldreturnpricet=rs.returnprice+oldreturnpricet
                
         netsale2 =s - (returnprice-oldreturnpricet)

         context = {#'category': category,
               'pettycashreportbalnce':pettycashreportbalnce,
               'commisiondisreportbalnce':commisiondisreportbalnce,
               'cashreturnbalance':cashreturnbalance,
               'collentionbalance':collentionbalance,
               'openbalance':openbalance,
               'orders': orders,
               'myFilter':myFilter,
               'a':soldlist,
               'duesales':duesales,
                'c':c,
                's':s,
                'e':e,
                'pettycashtransfer':pettycashtransfer,
                'percentageprofit':percentageprofit,
                'grossprofit': grossprofit,
                'netprofit':netprofit,
                'totalcost':totalcost,
                'withoutex':withoutex,
                'profit':profit,
                'open':open,
                'cash':cash,
                'dew' :dew,
                'open2':open2,
                'comm' :comm,
                'discount':discount , 
                'closeblance':closeblance,
                'corporrateex':corporrateex,
                'aftercommmision':aftercommmision,
                'returnprice':returnprice,
                 'returncostprice': returncostprice,
                'officeexpense':officeexpense,
                'start_date': start_date,
                 'end_date': end_date,
                 'netsale' :netsale,
                 'netsale2' :netsale2,
                 'oldreturnpricet':oldreturnpricet,
               }  
    
         return render(request, "core/salesreport.html",context )           


def expensereport(request):
         credit1 =0
         debit1= 0
          

         orders=paybill.objects.all().order_by('datetime')
         myFilter =paybillfilter(request.GET, queryset=orders)
         orders = myFilter.qs 
         
         
         for rs in orders :
             credit1 = credit1 + (rs.reloadpetteycash if rs.reloadpetteycash is not None else 0)
             debit1 = debit1 + (rs.ammount if rs.ammount is not None else 0)
        
         context = {#'category': category,
               'orders': orders,
               'myFilter':myFilter,
               'credittotal'  :credit1,
               'debit1total'   :debit1
               }


         return render(request, 'core/expensereport.html',context)



def corporatepayment(request):
    suppliers = supplier.objects.all()
    if request.method == 'POST':
        selected_supplier_id = request.POST.get('supplier')
        amount = request.POST.get('amount')
        des = request.POST.get('description')
        selected_supplier = supplier.objects.get(id=selected_supplier_id)
        selected_supplier.balance = selected_supplier.balance - int(amount)
        selected_supplier.save()

        orders=dailyreport.objects.all().last()
        item, created =paybill.objects.get_or_create(

             pettycashbalance=orders.petteyCash - int(amount),
             ammount =int(amount),
             typecat="corporate payment " + selected_supplier.name,
             remarks = des
             )
        item, created =dailyreport.objects.get_or_create(
            
             ammount =orders.ammount ,
             billexpense= int(amount) ,
             reporttype="corporate payment " + selected_supplier.name,
             petteyCash = orders.petteyCash - int(amount)
             
             )
        
        
        return redirect('cart')

    context = {#'category': category,
               'suppliers': suppliers ,
              
               }
    
    return render(request, "core/corporatepayment.html",context)  


class AutocompleteView(View):
    def get(self, request):
        query = request.GET.get('term', '')
        countries = Product.objects.filter(name__icontains=query)[:10]
       
        results = []
        for country in countries:
            country_json = {
                'id': country.id,
                'label': country.name,
                'value': country.productcatagory,
            }
            results.append(country_json)
        return JsonResponse(results, safe=False) 


#### apiproductlist

@api_view(['GET'])
def api_productlist(request):
    tasks = UserItem.objects.filter(user=request.user, groupproduct=False).order_by('-id')
    serializer = TaskSerializer(tasks, many=True)
    #total_sum = tasks.aggregate(total_sum=Sum('price1'))['total_sum']  
    total=0
   
    for gs in tasks :
        total+=gs.price1 * gs.quantity

    response_data = {
        'tasks': serializer.data,
        'total_sum': total  # Include the total sum in the response
    }

    return Response(response_data, status=status.HTTP_200_OK)


@csrf_exempt
def delete_user_item(request, item_id):
    if request.method == 'DELETE':
        try:
            with transaction.atomic():
                user_item = get_object_or_404(UserItem, id=item_id)
                product_id = user_item.product_id
                groupname = user_item.product.groupname
                
                # Delete related UserItems in the same group
                if  user_item.product.mother == 1:
                    products_to_delete = UserItem.objects.filter(
                        product__groupname=groupname,
                        product_id__isnull=False  # Ensure valid product_id
                    )
                    products_to_delete.delete()

                    




                
                # Delete the primary UserItem
                user_item.delete()
                
                # Debugging output
                print("UserItem and related records deleted successfully.")
                
                return JsonResponse({"message": "UserItem and related records deleted successfully."})
                
        except UserItem.DoesNotExist:
            return JsonResponse({"error": "UserItem with ID {} does not exist.".format(item_id)})
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product with ID {} does not exist.".format(product_id)})
        except Exception as e:
            return JsonResponse({"error": "An error occurred: {}".format(e)})







    


@csrf_exempt
def apiaddproduct(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct = False
        )

    #obj = get_object_or_404(Product, id = id,mother=True)
   

      
    return JsonResponse({'error': 'Method not allowed'}, status=405)





# product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,related_name='product')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=0,null=True)
#     price1 = models.DecimalField(
#         default=0,
#         decimal_places=0,
#         max_digits=10,
#         validators=[MinValueValidator(0)],
#         null=True
#     )
#     price2 = models.DecimalField(
#         default=0,
#         decimal_places=0,
#         max_digits=10,
#         validators=[MinValueValidator(0)],
#         null=True
#     )
#     added = models.DateTimeField(auto_now_add=True)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
#     model_no = models.CharField(max_length=200,blank=True,null=True)
#     engine_no = models.CharField(max_length=200,null=True,default='',blank=True)
#     status=models.CharField(max_length=10,choices=PRODUCT,default='Direct',null=True)
#     credit=models.CharField(max_length=10,choices=credit,default='noncredit',null=True)
#     productype=models.CharField(max_length=100,choices=PRODUCT1,default='LocalContainer',null=True)
#     enginecomplete=models.CharField(max_length=10,choices=engine,default='incomplete',null=True)
#     remarks = models.CharField(max_length=500,blank=True,null=True)
#     exchange_ammount = models.PositiveIntegerField(default=0,null=True)
#     #exchange_engine = models.CharField(max_length=500,blank=True,default='')
#     sparename = models.CharField(max_length=200,null=True,blank=True)
#     groupproduct = models.BooleanField(null=True,blank=True)


def process_products(request, product_id, quantity):
    shopcart = UserItem.objects.filter(user=request.user, product_id=product_id).first()
    obj = get_object_or_404(Product, id=product_id)
    motherproduct = Product.objects.filter(groupname=obj.groupname, mother=True).first()
    products = Product.objects.filter(groupname=obj.groupname).exclude(groupname='')
   
    for rs in products:
        item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.subpartquantity * quantity
        )
        print(rs.id)

    




@csrf_exempt
def userItemstore(request):
    if request.method == 'POST':
        # Retrieve the form data from the request
        
        json_data = json.loads(request.body)
            # Extract the required fields from the JSON data
        productId = json_data.get('productId')
        product = json_data.get('product')
        quantity = json_data.get('quantity')
        price1 = json_data.get('price1')
        price2 = json_data.get('price2')
        status = json_data.get('status')
        engine = json_data.get('engine')
        engine_no = json_data.get('engine_no')
        exchangeAmount = json_data.get('exchangeAmount')
        spareName = json_data.get('spareName')
        remarks = json_data.get('remarks')
        print(productId)
        obj = get_object_or_404(Product, id = productId)
        # Create an object using the form data


        if int(quantity) > int(obj.quantity) :
            messages.error(request, 'Do not have that quantity')
            return redirect('cart') 
        if int(quantity) <= int(obj.quantity) :
            obj = UserItem.objects.create(
                product_id=productId,
                user_id=request.user.id,
                quantity=quantity,
                price1=price1,
                price2=price2,
                groupproduct = False,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine,
                engine_no = engine_no

                
            )

        # if qua - fs.quantity < 0:
        #     messages.error(request, 'Do not have that quantity')
        #     return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        # form.save()

        # # Update product quantity
        # productnew.quantity = qua - fs.quantity
        # productnew.save()

        # messages.success(request, 'Form submitted successfully')

        
        
       
        obj = get_object_or_404(Product, id = productId)
        motherproduct = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
        if  obj.mother ==1 :
            products = Product.objects.filter(groupname=obj.groupname).exclude(groupname='').exclude(id=obj.id)
            

            # allsubquantity=0
            # for product in products:
            #     if int(product.quantity) < int(product.subpartquantity)*int(quantity) :
            #         allsubquantity=1

            # print(str(allsubquantity) + "JJJJJ")        
            # if allsubquantity ==0:
            for product in products:
                print(product.id)
                
        # Create an object using the form data
                
                print(product.subpartquantity )
                totalquan=product.subpartquantity * int(quantity)
                obj = UserItem.objects.create(
                product_id=product.id,
            
            
                user_id=request.user.id,
                quantity =  totalquan ,
                price1=0,
                price2=0,
                groupproduct = True,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )







       
    
    # pass the object as instance in form
    



        # You can perform additional operations with the created object if needed

        # Return a JSON response
        return JsonResponse({"message": "Form data received and object created successfully"})

    # Return an error response for other request methods
    return JsonResponse({"error": "Invalid request method"}, status=405)






@csrf_exempt
def mruserItemstore(request):
    if request.method == 'POST':
        # Retrieve the form data from the request
        
        json_data = json.loads(request.body)
            # Extract the required fields from the JSON data
        productId = json_data.get('productId')
        product = json_data.get('product')
        quantity = json_data.get('quantity')
        price1 = json_data.get('price1')
        price2 = json_data.get('price2')
        status = json_data.get('status')
        engine = json_data.get('engine')
        exchangeAmount = json_data.get('exchangeAmount')
        spareName = json_data.get('spareName')
        remarks = json_data.get('remarks')
        print(productId)
        obj = get_object_or_404(Product, id = productId)
        # Create an object using the form data


      
        
        obj = UserItem.objects.create(
                product_id=productId,
                user_id=request.user.id,
                quantity=quantity,
                price1=price1,
                price2=0,
                groupproduct = False,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )

        # if qua - fs.quantity < 0:
        #     messages.error(request, 'Do not have that quantity')
        #     return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        # form.save()

        # # Update product quantity
        # productnew.quantity = qua - fs.quantity
        # productnew.save()

        # messages.success(request, 'Form submitted successfully')

        
        
       
        obj = get_object_or_404(Product, id = productId)
        motherproduct = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
        if  obj.mother ==1 :
            products = Product.objects.filter(groupname=obj.groupname).exclude(groupname='').exclude(id=obj.id)
            

            # allsubquantity=0
            # for product in products:
            #     if int(product.quantity) < int(product.subpartquantity)*int(quantity) :
            #         allsubquantity=1

            # print(str(allsubquantity) + "JJJJJ")        
            # if allsubquantity ==0:
            for product in products:
                print(product.id)
                
        # Create an object using the form data
                
                print(product.subpartquantity )
                totalquan=product.subpartquantity * int(quantity)
                obj = UserItem.objects.create(
                product_id=product.id,
            
            
                user_id=request.user.id,
                quantity =  totalquan ,
                price1=0,
                price2=0,
                groupproduct = True,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )







       
    
    # pass the object as instance in form
    



        # You can perform additional operations with the created object if needed

        # Return a JSON response
        return JsonResponse({"message": "Form data received and object created successfully"})

    # Return an error response for other request methods
    return JsonResponse({"error": "Invalid request method"}, status=405)





from django.http import JsonResponse
from django.views.generic import View


class CustomerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Customer.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
    


def groupproductstore(request):
    if request.method == 'GET':
        price = float(request.GET.get('price', 0))  # If price is blank, set it to 0
        quantity = int(request.GET.get('quantity', 0))  # If quantity is blank, set it to 0
        product_id = request.GET.get('product')
        
        # Check if either price or quantity is not null or 0
        if price != 0 or quantity != 0:
            # Check if the object already exists
            existing_object = UserItem.objects.filter(product_id=product_id).first()
            
            if existing_object:
                # Update the existing object based on the provided values
                if price == 0 and quantity != 0:
                    existing_object.quantity = quantity
                elif quantity == 0 and price != 0:
                    existing_object.price1 = price
                elif price != 0 and quantity != 0:
                    existing_object.quantity = quantity
                    existing_object.price1 = price
                existing_object.save()
            else:
                # Create a new object
                new_object = UserItem.objects.create(
                    user_id=request.user.id,
                    price1=price,
                    quantity=quantity,
                    product_id=product_id
                )
                new_object.save()
        
        product = Product.objects.get(pk=product_id)
        
        # Get the group name of the selected product
        group_name = product.groupname
        
        # Filter products from the same group where mother is True
        mother_products = Product.objects.filter(groupname=group_name, mother=True)
        
        # Assuming there's only one mother product, you can get its ID
        if mother_products.exists():
            mother_product_id = mother_products.first().id
            # Redirect to the 'group' URL with mother product ID in the URL
            return HttpResponseRedirect(f"/{mother_product_id}/group")
        else:
            # If there's no mother product, simply redirect to the 'group' URL without including the ID parameter.
            return HttpResponseRedirect("/group")

    





def smssendinvoice(request, id):
    # Define your URL and headers
    url = 'https://login.esms.com.bd/api/v3/sms/send'
    headers = {
        'Authorization': 'Bearer 297|fOiAZt4BLS5eL1MTjmk4UZvWlHPaOnsIhpW7ivqq',
        'Content-Type': 'application/json'
    }
    sender_id = "8809601001296"
    message = "Dear Sir, Thank you for buying and being loyal to us. You are a special and a valued customer to our company.Thanking you!Rana Motors Team "

    # Query the specific order based on the provided ID
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return HttpResponseRedirect("/sms?error=Order not found.")

    if order.Phone:
        recipient = "88" + order.Phone.replace(" ", "")
    else:
        recipient = "88" + order.customer.Phone.replace(" ", "")
    data = {
        "recipient": recipient,
        "sender_id": sender_id,
        "type": "plain",
        "message": message
    }

    response = requests.post(url, headers=headers, json=data)

    print(f"Recipient: {recipient}")
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text}")
    print()

    if response.status_code == 200:
        # If SMS sent successfully, update the smssend field
       
        return HttpResponseRedirect("/soldlist?success=SMS sent successfully.")
    else:
        # If there's an error, redirect with an error message
        return HttpResponseRedirect("/sms?error=Error occurred while sending SMS. Please try again later.")




def smssendbill(request, id):
    # Define your URL and headers
    url = 'https://login.esms.com.bd/api/v3/sms/send'
    headers = {
        'Authorization': 'Bearer 297|fOiAZt4BLS5eL1MTjmk4UZvWlHPaOnsIhpW7ivqq',
        'Content-Type': 'application/json'
    }
    sender_id = "8809601001296"
    message = "bill received successfully"

    # Query the specific order based on the provided ID
    try:
        bills = bill.objects.get(id=id)
    except Order.DoesNotExist:
        return HttpResponseRedirect("/sms?error=Order not found.")

    if bills.order:
        recipient = "88" + bills.order.Phone.replace(" ", "")
    else:
        recipient = "88" + bills.customer.Phone.replace(" ", "")
    data = {
        "recipient": recipient,
        "sender_id": sender_id,
        "type": "plain",
        "message": message
    }

    response = requests.post(url, headers=headers, json=data)

    print(f"Recipient: {recipient}")
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text}")
    print()

    if response.status_code == 200:
        # If SMS sent successfully, update the smssend field
       
        return HttpResponseRedirect("/bill_list?success=SMS sent successfully.")
    else:
        # If there's an error, redirect with an error message
        return HttpResponseRedirect("/sms?error=Error occurred while sending SMS. Please try again later.")
    



def smssendcustomer(request, id):
    if request.method == "POST":
        # Define your URL and headers
        url = 'https://login.esms.com.bd/api/v3/sms/send'
        headers = {
            'Authorization': 'Bearer 297|fOiAZt4BLS5eL1MTjmk4UZvWlHPaOnsIhpW7ivqq',
            'Content-Type': 'application/json'
        }
        sender_id = "8809601001296"

        # Get the message from the form data
        message = request.POST.get('message')

        # Query the specific order based on the provided ID
        try:
            customers = Customer.objects.get(id=id)
        except Order.DoesNotExist:
            return HttpResponseRedirect("/sms?error=Order not found.")

        # Use order.Phone if available, otherwise use order.customer.phone
       
        recipient = "88" + customers.Phone.replace(" ", "")
       

        data = {
            "recipient": recipient,
            "sender_id": sender_id,
            "type": "plain",
            "message": message
        }

        response = requests.post(url, headers=headers, json=data)

        print(f"Recipient: {recipient}")
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        print()

        if response.status_code == 200:
            # If SMS sent successfully, update the smssend field
            
            return HttpResponseRedirect("/customerlist?success=SMS sent successfully.")
        else:
            # If there's an error, redirect with an error message
            return HttpResponseRedirect("/sms?error=Error occurred while sending SMS. Please try again later.")
    else:
        # Handle the case when the request method is not POST
        return HttpResponseRedirect("/sms?error=Invalid request method.")    
    





def sendsmssupplier(request, id):
    if request.method == "POST":
        # Define your URL and headers
        url = 'https://login.esms.com.bd/api/v3/sms/send'
        headers = {
            'Authorization': 'Bearer 297|fOiAZt4BLS5eL1MTjmk4UZvWlHPaOnsIhpW7ivqq',
            'Content-Type': 'application/json'
        }
        sender_id = "8809601001296"

        # Get the message from the form data
        message = request.POST.get('message')

        # Query the specific order based on the provided ID
        try:
            suppliers = supplier.objects.get(id=id)
        except Order.DoesNotExist:
            return HttpResponseRedirect("/sms?error=Order not found.")

        # Use order.Phone if available, otherwise use order.customer.phone
       
        recipient = "88" + suppliers.Phone.replace(" ", "")
       

        data = {
            "recipient": recipient,
            "sender_id": sender_id,
            "type": "plain",
            "message": message
        }

        response = requests.post(url, headers=headers, json=data)

        print(f"Recipient: {recipient}")
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        print()

        if response.status_code == 200:
            # If SMS sent successfully, update the smssend field
            
            return HttpResponseRedirect("/suplierlist?success=SMS sent successfully.")
        else:
            # If there's an error, redirect with an error message
            return HttpResponseRedirect("/sms?error=Error occurred while sending SMS. Please try again later.")
    else:
        # Handle the case when the request method is not POST
        return HttpResponseRedirect("/sms?error=Invalid request method.")  
    




def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                new_product = form.save(commit=False)

                # Extract the necessary fields from the form data
                groupnamecopy = form.cleaned_data['groupnamecopy']
                groupname = form.cleaned_data['groupname']
                productcatagory = form.cleaned_data['productcatagory']
                price = form.cleaned_data['price']
                quantity = form.cleaned_data['quantity']
                name = form.cleaned_data['name']
                mother = form.cleaned_data['mother']
                # Set the fields on the new product
              

                # Create a new product instance
                new_product1 = Product(
                    groupname=groupname,
                    productcatagory=productcatagory,
                    price=price,
                    quantity=quantity,
                    name=name,
                    mother=mother,
                )

                # Save the new product
                new_product1.save()
                if groupnamecopy !="":
                # Handle copying products based on groupnamecopy
                    user_products = Product.objects.filter(groupname=groupnamecopy).exclude(mother=1)
                    
                    if user_products.exists():
                        new_products = []
                        for rs in user_products:
                            new_products.append(Product(
                                name=rs.name.split('-')[0] + " -" + groupname,
                                productcatagory=productcatagory,
                                price=0,
                                quantity=0,
                                groupname=groupname,
                                subpartquantity=rs.subpartquantity
                            ))
                        Product.objects.bulk_create(new_products)
                
                messages.success(request, 'Product created successfully.')
                return redirect('cart')  # Redirect to a success page
            except Exception as e:
                messages.error(request, f'Error creating product: {e}')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = ProductForm()

    # Get unique group names from the Product model
    groupnames = list(Product.objects.values_list('groupname', flat=True).distinct())

    return render(request, 'core/product_form.html', {'form': form, 'groupnames': groupnames})


def autocomplete_groupnamecopy(request):
    term = request.GET.get('term')  # Get search term from AJAX request
    products = Product.objects.filter(groupname__icontains=term)[:10]  # Adjust queryset as needed
    results = list(products.values_list('groupname', flat=True))
    return JsonResponse(results, safe=False)


def autocomplete_category(request):
    term = request.GET.get('term')  # Get search term from AJAX request
    products = Product.objects.filter(productcatagory__icontains=term)[:10]  # Adjust queryset as needed
    results = list(products.values_list('productcatagory', flat=True))
    return JsonResponse(results, safe=False)





def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cart')  # Redirect to a success page
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form})






def supplier_create_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cart')  # Redirect to a success page
    else:
        form = SupplierForm()
    return render(request, 'core/customer_form.html', {'form': form})   



def paybillcategory_create_view(request):
    if request.method == 'POST':
        form = PayBillCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cart')  # Redirect to a success page
    else:
        form = PayBillCategoryForm()
    return render(request, 'core/customer_form.html', {'form': form}) 




def corpocategory_create_view(request):
    if request.method == 'POST':
        form = CorpoCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cart')  # Redirect to a success page
    else:
        form = CorpoCategoryForm()
    return render(request, 'core/customer_form.html', {'form': form})





def update_paybill(request, pk):
    # Retrieve the last daily report entry
    orders = dailyreport.objects.all().order_by('datetime').last()
    # Retrieve the paybill instance to be updated
    paybill_instance = get_object_or_404(paybill, pk=pk)
    original_amount = paybill_instance.ammount
    
    if request.method == 'POST':
        form = PaybillForm(request.POST, instance=paybill_instance)
        if form.is_valid():
            # Save the updated paybill instance but don't commit to DB yet
            new_product = form.save(commit=False)
            new_amount = new_product.ammount
            # Commit the updated paybill instance to DB
            new_product.save()
            
            # Find all paybill entries after the updated one (including itself)
            daily_reports_after_id = paybill.objects.filter(datetime__gte=paybill_instance.datetime).order_by('datetime')
            
            # Update the pettycashbalance by subtracting the original amount
            for i in daily_reports_after_id:
                i.pettycashbalance += original_amount
                i.save()
            
            # Update the pettycashbalance by adding the new amount
            for i in daily_reports_after_id:
                i.pettycashbalance -= new_amount
                i.save()
            
            # Update the last daily report's petty cash
            if orders:
                pay=paybill.objects.all().order_by('datetime').last()
                orders.petteyCash = pay.pettycashbalance
                
                orders.save()
            
            return redirect('expensereport')  # Replace with your success URL or view name
    else:
        form = PaybillForm(instance=paybill_instance)
    
    return render(request, 'core/customer_form.html', {'form': form})




def delete_all_products(request):
    # Product.objects.all().delete()

    products = Product.objects.all()
    updated_count = 0

    for product in products:
            if product.price is not None and (product.avg_price is None or product.avg_price != product.price):
                product.avg_price = product.price
                product.save()
                updated_count += 1

    delete_all_products
    return render(request, 'core/customer_form.html')



from django.shortcuts import render
from .models import Product
from django.db.models import Sum, F, FloatField


def grouped_products(request):
    categories = Product.objects.values('productcatagory').distinct()
    
    grouped_products = {}
    total_price_all_categories = 0  # To accumulate total price across all categories
    
    for category in categories:
        products = Product.objects.filter(productcatagory=category['productcatagory']).exclude(quantity=0)
        
        # Filter products where mother is not true (assuming mother=1 means mother=True)
        total_price_category = products.exclude(mother=True).aggregate(
            total=Sum(F('quantity') * F('avg_price'), output_field=FloatField())
        )['total'] or 0
        
        grouped_products[category['productcatagory']] = {
            'products': products,
            'total_price': total_price_category
        }
        
        total_price_all_categories += total_price_category  # Accumulate total price for all categories
    
    return render(request, 'core/grouped_products.html', {
        'grouped_products': grouped_products,
        'total_price_all_categories': total_price_all_categories
    })




from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Product, sold


def product_list_grouped_by_category(request):
    # Query distinct product categories that have sold items with non-zero quantity
    distinct_categories = sold.objects.filter(quantity__gt=0).values_list('product__productcatagory', flat=True).distinct()

    products_by_category = []
    for category in distinct_categories:
        # Query products for each distinct category with non-zero sold quantity
        products_in_category = Product.objects.filter(
            productcatagory=category,
            sold__quantity__gt=0  # Filter to ensure non-zero sold quantity
        ).annotate(
            total_quantity_sold=Sum('sold__quantity'),
            total_return_quantity=Sum('sold__returnquantity'),
            total_cost_price=ExpressionWrapper(F('sold__costprice') * F('sold__quantity'), output_field=DecimalField())
        ).order_by('name')  # Adjust ordering as needed

        # Calculate total quantities where mother is True (mother=1)
        total_mother_quantity = sold.objects.filter(
            product__productcatagory=category,
            quantity__gt=0,  # Filter to ensure non-zero sold quantity
            product__mother=True
        ).aggregate(
            total_mother_quantity=Sum('quantity')
        )['total_mother_quantity'] or 0

        if products_in_category.exists():
            total_category_quantity_sold = products_in_category.aggregate(
                total_category_quantity_sold=Sum('sold__quantity')
            )['total_category_quantity_sold'] or 0

            total_category_price = products_in_category.aggregate(
                total_category_price=Sum('total_cost_price')
            )['total_category_price'] or 0

            products_by_category.append({
                'category': category,
                'products': products_in_category,
                'total_category_price': total_category_price,
                'total_category_quantity_sold': total_category_quantity_sold,
                'total_mother_quantity': total_mother_quantity
            })

    context = {
        'products_by_category': products_by_category
    }
    return render(request, 'core/soldreportgroup.html', context)



def menu_view(request):
    menus = [
        {"name": "INVOICE/BILL ENTRY", "url": "", "icon": "fa-solid fa-file-invoice"},
        {"name": "INVOICE/BILL LIST", "url": "/soldlist", "icon": "fa-solid fa-file-invoice"},
        
        {"name": "EXPENSE", "url": "/expense", "icon": "fa-solid fa-coins"},
       
        {"name": "CLIENT LEDGER", "url": "/customerlist", "icon": "fa-solid fa-people-group"},
        {"name": "SUPPLIER LEDGER", "url": "/suplierlist", "icon": "fa-solid fa-people-group"},
         
        
        {"name": "RETURN LIST", "url": "/returnlist", "icon": "fa-solid fa-list"},
        {"name": "BILL RECEIVE LIST", "url": "bill_list", "icon": "fa-solid fa-list"},
       
        
        {"name": "MRR ENTRY", "url": "/mr", "icon": "fa-solid fa-file-invoice"},
        {"name": "MRR LIST", "url": "/mrinvoicelist", "icon": "fa-solid fa-file-invoice"},
        {"name": "ADD PRODUCT", "url": "/productcreate", "icon": "fa-solid fa-plus"},
        {"name": "ADD CLIENT", "url": "/customercreate", "icon": "fa-solid fa-plus"},
        {"name": "ADD SUPPLIER", "url": "/suppliercreate", "icon": "fa-solid fa-plus"},
        {"name": "NEW EXPENSE CATEGORY", "url": "/paybillcategorycreate", "icon": "fa-solid fa-plus"},
        {"name": "NEW CORPORATE CATEGORY", "url": "/corpocategorycreate", "icon": "fa-solid fa-plus"},
        
        
        
        {"name": "DAILY REPORT", "url": "/daily", "icon": "fa-solid fa-file-pen"},
        {"name": "SALES REPORT", "url": "/salesreport", "icon": "fa-solid fa-file-pen"},
        {"name": "EXPENSE REPORT", "url": "/expensereport", "icon": "fa-solid fa-wallet"},
        {"name": "PRODUCT REPORT", "url": "/plreport", "icon": "ion-icon name='documents-outline'"},
        {"name": "CURRENT PRODUCT", "url": "/currentproduct", "icon": "ion-icon name='documents-outline'"},
        {"name": "ADMIN", "url": "/admin", "icon": "fa-solid fa-user-tie"},
        {"name": "SMS", "url": "/sms", "icon": "fa-solid fa-comments"},
    ]
    return render(request, 'core/menu.html', {'menus': menus})    



from django.shortcuts import render
from django.db.models import Sum, Avg, Count
from .models import sold



def sales_dashboard(request):
    # Aggregate data
    sold_items = sold.objects.all()
    
    # Calculate total sales and profit
    total_sales = sum(item.quantity * (item.price1 or 0) + (item.exchange_ammount or 0) for item in sold_items)
    total_profit = sum((item.quantity * (item.price1 or 0) + (item.exchange_ammount or 0) - (item.costprice or 0)) for item in sold_items)
    
    # Aggregations by product, user, and date
    sales_by_product = sold_items.values('product__name').annotate(total_sales=Sum(F('quantity') * F('price1') + F('exchange_ammount'))).order_by('-total_sales')
    sales_by_user = sold_items.values('user__username').annotate(total_sales=Sum(F('quantity') * F('price1') + F('exchange_ammount'))).order_by('-total_sales')
    sales_by_date = sold_items.values('added__date').annotate(total_sales=Sum(F('quantity') * F('price1') + F('exchange_ammount'))).order_by('added__date')
    profit_by_product = sold_items.values('product__name').annotate(total_profit=Sum(F('quantity') * F('price1') + F('exchange_ammount') - F('costprice'))).order_by('-total_profit')

    context = {
        'total_sales': total_sales,
        'total_profit': total_profit,
        'sales_by_product': sales_by_product,
        'sales_by_user': sales_by_user,
        'sales_by_date': sales_by_date,
        'profit_by_product': profit_by_product,
    }
    return render(request, 'core/sales_dashboard.html', context)