
from urllib.parse import quote

from django.conf import settings


def generate_whatsapp_link(order):
    """
    Generate a WhatsApp Click-to-Chat URL for an order.
    """

    phone = order.branch.whatsapp_number

    # Remove spaces, +, and other formatting characters.
    phone = "".join(
        character
        for character in phone
        if character.isdigit()
    )

    message = f"""
Hello {order.branch.name}!

I would like to place an order.

Order Number: {order.order_number}

Customer: {order.customer.full_name}
Phone: {order.customer.phone_number}

Products:
"""

    for item in order.items.all():
        message += (
            f"\n- {item.product_name}"
            f"\n  Quantity: {item.quantity}"
            f"\n  Unit Price: {order.currency} {item.unit_price:,.2f}"
            f"\n  Subtotal: {order.currency} {item.subtotal:,.2f}\n"
        )

    message += f"""

Total: {order.currency} {order.total_amount:,.2f}

Please confirm my order.

Thank you!
"""

    encoded_message = quote(message.strip())

    return (
        f"https://wa.me/{phone}"
        f"?text={encoded_message}"
    )
