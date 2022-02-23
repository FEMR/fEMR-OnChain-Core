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
            category=InventoryCategory.objects.get_or_create(name=row["Category"])[0],
            medication=Medication.objects.get_or_create(text=row["Medication"])[0],
            form=InventoryForm.objects.get_or_create(name=row["Form"])[0],
            strength=row["Strength"],
            strength_unit=row["Strength Unit"],
            count=row["Count"],
            count_unit=row["Count Unit"],
            quantity=row["Quantity"],
            quantity_unit=row["Quantity Unit"],
            initial_quantity=row["Initial quantity"],
            item_number=row["Item number"],
            box_number=row["Box number"],
            expiration_date=row["Expiration date"],
            manufacturer=Manufacturer.objects.get_or_create(name=row["Manufacturer"])[
                0
            ],
        )
    )
    campaign.save()
