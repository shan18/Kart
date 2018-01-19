"""
Annotation & Aggregation
"""


from django.db.models import Count, Sum, Avg

from orders.models import Order


            """ Annotation """


''' This adds a order_totals field to every object in qs.
The value of order_totals is same as the total field. '''
qs = Order.objects.all().annotate(order_totals=Sum('total'))

''' This adds a product_total field to every object in qs and calculates the sum of
the prices of every product in the order and stores the sum in product_total. (This won't include the shipping cost).'''
qs = Order.objects.all().annotate(product_total=Sum('cart__products__price'))

''' product_avg -> Average product price in each order
product_count -> Number of products in each order '''
qs = Order.objects.all().annotate(product_avg=Avg('cart__products__price'), product_count=Count('cart__products'))

# Print out the values
for i in qs:
    print(i.product_avg)
    print(i.product_count)



            """ Aggregation """


''' Calculates the sum of the total attribute of all the orders in the qs.
It also adds an attribute called 'total__sum'. '''
qs = Order.objects.all().aggregate(Sum('total'))
print(qs)
''' Output:
{'total__sum': Decimal('24481.63')}
'''

''' Avg('total') -> average of total among all the products in qs
Avg('cart__products__price') -> average product price among all the orders in qs
Count('cart_products') -> number of products combining all the orders in qs '''
qs = Order.objects.all().aggregate(Sum('total'), Avg('total'), Avg('cart__products__price'), Count('cart__products'))
print(qs)
''' Output:
{'total__sum': Decimal('63741.32'), 'total__avg': 1416.4737777777782,
'cart__products__price__avg': 504.44452380952436, 'cart__products__count': 42}
'''

''' The above two queries give different values of 'total__sum' on the same qs.
This is because in the 2nd qs, order total is chained with a foreign key 'cart' and when the
regular fields are chained with the foreign key fields, the aggregation causes some error.
To get correct result:
'''
qs = Order.objects.all().aggregate(Sum('total'), Avg('total'))
print(qs)
''' Output:
{'total__sum': Decimal('24481.63'), 'total__avg': 765.0509375000001}
'''


"""
Note: Annotation & Aggregation can be replaced by using a for loop.

The for loop method is inefficient because, if the corresponding template also makes a call to the database with a
for loop then there will be two consecutive calls to the database and this should be avoided. Thus, comes the need to 
annotate or aggregate the data.
"""
