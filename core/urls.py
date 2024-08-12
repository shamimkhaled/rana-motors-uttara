from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path,include
from .views import  update_view,ggroup,group,mrupdate_view,customersolddeatails,chalan,billcustomer,groupupdate_view,dalyreport,dalyreportsearch,expenseform,expensestore,addproduct,addproductgroup,CountryAutocomplete,sms,salesreport,expensereport,api_productlist,delete_user_item,apiaddproduct,userItemstore,mreditcashmemo,smssend,supplierbalancesheetlist,CustomerAutocomplete,bothcashmemo,groupproductstore,smssendcustomer,sendsmssupplier,product_create,autocomplete_groupnamecopy,customer_create_view,supplier_create_view,paybillcategory_create_view,corpocategory_create_view,update_paybill,sales_dashboard,menu_view,paybillcatogoryAutocompleteview

from django.urls import re_path as url
from django.urls import reverse
from . import views

urlpatterns = [
    path(
        'accounts/login/',
        LoginView.as_view(template_name='core/login.html'),
        name='login'
    ),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('', views.cart, name='cart'),
    path('salesreport', views.salesreport, name='salesreport'),
    
    path('corporatepayment', views.corporatepayment, name='corporatepayment'),
  
    path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    path('<id>/update',update_view ,name='update'),
    path('<id>/addproduct',addproduct ,name='update'),

    path('<id>/group',group,name='group'),
    path('<id>/addproductgroup',views.addproductgroup ,name='update'),

     path('groupproductstore/', views.groupproductstore, name='groupproductstore'),
    path('<id>/groupupdate',groupupdate_view ,name='update'),

    path('<id>/deletegroup', views.delete_itemgroup, name='delete'),
    path('<id>/mrupdate',mrupdate_view ,name='mrupdate'),


    path('<id>/deletexpense', views.deletexpense, name='deletexpense'),

    
    path('soldlist', views.soldlist, name='soldlist'),
    path('mrlist', views.mrlist, name='mrlist'),


    path('<id>/cashmemo', views.cashmemo, name='cashmemo'),
    path('<id>/cashmemo1', views.cashmemo1, name='cashmemo1'),
    path('<id>/billreport', views.billreport, name='billreport'),


     path('<id>/chalan', views.chalan, name='chalan'),
     path('<id>/deleteinvoice', views.deleteinvoice, name='deleteinvoice'),
      path('<id>/editcashmemo', views.editcashmemo, name='editcashmemo'),
    path('<id>/fianaleditcashmemo', views.fianaleditcashmemo, name='fianaleditcashmemo'),
    path('<id>/bothcashmemo', views.bothcashmemo, name='bothcashmemo'),



   


   # path('<id>/mrmemo', views.mrmemo, name='mrmemo'),
   
    path('<id>/returnn', views.returnno, name='return'),
    path('<id>/returnitem', views.returnreasonn, name='returnreasonn'),
    path('returnlist', views.returnlist, name='returnlist'),
    #bill
    path('bill_list', views.bill_list, name='bill_list'),
    path('supplierbill_list', views.supplierbill_list, name='supplierbill_list'),
    path('<id>/bill', views.billt, name='bill'),
   
    path('productlist', views.productlist, name='productlist'),

    path('mr', views.mr, name='mr'),
    path('mrinvoicelist', views.mrinvoicelist, name='mrinvoicelist'),
    path('<id>/mrcashmemo', views.mrcashmemo, name='mrcashmemo'),
    path('<id>/mreditcashmemo', views.mreditcashmemo, name='mreditcashmemo'),
    path('<id>/mrfianaleditcashmemo', views.mrfianaleditcashmemo, name='mrfianaleditcashmemo'),

    
    path('<id>/delete', views.delete_item, name='delete'),
   
    path('<id>/billcustomer', views.billcustomer, name='bill'),

    path('customerlist', views.customerlist, name='customerlist'),
   # path('customerdetail', views.customersolddeatails, name='bill'),
    path("search/", views.search, name="search_results"),
    path('customerbalancesheet', views.customerbalancesheetlist, name='customerbalancesheet'),


    path('suplierlist', views.suplierlist, name='suplierlist'),
    path('supplierbalancesheet', views.supplierbalancesheetlist, name='supplierbalancesheet'),



    path("daily", views.dalyreport, name=""),
    path("expensereport", views.expensereport, name="expensereport"),
    path('plreport', views.plreportlist, name='plreportlist'),
     path('productview', views.productreport, name='productreport'),
 

    path("expense", views.expense, name="expense"),
    

    
    path("sms", views.sms, name="sms"),
    path("smssend", views.smssend, name="smssend"),
    path('<id>/smssendinvoice', views.smssendinvoice, name='smssendinvoice'),
    path('<id>/smssendbill', views.smssendbill, name='smssendbill'),
    path('send-smscustomer/<int:id>/', views.smssendcustomer, name='send-smscustomer'),
    path('send-smssupplier/<int:id>/', views.sendsmssupplier, name='send-smssupplier'),




    path("<id>/expenseform", views.expenseform ,name=""),
    path("expensestore", views.expensestore ,name=""),
   # path("dailysearchresult", views.dalyreportsearch, name="search_results"),
    #path("corporatepay", views.corporatepayment ,name=""),


    #api

    path('api_productlist/', views.api_productlist, name="api_productlist"),
    path('api-delete/<int:item_id>/', views.delete_user_item, name='delete_user_item'),
    path('apiaddproduct/<int:item_id>/', views.apiaddproduct, name='apiaddcart'),

    path('api_useritemstore/', views.userItemstore, name="userItemstore"),
    path('api_mruseritemstore/', views.mruserItemstore, name="mruserItemstore"),

     path('customer-autocomplete/', CustomerAutocomplete.as_view(), name='customer-autocomplete'),
     path('paybillcatogoryAutocomplete/', paybillcatogoryAutocompleteview.as_view(), name='paybillcatogoryAutocomplete'),
     


     path('productcreate', views.product_create, name='product_create'),
     path('autocomplete-groupnamecopy/', views.autocomplete_groupnamecopy, name='autocomplete-groupnamecopy'),
     
     path('autocomplete_category/', views.autocomplete_category, name='autocomplete_category'),
     path('customercreate', views.customer_create_view, name='customer_create'),
     path('suppliercreate', views.supplier_create_view, name='supplier_create'),
     path('paybillcategorycreate', views.paybillcategory_create_view, name='paybillcategory_create'),
     path('corpocategorycreate', views.corpocategory_create_view, name='corpocategory_create'),
     path('paybill/update/<int:pk>/', views.update_paybill, name='update_paybill'),
     
     path('delete-all-products/', views.delete_all_products, name='delete_all_products'),



     path('currentproduct', views.grouped_products, name='grouped_products'),


     path('soldreportgroup', views.product_list_grouped_by_category, name='product_list_grouped'),

     path('menu', views.menu_view, name='menu'),

     path('dashboard', views.sales_dashboard, name='sales_dashboard'),


     
]





   

