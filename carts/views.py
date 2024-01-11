from django.shortcuts import render,redirect
from store.models import Product
from .models import Cart,CartItem

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart= request.session.create()
    return cart
    
def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(card_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(card_id=_cart_id(request))
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(product=product,quantity=1,cart=cart)
        cart_item.save()
    return redirect('carts')
        



def carts(request,total=0,quantity=0,cart_item=None):
    try:
        cart = Cart.objects.get(card_id=_cart_id(request))
        cart_items =CartItem.objects.filter(cart= cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity +=cart_item.quantity
    except cart.DoesNotExist as e:
        print(e)
    context =  {
        'total':total,
        'quantity': quantity,
        'cart_items': cart_items
    }
    return render(request,'store/carts.html',context)