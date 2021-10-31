import csv

import requests
from main.csvio import add_to_inventory


class InitialInventoryHandler:
    def __init__(self) -> None:
        super().__init__()

    def read(self, upload, campaign):
        return self.__import(upload, campaign)

    def write(self, response, formulary):
        return self.__export(response, formulary)

    @staticmethod
    def __export(response, formulary):
        writer = csv.writer(response)
        writer.writerow(
            [
                "Category",
                "Medication",
                "Form",
                "Strength",
                "Count",
                "Quantity",
                "Initial Quantity",
                "Item Number",
                "Box Number",
                "Expiration Date",
                "Manufacturer",
            ]
        )
        for x in formulary:
            writer.write(
                [
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
                ]
            )
        return response

    @staticmethod
    def __import(upload, campaign):
        csvfile = requests.get(upload.document.url).content
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            add_to_inventory(campaign, row)
