"""
Application-wide functions for interfacing with AWS QLDB.
"""
from pyqldb.driver.qldb_driver import QldbDriver

import os
import json

from django.core.serializers.json import DjangoJSONEncoder

try:
    LEDGER_NAME = os.environ['qldb_name']
except KeyError:
    LEDGER_NAME = "fEMR-OnChain-Test"


# noinspection PyTypeChecker
def create_tables():
    def create_patient_table(transaction_executor):
        statement = 'CREATE TABLE Patient'
        cursor = transaction_executor.execute_statement(statement)
        return len(list(cursor))

    def create_patient_encounter_table(transaction_executor):
        statement = 'CREATE TABLE PatientEncounter'
        cursor = transaction_executor.execute_statement(statement)
        return len(list(cursor))

    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(lambda x: create_patient_table(x))
    qldb_driver.execute_lambda(lambda x: create_patient_encounter_table(x))


# noinspection PyTypeChecker
def create_new_patient(patient: dict):
    """
    Create a new, blank patient record.
    """

    def insert_documents(transaction_executor, p: dict):
        """
        Internal function handling insertion of new patients.
        """
        transaction_executor.execute_statement(
            "INSERT INTO Patient ?", p)

    patient["action"] = "INSERT"
    patient["date_of_birth"] = str(patient["date_of_birth"])
    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(lambda x: insert_documents(x, patient))


# noinspection PyTypeChecker
def update_patient(patient: dict):
    """
    Update a patient with the provided dataset.
    """

    def update_documents(transaction_executor, p: dict):
        """
        Internal function for updating a patient record.
        """
        transaction_executor.execute_statement(
            "INSERT INTO Patient ?", p)

    patient["action"] = "UPDATE"
    patient["date_of_birth"] = str(patient["date_of_birth"])
    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(lambda x: update_documents(x, patient))


# noinspection PyTypeChecker
def get_all_patients():
    """
    Retrieve all patient data
    """

    def read_documents(transaction_executor):
        """
        Internal function used to retrieve all Patient data.
        """
        cursor = transaction_executor.execute_statement(
            "SELECT * FROM Patient")
        return cursor

    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(lambda x: read_documents(x))


# noinspection PyTypeChecker
def create_new_patient_encounter(patient_encounter: dict):
    """
    Create a new, blank patient record.
    """

    def insert_documents(transaction_executor, p: dict):
        """
        Internal function handling insertion of new patients.
        """
        p['diagnoses'] = json.dumps(list(p['diagnoses']), cls=DjangoJSONEncoder)
        p['treatments'] = json.dumps(list(p['treatments']), cls=DjangoJSONEncoder)
        p['chief_complaint'] = json.dumps(list(p['chief_complaint']), cls=DjangoJSONEncoder)
        transaction_executor.execute_statement(
            "INSERT INTO PatientEncounter ?", p)

    patient_encounter["action"] = "INSERT"
    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(
        lambda x: insert_documents(x, patient_encounter))


# noinspection PyTypeChecker
def update_patient_encounter(patient_encounter: dict):
    
    def insert_documents(transaction_executor, p: dict):
        p['diagnoses'] = json.dumps(list(p['diagnoses']), cls=DjangoJSONEncoder)
        p['treatments'] = json.dumps(list(p['treatments']), cls=DjangoJSONEncoder)
        p['chief_complaint'] = json.dumps(list(p['chief_complaint']), cls=DjangoJSONEncoder)
        transaction_executor.execute_statement(
            "INSERT INTO PatientEncounter ?", p)

    patient_encounter["action"] = "UPDATE"
    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(
        lambda x: insert_documents(x, patient_encounter))


# noinspection PyTypeChecker
def get_all_patient_encounters():
    """
    Retrieve all patient data
    """

    def read_documents(transaction_executor):
        """
        Internal function used to retrieve all Patient data.
        """
        cursor = transaction_executor.execute_statement(
            "SELECT * FROM PatientEncounter")
        return cursor

    qldb_driver = QldbDriver(ledger_name=LEDGER_NAME, region_name='us-west-2')
    qldb_driver.execute_lambda(lambda x: read_documents(x))
