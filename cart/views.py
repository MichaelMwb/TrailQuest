from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')
@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if not movie_ids:
        return redirect('cart.index')

    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)

    # Create a new order
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()

    # Assign a user-specific order number
    user_orders = Order.objects.filter(user=request.user).order_by('id')
    order.user_order_number = user_orders.count()  # Sequential number for the user
    order.save()

    # Save items in the order
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()

    # Clear the cart after purchase
    request.session['cart'] = {}

    # Pass the user-specific order number to the template
    template_data = {
        'title': 'Purchase confirmation',
        'order': order,  # Send the entire order object, including user_order_number
    }
    
    return render(request, 'cart/purchase.html', template_data)
