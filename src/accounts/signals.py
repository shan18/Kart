from django.dispatch import Signal


user_session_signal = Signal(providing_args=['instance', 'request'])
