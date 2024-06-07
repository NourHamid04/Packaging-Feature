import pytest
import json
from rest_framework.test import APIClient
from inventory.models import PackagingMaterials, PackagingTypes, UnitsOfMeasurement, Warehouse, Items, PackagingInstructions, BillOfMaterials, WorkOrders
from django.utils import timezone
from inventory.schemas import PackagingLevel
from django.test import TestCase, Client
@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_get_units_of_measurement(client):
    UnitsOfMeasurement.objects.create(name="Kilogram", abbreviation="kg")
    UnitsOfMeasurement.objects.create(name="Liter", abbreviation="L")
    url = "/api/units_of_measurement"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# @pytest.mark.django_db
# def test_create_packaging_material(client):
#     url = "/api/packaging_materials"
#     data = {
#         "name": "Cardboard",
#         "description": "Sturdy cardboard for packaging",
#         "cost": 2.5,
#         "available_quantity": 100.0
#     }
#     response = client.post(url, data, format='json')
#     assert response.status_code == 200, response.json()
#     response_data = response.json()
#     assert response_data['name'] == "Cardboard"
#     assert response_data['description'] == "Sturdy cardboard for packaging"
#     assert response_data['cost'] == 2.5
#     assert response_data['available_quantity'] == 100.0


@pytest.mark.django_db
def test_get_packaging_types(client):
    material = PackagingMaterials.objects.create(
        name="Plastic",
        description="Durable plastic",
        cost=1.5,
        available_quantity=200.0,
        created_at=timezone.now()
    )
    PackagingTypes.objects.create(
        name="Box",
        description="Plastic box",
        weight=0.5,
        volume=1.0,
        length=30.0,
        width=30.0,
        height=30.0,
        material=material,
        cost=1.0,
        quantity=50,
        level=PackagingLevel.PRIMARY,
        created_at=timezone.now()
    )
    url = "/api/packaging_types"
    response = client.get(url)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == "Box"
    assert data[0]['description'] == "Plastic box"
@pytest.mark.django_db
def test_validate_barcode(client):
    material = PackagingMaterials.objects.create(
        name="Plastic",
        description="Durable plastic",
        cost=1.5,
        available_quantity=200.0,
        created_at=timezone.now()
    )
    packaging_type = PackagingTypes.objects.create(
        name="Box",
        description="Plastic box",
        weight=0.5,
        volume=1.0,
        length=30.0,
        width=30.0,
        height=30.0,
        material=material,
        cost=1.0,
        quantity=50,
        level=PackagingLevel.PRIMARY,
        created_at=timezone.now()
    )
    barcode_number = f"{packaging_type.id}{1234567890}"
    url = "/api/validate_barcode"
    data = {"barcode_number": barcode_number}
    response = client.post(url, data, format='json')
    assert response.status_code == 200, response.json()
    response_data = response.json()
    assert response_data['valid'] is True
    assert response_data['packaging_type_info']['name'] == "Box"




@pytest.mark.django_db
def test_get_warehouses(client):
    Warehouse.objects.create(
        code="WH001",
        name="Main Warehouse",
        warehouse_type=1,
        description="Primary storage",
        total_capacity=1000,
        available_capacity=500
    )
    url = "/api/warehouses"
    response = client.get(url)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data) == 1
    assert data[0]['code'] == "WH001"
    assert data[0]['name'] == "Main Warehouse"





@pytest.mark.django_db
def test_print_label(client):
    packaging_type = PackagingTypes.objects.create(
        name="Box",
        description="Plastic box",
        weight=0.5,
        volume=1.0,
        length=30.0,
        width=30.0,
        height=30.0,
        material=PackagingMaterials.objects.create(
            name="Plastic",
            description="Durable plastic",
            cost=1.5,
            available_quantity=200.0,
            created_at=timezone.now()
        ),
        cost=1.0,
        quantity=50,
        level=PackagingLevel.PRIMARY,
        created_at=timezone.now()
    )
    url = f"/api/print_label?packaging_type_id={packaging_type.id}&priority=1"
    response = client.post(url)
    assert response.status_code == 200, response.json()
    response_data = response.json()
    assert response_data['message'] == "Label added to printing queue", response_data
    assert response_data['queue_position'] == 1, response_data
