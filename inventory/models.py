
from django.db import models
from django.utils import timezone
from .enums import PackagingLevel
from tinymce.models import HTMLField

WAREHOUSE_TYPES = [(1, 'Type1'), (2, 'Type2')]

LEVEL_OPTIONS = [
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('Tertiary', 'Tertiary')
    ]

class Warehouse(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    warehouse_type = models.IntegerField(choices=WAREHOUSE_TYPES)
    description = models.TextField(blank=True)
    total_capacity = models.IntegerField()
    available_capacity = models.IntegerField()
    packaging_materials = models.ForeignKey('PackagingMaterials', on_delete=models.CASCADE, null=True, blank=True)
    packaging_types = models.ForeignKey('PackagingTypes', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        permissions = [
            ("can_create_warehouse", "Can create warehouse"),
            ("can_view_warehouse", "Can view warehouse"),
            ("can_update_warehouse", "Can update warehouse"),
            ("can_delete_warehouse", "Can delete warehouse"),
        ]

    def __unicode__(self):
        return u'%(code)s | %(name)s' % {'code': self.code, 'name': self.name}

class UnitsOfMeasurement(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    class Meta:
        permissions = [
            ("can_create_unit_of_measurement", "Can create unit of measurement"),
            ("can_view_unit_of_measurement", "Can view unit of measurement"),
            ("can_update_unit_of_measurement", "Can update unit of measurement"),
            ("can_delete_unit_of_measurement", "Can delete unit of measurement"),
        ]

    def __str__(self):
        return self.name

class PackagingMaterials(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.FloatField(default=0.0)  # Default value added here
    available_quantity = models.FloatField(default=0.0)  # Add default value here
    created_at = models.DateTimeField(default=timezone.now)  # Add default value here
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("can_create_packaging_material", "Can create packaging material"),
            ("can_view_packaging_material", "Can view packaging material"),
            ("can_update_packaging_material", "Can update packaging material"),
            ("can_delete_packaging_material", "Can delete packaging material"),
        ]

    def __str__(self):
        return self.name



class PackagingTypes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    weight = models.FloatField()
    volume = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    material = models.ForeignKey(PackagingMaterials, on_delete=models.CASCADE)
    cost = models.FloatField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.CharField(max_length=100, choices=LEVEL_OPTIONS)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)  # Add this line

    class Meta:
        permissions = [
            ("can_create_packaging_type", "Can create packaging type"),
            ("can_view_packaging_type", "Can view packaging type"),
            ("can_update_packaging_type", "Can update packaging type"),
            ("can_delete_packaging_type", "Can delete packaging type"),
        ]

    def __str__(self):
        return self.name

class Items(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=100)
    uom = models.ForeignKey(UnitsOfMeasurement, on_delete=models.CASCADE)
    cost = models.FloatField()
    weight = models.FloatField()
    volume = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    packaging_type = models.ForeignKey(PackagingTypes, on_delete=models.CASCADE, default=1)  # Default value for existing rows
    stock_quantity = models.IntegerField()
    reorder_level = models.IntegerField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, default=1)  # Default value for existing rows

    class Meta:
        permissions = [
            ("can_create_item", "Can create item"),
            ("can_view_item", "Can view item"),
            ("can_update_item", "Can update item"),
            ("can_delete_item", "Can delete item"),
        ]

    def __str__(self):
        return self.name

class PackagingInstructions(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    packaging_type = models.ForeignKey(PackagingTypes, on_delete=models.CASCADE)
    steps = models.TextField()
    required_tools = models.CharField(max_length=100)

    class Meta:
        permissions = [
            ("can_create_packaging_instruction", "Can create packaging instruction"),
            ("can_view_packaging_instruction", "Can view packaging instruction"),
            ("can_update_packaging_instruction", "Can update packaging instruction"),
            ("can_delete_packaging_instruction", "Can delete packaging instruction"),
        ]

    def __str__(self):
        return self.name

class BillOfMaterials(models.Model):
    product = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit_cost = models.FloatField()
    total_cost = models.FloatField()

    class Meta:
        permissions = [
            ("can_create_bom", "Can create BOM"),
            ("can_view_bom", "Can view BOM"),
            ("can_update_bom", "Can update BOM"),
            ("can_delete_bom", "Can delete BOM"),
        ]

    def __str__(self):
        return f"BOM for {self.product.name}"

class WorkOrders(models.Model):
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_to = models.CharField(max_length=100)
    priority = models.CharField(max_length=100)

    class Meta:
        permissions = [
            ("can_create_work_order", "Can create work order"),
            ("can_view_work_order", "Can view work order"),
            ("can_update_work_order", "Can update work order"),
            ("can_delete_work_order", "Can delete work order"),
        ]

    def __str__(self):
        return f"Work Order {self.id} - {self.status}"
    
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class SalesOrder1(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    packaging_types = models.ManyToManyField('PackagingTypes', blank=True)
    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return self.order_number
  



class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, default="Unknown Contact")
    phone = models.CharField(max_length=15, default="000-000-0000")
    email = models.EmailField(unique=True, default="unknown@example.com")
    packaging_materials = models.ManyToManyField('PackagingMaterials', blank=True)

    def __str__(self):
        return self.name

class SalesRecord(models.Model):
    order_number = models.CharField(max_length=50)
    package = models.ForeignKey('PackagingTypes', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20, default="Pending")
    delivery_date = models.DateTimeField(null=True, blank=True)
    item = models.ForeignKey('Items', on_delete=models.CASCADE, null=True, blank=True)  

    def __str__(self):
        return f"Order {self.order_number} - {self.package.name} x {self.quantity}"
