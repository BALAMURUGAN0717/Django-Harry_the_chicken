def cart_context(request):
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
    username = request.session.get('username') or request.COOKIES.get('username')
    # Re-hydrate session from valid cookie if needed
    if not request.session.get('username') and username:
        request.session['username'] = username
        request.session.modified = True
    return {
        'cart_count': cart_count,
        'current_user': username,
    }
