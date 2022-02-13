import csv

import requests
from main.csvio import add_to_inventory


class InitialInventoryHandler:
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
        for item in formulary:
            writer.write(
                [
                    item.category,
                    item.medication,
                    item.form,
                    item.strength,
                    item.count,
                    item.quantity,
                    item.initial_quantity,
                    item.item_number,
                    item.box_number,
                    item.expiration_date,
                    item.manufacturer,
                ]
            )
        return response

    @staticmethod
    def __import(upload, campaign):
        csvfile = requests.get(upload.document.url).content.decode('utf-8')
        reader = csv.reader(csvfile.splitlines(), delimiter=",")
        next(reader)
        for row in reader:
            add_to_inventory(campaign, row)
