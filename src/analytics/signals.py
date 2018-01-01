from django.dispatch import Signal


# providing_args contains the list of additional arguments that we are going to pass to the signal
# we included request because it has the IP address that we fetched from the user.
object_viewed_signal = Signal(providing_args=['instance', 'request'])
