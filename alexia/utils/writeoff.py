from collections import defaultdict
from django.db.models import Sum

def get_writeoff_products(event, writeoff_purchases):
    writeoff_products = writeoff_purchases.filter(order__event=event) \
        .values('order__writeoff_category__name', 'product') \
        .annotate(total_amount=Sum('amount'), total_price=Sum('price')) \
        .order_by('order__writeoff_category__name', 'product')

    # Group writeoffs by category
    grouped_writeoff_products = defaultdict(lambda: {'products': [], 'total_amount': 0, 'total_price': 0})
    
    # calculate total product amount and total price per category
    for product in writeoff_products:
        category_name = product['order__writeoff_category__name']
        grouped_writeoff_products[category_name]['products'].append(product)
        grouped_writeoff_products[category_name]['total_amount'] += product['total_amount']
        grouped_writeoff_products[category_name]['total_price'] += product['total_price']

    # Convert defaultdict to a regular dict for easier template use
    return dict(grouped_writeoff_products)