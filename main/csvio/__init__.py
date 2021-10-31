from main.models import (
    InventoryCategory,
    InventoryEntry,
    InventoryForm,
    Manufacturer,
    Medication,
)


def add_to_inventory(campaign, row):
    campaign.inventory.entries.add(
        InventoryEntry.objects.create(
            category=InventoryCategory.objects.get_or_create(name=row[0])[0],
            medication=Medication.objects.get_or_create(text=row[1])[0],
            form=InventoryForm.objects.get_or_create(name=row[2])[0],
            strength=row[3],
            count=row[4],
            quantity=row[5],
            initial_quantity=row[6],
            item_number=row[7],
            box_number=row[8],
            expiration_date=row[9],
            manufacturer=Manufacturer.objects.get_or_create(name=row[10])[0],
        )
    )
