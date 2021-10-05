import csv
from main.models import InventoryCategory, InventoryEntry, InventoryForm, Manufacturer, Medication
from main.csvio.csv_interface import CSVHandler


class AddedInventoryHandler(CSVHandler):
    def __init__(self) -> None:
        super().__init__()
    
    def read(self, upload, campaign):
        return self.__import(upload, campaign)
    
    def write(self, response, formulary):
        return self.__export(response, formulary)
    
    def __export(self, response, formulary):
        writer = csv.writer(response)
        writer.writerow(["Category", "Medication", "Form", "Strength", "Count", "Quantity",
                            "Initial Quantity", "Item Number", "Box Number", "Expiration Date", "Manufacturer"])
        for x in formulary:
            writer.write([
                x.category,
                x.medication,
                x.form,
                x.strength,
                x.count,
                x.quantity,
                x.initial_quantity,
                x.item_number,
                x.box_number,
                x.expiration_date,
                x.manufacturer,
            ])
        return response

    def __import(self, upload, campaign):
        with open(upload.document.url) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                campaign.inventory.entries.add(
                    InventoryEntry.objects.update_or_create(
                        category=InventoryCategory.objects.get_or_create(
                            name=row[0])[0],
                        medication=Medication.objects.get_or_create(
                            text=row[1])[0],
                        form=InventoryForm.objects.get_or_create(
                            name=row[2]),
                        strength=row[3],
                        count=row[4],
                        quantity=row[5],
                        initial_quantity=row[6],
                        item_number=row[7],
                        box_number=row[8],
                        expiration_date=row[9],
                        manufacturer=Manufacturer.objects.get_or_create(
                            name=row[10])[0]
                    )
                )