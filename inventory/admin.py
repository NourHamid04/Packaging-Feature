from django.contrib import admin
from .models import (
    UnitsOfMeasurement,
    PackagingTypes,
    Items,
    PackagingInstructions,
    BillOfMaterials,
    WorkOrders,
    PackagingMaterials,
    Warehouse,
    SalesOrder1,
    Customer,
    Supplier
)

admin.site.register(UnitsOfMeasurement)
admin.site.register(PackagingTypes)
admin.site.register(Items)
admin.site.register(PackagingInstructions)
admin.site.register(BillOfMaterials)
admin.site.register(WorkOrders)
admin.site.register(PackagingMaterials)
admin.site.register(Warehouse)
admin.site.register(SalesOrder1)
admin.site.register(Customer)
admin.site.register(Supplier)
