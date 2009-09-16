def liveblog_order(request):
    valid_orders = {'asc': 'timestamp',
                    'desc': '-timestamp', }
    order = valid_orders['asc'] # default
    if request.GET:
        if request.GET.has_key('order'):
            selected_order = request.GET['order']
            if selected_order in valid_orders.keys():
                order = valid_orders[selected_order]
    return {'liveblog_order': order, }
