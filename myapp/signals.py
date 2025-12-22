from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from .models.bill import Bill

def calc_reward_points(customer):
    total = customer.totalExpenditure or 0
    customer_type = customer.tid.name.lower()

    if customer_type == "vip":
        rate = 0.10
    else:
        rate = 0.02

    return int(total * rate)

def recalc_customer_total(customer):
    total = (
        Bill.objects
        .filter(cid=customer)
        .aggregate(total=Sum('totalAmount'))
        ['total']
        or 0
    )

    customer.totalExpenditure = total
    customer.cumulativePoints = calc_reward_points(customer)

    customer.save(update_fields=[
        'totalExpenditure',
        'cumulativePoints'
    ])


@receiver(post_save, sender=Bill)
def bill_post_save(sender, instance, created, **kwargs):
    recalc_customer_total(instance.cid)


@receiver(post_delete, sender=Bill)
def bill_post_delete(sender, instance, **kwargs):
    recalc_customer_total(instance.cid)
