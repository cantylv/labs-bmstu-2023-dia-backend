from .models import *

admin.site.register(Service, ServiceAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)