import csv
import io

from django.core.exceptions import ValidationError

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
            writer.writerow(
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
        proc_file = proc_file.replace("\ufeff", "")
        proc_file = proc_file.replace("\r\n", "\n")
        reader = csv.DictReader(io.StringIO(proc_file))
        try:
            for row in list(reader):
                add_to_inventory(campaign, row)
            return_result = "Formulary uploaded successfully."
        except KeyError as error:
            return_result = f"Heading '{error}' is missing or incorrect."
        except ValidationError as error:
            return_result = f"Data is misformatted: {error}"
        except UnicodeDecodeError as error:
            return_result = "File is encoded incorrectly. You may have uploaded an Excel sheet - Make sure you uploaded a CSV file."
        return return_result
