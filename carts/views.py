from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from store.models import Product, Variation
from .models import Cart,CartItem

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart= request.session.create()
    return cart
    
def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == "POST":
       for item in request.POST:
           key = item
           value = request.POST[key]
           # print(key, value)
           try:
            variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
            # print(variation)
            product_variation.append(variation)

           except:
               pass      


    try:
        cart = Cart.objects.get(card_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(card_id=_cart_id(request))
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product,cart=cart)
        if len(product_variation)>0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(product=product,quantity=1,cart=cart)
        if len(product_variation)>0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
        cart_item.save()
    return redirect('carts')
        



def carts(request,total=0,quantity=0,cart_items=None):
    try:
        cart = Cart.objects.get(card_id=_cart_id(request))
        cart_items =CartItem.objects.filter(cart= cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity +=cart_item.quantity
    except Cart.DoesNotExist as e:
        print(e)
    context =  {
        'total':total,
        'quantity': quantity,
        'cart_items': cart_items
    }
    return render(request,'store/carts.html',context)

def remove_cart(request,product_id):
    cart = Cart.objects.get(card_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if(cart_item.quantity >1):
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('carts')

def remove_cart_item(request,product_id):
    cart = Cart.objects.get(card_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('carts')

def add_cart_item(request,product_id):
    cart = Cart.objects.get(card_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if(cart_item.quantity >=1):
        cart_item.quantity +=1
        cart_item.save()
    return redirect('carts')
