"""
AddedInventoryHandler and required imports.
"""
import csv

import requests
from main.csvio import add_to_inventory


class AddedInventoryHandler:
    """
    Implements CSVHandler and adds inventory to supplies that already existed in the formulary.
    """

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
                "Strength Unit",
                "Count",
                "Count Unit",
                "Quantity",
                "Amount",
                "Quantity Unit",
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
                    item.strength_unit,
                    item.count,
                    item.count_unit,
                    item.quantity,
                    item.amount,
                    item.quantity_unit,
                    item.initial_quantity,
                    item.item_number,
                    item.box_number,
                    item.expiration_date,
                    item.manufacturer,
                ]
            )
        return response

    @staticmethod
    def __import(csvfile, campaign):
        proc_file = csvfile.read().decode("utf-8")
        lines = proc_file.split("\n")
        lines.pop(0)
        for row in lines:
            add_to_inventory(campaign, row.split(","))
