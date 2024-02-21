from .models import *

admin.site.register(Service, ServiceAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Bid, BidAdmin)