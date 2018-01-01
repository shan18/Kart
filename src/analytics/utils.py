def get_client_ip(request):
    # This function will work for most of the servers but users can change their ip or we can have some other
    # problems with server etc. So we can't always fetch the correct/any ip.
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip
