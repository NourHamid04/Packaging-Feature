import pytest
from django.utils import timezone
from inventory.models import PackagingMaterials, Warehouse, PackagingTypes, UnitsOfMeasurement, Items

@pytest.mark.django_db
def test_packaging_material_creation():
    material = PackagingMaterials.objects.create(
        name="Cardboard",
        description="Sturdy cardboard for packaging",
        cost=2.5,
        available_quantity=100.0,
        created_at=timezone.now()
    )
    assert material.name == "Cardboard"
    assert material.description == "Sturdy cardboard for packaging"
    assert material.cost == 2.5
    assert material.available_quantity == 100.0
    assert material.created_at is not None




@pytest.mark.django_db
def test_warehouse_creation():
    warehouse = Warehouse.objects.create(
        code="WH001",
        name="Main Warehouse",
        warehouse_type=1,
        description="Primary storage",
        total_capacity=1000,
        available_capacity=500
    )
    assert warehouse.code == "WH001"
    assert warehouse.name == "Main Warehouse"
    assert warehouse.warehouse_type == 1
    assert warehouse.description == "Primary storage"
    assert warehouse.total_capacity == 1000
    assert warehouse.available_capacity == 500




@pytest.mark.django_db
def test_packaging_type_creation():
    material = PackagingMaterials.objects.create(
        name="Plastic",
        description="Durable plastic",
        cost=1.5,
        available_quantity=200.0,
        created_at=timezone.now()
    )
    packaging_type = PackagingTypes.objects.create(
        name="Bottle",
        description="Plastic bottle",
        weight=0.1,
        volume=1.0,
        length=10.0,
        width=5.0,
        height=20.0,
        material=material,
        cost=0.5,
        quantity=100,
        level="Primary",
        created_at=timezone.now()
    )
    assert packaging_type.name == "Bottle"
    assert packaging_type.description == "Plastic bottle"
    assert packaging_type.weight == 0.1
    assert packaging_type.volume == 1.0
    assert packaging_type.length == 10.0
    assert packaging_type.width == 5.0
    assert packaging_type.height == 20.0
    assert packaging_type.material == material
    assert packaging_type.cost == 0.5
    assert packaging_type.quantity == 100
    assert packaging_type.level == "Primary"


@pytest.mark.django_db
def test_item_creation():
    uom = UnitsOfMeasurement.objects.create(
        name="Kilogram",
        abbreviation="kg"
    )
    material = PackagingMaterials.objects.create(
        name="Plastic",
        description="Durable plastic",
        cost=1.5,
        available_quantity=200.0,
        created_at=timezone.now()
    )
    packaging_type = PackagingTypes.objects.create(
        name="Bottle",
        description="Plastic bottle",
        weight=0.1,
        volume=1.0,
        length=10.0,
        width=5.0,
        height=20.0,
        material=material,
        cost=0.5,
        quantity=100,
        level="Primary",
        created_at=timezone.now()
    )
    warehouse = Warehouse.objects.create(
        code="WH001",
        name="Main Warehouse",
        warehouse_type=1,
        description="Primary storage",
        total_capacity=1000,
        available_capacity=500
    )
    item = Items.objects.create(
        name="Water Bottle",
        description="1L water bottle",
        type="Beverage",
        uom=uom,
        cost=1.0,
        weight=1.0,
        volume=1.0,
        length=10.0,
        width=5.0,
        height=20.0,
        packaging_type=packaging_type,
        stock_quantity=100,
        reorder_level=20,
        warehouse=warehouse
    )
    assert item.name == "Water Bottle"
    assert item.description == "1L water bottle"
    assert item.type == "Beverage"
    assert item.uom == uom
    assert item.cost == 1.0
    assert item.weight == 1.0
    assert item.volume == 1.0
    assert item.length == 10.0
    assert item.width == 5.0
    assert item.height == 20.0
    assert item.packaging_type == packaging_type
    assert item.stock_quantity == 100
    assert item.reorder_level == 20
    assert item.warehouse == warehouse