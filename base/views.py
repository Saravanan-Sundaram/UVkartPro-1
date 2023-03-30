from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from base.form import CustomUserForm
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json

def home(request):
    products = Products.objects.filter(trending=1)
    return render(request,"TempBase/index.html",{"products":products})

def register(request):
    form= CustomUserForm()
    if request.method == 'POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You can login now.. ")
            return redirect('/login')
    return render(request,"TempBase/register.html",{'form':form}) 

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            
            userna=request.POST['username']
            passwr=request.POST['password']
            user= authenticate(request,username=userna, password=passwr )
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid username or password")
                return redirect("/login")
        return render(request,'TempBase/login.html')
    
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out successfully")
        return redirect('/login')
    
def fav_page(request):
    if request.user.is_authenticated:
        Fav=Favourite.objects.filter(user=request.user)
        return render(request,'TempBase/FavView.html',{"Fav":Fav})
    else:
        messages.error(request,'Login to access your Favourite')
        return redirect("/login")
    
def remove_fav(request,fid):
    fav_item= Favourite.objects.get(id=fid)
    fav_item.delete()
    return redirect("/fav")

def cart_page(request):
    if request.user.is_authenticated:
        cart=CartIn.objects.filter(users=request.user)
        return render(request,'TempBase/cart.html',{"cart":cart})
    else:
        messages.error(request,'Login to access your cart')
        return redirect("/login")
 
def remove_cart(request,cid):
    cart_item= CartIn.objects.get(id=cid)
    cart_item.delete()
    return redirect("/cart")

def collections(request):
    catagory= Category.objects.filter(status=0)
    return render(request,"TempBase/collections.html",{"catagory": catagory})

def collectionsview(request,name):
    if (Category.objects.filter(name=name,status=0)):
        products= Products.objects.filter(category__name=name)
        return render(request,"TempBase/product/index.html",{"products": products,"category_name":name})
    else:
        messages.warning(request,"No such category found.")
        return redirect('collections')

def product_details(request,cname,pname):
    if (Category.objects.filter(name=cname,status=0)):
        if (Products.objects.filter(name=pname,status=0)):
            products= Products.objects.filter(name=pname,status=0).first()
            return render(request,"TempBase/product/product_details.html",{"products": products})
        else:
            messages.error(request,"No such product found.")
            return redirect('collections')
    else:
        messages.error(request,"No such category found.")
        return redirect('collections')
    
def add_to_cart(request):
   if request.headers.get('X-requested-with')== 'XMLHttpRequest':
       if request.user.is_authenticated:
           data=json.load(request)
           product_qty=data['product_qty']
           product_id=data['pid']
           product_status= Products.objects.get(id=product_id)
           if product_status:
               if CartIn.objects.filter(users=request.user,product_id=product_id):
                return JsonResponse({'status':'Product already in cart '},status=200)
               else:
                   if product_status.quantity>=product_qty:
                       CartIn.objects.create(users=request.user,product_id=product_id,product_qty=product_qty)
                       return JsonResponse({'status':'Product added to cart Success'},status=200)
                   else:
                       return JsonResponse({'status':'Product stock not available'},status=200)
       else:
           return JsonResponse({'status':'Login to Add Cart'},status=200)
   else:
       return JsonResponse({'status':'Invalid Access'},status=200)
   
def add_to_fav(request):
    if request.headers.get('X-requested-with')== 'XMLHttpRequest':
       if request.user.is_authenticated:
           data=json.load(request)
           product_id=data['pid']
           product_status= Products.objects.get(id=product_id)
           if product_status:
               if Favourite.objects.filter(user=request.user,product_id=product_id):
                   return JsonResponse({'status':'Product already in Favourite '},status=200)
               else:
                   Favourite.objects.create(user=request.user,product_id=product_id)
                   return JsonResponse({'status':'Product added to Favourite'},status=200)
       else:
           return JsonResponse({'status':'Login to Add Favourite'},status=200)
    else:
       return JsonResponse({'status':'Invalid Access'},status=200)