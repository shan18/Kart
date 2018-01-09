from .signals import object_viewed_signal


class ObjectViewedMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super(ObjectViewedMixin, self).get_context_data(*args, **kwargs)
        request = self.request
        instance = context.get('object')
        # if is_authenticated is not checked then guest user will get errors in the detail view
        if instance:
            object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return context
