from django.contrib import admin

# Register your models here.
# 
# from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.utils.translation import gettext_lazy as _
from django.forms import Media

from .models import Product,UserItem,Customer,Order,sold,mrentryrecord,supplier,mrentry,returnn,bill,paybill,paybillcatogory,dailyreport,temppaybill,corportepay,corpocatagory,Customerbalacesheet,Customerbalacesheet,supplierbalancesheet,plreport
class OrderProductline(admin.TabularInline):
    model =sold
    
    extra = 0
class OrderAdmin(admin.ModelAdmin):
    
    inlines = [OrderProductline]

class PhotoAdmin(admin.ModelAdmin):
  
    search_fields = ['name']




class ComputerAdmin(admin.ModelAdmin):
    list_filter=('datetime', 'product')
    list_display = ('datetime', 'product')
    search_fields=('datime','product') 


#@admin.register (Product)
#class ViewAdmin(ImportExportModelAdmin):
  #pass

#admin.site.register(Product,OrderAdmin)
#admin.site.register(Customer,OrderAdmin)
admin.site.register(UserItem)
admin.site.register(mrentryrecord)
admin.site.register(mrentry)
admin.site.register(Order)
admin.site.register(plreport)
#admin.site.register(supplier)


admin.site.register(Customerbalacesheet)
admin.site.register(temppaybill)
admin.site.register(dailyreport)
admin.site.register(sold,ComputerAdmin)

admin.site.register(paybill)
admin.site.register(paybillcatogory)
admin.site.register(bill)


class SwitchModelResource(resources.ModelResource):
        class Meta:
            model = Product
    

class SwitchModelAdmin(ImportExportModelAdmin):
        list_display = ('name','price')
        list_filter=['productcatagory']
        resource_class = SwitchModelResource
        inlines = [OrderProductline]
        search_fields = ['name']

admin.site.register(Product,SwitchModelAdmin)





class SwitchModelResource1(resources.ModelResource):
        class Meta:
            model = Customer
    

class SwitchModelAdmin1(ImportExportModelAdmin):
        list_display = ('name','balance')
        search_fields = ['name']
        resource_class = SwitchModelResource1
        
       

admin.site.register(Customer,SwitchModelAdmin1)


class SwitchModelResource2(resources.ModelResource):
        class Meta:
            model = supplier
    

class SwitchModelAdmin2(ImportExportModelAdmin):
        list_display = ('name','balance')
        search_fields = ['name']
        resource_class = SwitchModelResource2
        #inlines = [OrderProductline]
       

admin.site.register(supplier,SwitchModelAdmin2)



class ReturnnAdmin(admin.ModelAdmin):
    list_filter = (
        ('datetime', admin.DateFieldListFilter),
    )

admin.site.register(returnn, ReturnnAdmin)



admin.site.register(corportepay)



admin.site.register(corpocatagory)

admin.site.register(supplierbalancesheet)

#admin.site.register(Customerbalacesheet)


