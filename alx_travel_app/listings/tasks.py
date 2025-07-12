from django.core.mail import send_mail
from django.conf import settings

from celery import shared_task


from .models import Payment


@shared_task
def send_confirm_booking_email(booking_id, email, title):
    """Sends a booking confirmation email to user"""
    subject = f"Booking confirmation for {title}"
    msg = f"""
        Thank you for booking with us.
        
        Your booking for reference {booking_id} for {title} has been confirmed.
        
        Welcome
    """

    send_mail(
        subject=subject,
        message=msg,
        from_email=settings.DEFAULT_FROM_MAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return f"Confirmation email send for {email}"


@shared_task
def send_confirm_payment_mail(payment_id, email):
    """Sends payment confirmation mail to user"""
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        booking = payment.booking
        subject = f"Payment confirmation - {booking.listing.name}"
        msg = f"""
            Dear {booking.user.username}, your payment of {payment.amount} for {booking.listing.name} has been confirmed.
            
            Details:
            * Property      : {booking.listing.name}
            * Check-In      : {booking.start_date}
            * Check-Out     : {booking.end_date}
            * Amount        : {payment.amount}
            * Reference     : {payment.booking_reference}
            * Days          : {booking.end_date - booking.start_date}
            
            Regards,
        """

        send_mail(
            subject=subject,
            message=msg,
            from_email=settings.DEFAULT_FROM_MAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return f"Payment ocnfirmation mail sent to {email}"
    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"
    except Exception as e:
        return f"ERROR: sending confirmation mail {str(e)}"


@shared_task
def send_payment_checkout_mail(payment_id, email, checkout_url):
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        booking = payment.booking
        subject = f"Complete your payment for - {booking.listing.name}"
        msg = f"""
            Hello, {booking.user.username}, please complete your payment for {booking.listing.name} booking.
            
            Details:
            * Property      : {booking.listing.name}
            * Check-In      : {booking.start_date}
            * Check-Out     : {booking.end_date}
            * Amount        : {payment.amount}
            
            Click here to complete payment {checkout_url}
            
            This expires in 24 hours. 
            
            Regards,
            
        """
        send_mail(
            subject=subject,
            message=msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Payment.DoesNotExist:
        return f"Payment {payment_id} does not found"
    except Exception as e:
        return f"ERROR: sending payment checkout mail : {str(e)}"
