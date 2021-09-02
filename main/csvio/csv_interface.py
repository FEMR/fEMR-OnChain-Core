import csv


class CSVHandler(object):
    def __init__(self) -> None:
        super().__init__()
        pass

    def read(self, upload, campaign):
        return self.__import(upload, campaign)

    def write(self, response, formulary):
        return self.__export(response, formulary)
    
    def __import(self, upload, campaign):
        pass

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