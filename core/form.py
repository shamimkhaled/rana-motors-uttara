from django import forms  
from core.models import Order, UserItem,Product,mrentry,returnn,sold,bill,dailyreport,temppaybill,mrentryrecord,corportepay,Customer,supplier,paybillcatogory,corpocatagory,paybill
from dal import autocomplete
from django.forms.widgets import DateTimeInput
class mrr(forms.ModelForm):  
    datetime= forms.DateTimeField(
        label=" Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:  
        model = mrentry 
        fields = ['supplier','name','address','companyname','companyaddress','paid',"discount","datetime"]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
           
        }



class  useritem(forms.ModelForm):
    datetime= forms.DateTimeField(
        label=" Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )

    class Meta:
        model = Order 
        fields = ['customer', 'name', 'address', 'paid', 'discount', 'Phone', 'vehicleno','datetime']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'customer': autocomplete.ModelSelect2(url='customer-autocomplete'),
        }




      





 
# creating a form
class GeeksForm(forms.ModelForm):
 
    # create meta class
    class Meta:
        # specify model to be used
        model = UserItem
 
        # specify fields to be used
        fields = [
           
          "productype","quantity","engine_no","status","enginecomplete","price1","price2","exchange_ammount","remarks","sparename"
        ]


class returnnform(forms.ModelForm):
    datetime= forms.DateTimeField(
        label="Date Time ",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
 
    # create meta class
    class Meta:
        # specify model to be used
        model = returnn
 
        # specify fields to be used
        fields = [
           
          "quantity","returnreason","status","cashreturnprice","duereturnprice","datetime",
        ]

        

class soldformm(forms.ModelForm):
    datetime= forms.DateTimeField(
        label="Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = sold
        fields = '__all__'
        exclude = ['product','order','user','Phone','customer','discount']



        def clean(self):
            cleaned_data = super().clean()
            quantity = cleaned_data.get('quantity')
            returnquantity = cleaned_data.get('returnquantity')

            if returnquantity and returnquantity > quantity:
                raise forms.ValidationError("Return quantity cannot be greater than so")




class mreditformm(forms.ModelForm):
    datetime= forms.DateTimeField(
        label="Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = mrentryrecord
        fields = '__all__'
        exclude = ['product','order','user','Phone','supplier','discount','datetime']

         




class billfrom(forms.ModelForm):
    datetime= forms.DateTimeField(
        label="Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = bill
        fields = ['name','ammount','billinvoiceid','datetime','bankname','brunchname','ChequeNo','issueDate','ClearingDate']
        widgets = {
            'name': forms.TextInput(attrs={'size': 20}),  # Adjust the size as needed
            'ammount': forms.NumberInput(attrs={'size': 10}),  # Adjust the size as needed
            'billinvoiceid': forms.TextInput(attrs={'size': 15}),  # Adjust the size as needed
            'issueDate': forms.DateInput(attrs={'type': 'date'}),
            'ClearingDate': forms.DateInput(attrs={'type': 'date'}),
        }



class dailyreportt(forms.ModelForm):
    datetime= forms.DateTimeField(
        label="Extra Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )

    class Meta:
        model = dailyreport
        fields = ['petteyCash', 'remarks','reporttype','datetime']  # Include the extra field here
        labels = {
            "petteyCash": ""
        }
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2, 'cols': 15}),  # Adjust rows and cols as needed
        }


class tempbilformm(forms.ModelForm):  
    datetime= forms.DateTimeField(
        label="Extra Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:  
        model =temppaybill
        fields = ['ammount','remarks','datetime']                  
  


class CorportepayForm(forms.ModelForm):

    datetime= forms.DateTimeField(
        label="Extra Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = corportepay
        fields = ['ammount','supplier','corpocatagory','remarks','datetime']


        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2, 'cols': 15}),  # Adjust rows and cols as needed
        }
        # You can customize the widgets or add more options if needed







class CorportepayForm(forms.ModelForm):

    datetime= forms.DateTimeField(
        label="Extra Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = corportepay
        fields = ['ammount','supplier','corpocatagory','remarks','datetime']


        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2, 'cols': 15}),  # Adjust rows and cols as needed
        } 




class tempform(forms.ModelForm):

    datetime= forms.DateTimeField(
        label="Extra Date Time Field",
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = corportepay
        fields = ['datetime']


        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2, 'cols': 15}),  # Adjust rows and cols as needed
        }                  









class ProductForm(forms.ModelForm):
    groupname = forms.CharField(required=False)
    class Meta:
        model = Product
        fields = ['name','pcode','productcatagory', 'status', 'price', 'quantity', 'mother', 'subpartquantity', 'groupname']
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 70%; padding: 8px;'}),
        }

        

    groupnamecopy = forms.CharField(
        label='Group Name Copy',
        widget=forms.TextInput(attrs={'class': 'autocomplete'})
    )
    groupnamecopy = forms.CharField(
        label='Group Name Copy',
        required=False,  # Make groupnamecopy not required
        widget=forms.TextInput(attrs={'class': 'autocomplete'})
    )


from django import forms
from .models import Customer
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'Phone', 'balance']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))





class SupplierForm(forms.ModelForm):
    class Meta:
        model = supplier
        fields = ['name', 'address', 'Phone', 'balance']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))




class PayBillCategoryForm(forms.ModelForm):
    class Meta:
        model = paybillcatogory
        fields = ['name']


        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 70%; padding: 8px;'}),
        }   
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit')) 



class CorpoCategoryForm(forms.ModelForm):
    class Meta:
        model = corpocatagory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 70%; padding: 8px;'}),
        } 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))       




class PaybillForm(forms.ModelForm):
    class Meta:
        model = paybill
        fields = [
            
            'ammount',
            
        ]
       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))        