"""
Management command to verify QLDB ledger connectivity and table existence.
Usage: python manage.py check_qldb
"""
import os
from django.core.management.base import BaseCommand

try:
    from pyqldb.driver.qldb_driver import QldbDriver
except ImportError:
    QldbDriver = None


class Command(BaseCommand):
    help = "Check QLDB ledger connectivity and verify Patient/PatientEncounter tables exist."

    def handle(self, *args, **options):
        if os.environ.get("QLDB_ENABLED") != "TRUE":
            self.stdout.write(self.style.WARNING(
                "QLDB_ENABLED is not set to TRUE — skipping check."
            ))
            return

        if QldbDriver is None:
            self.stderr.write(self.style.ERROR(
                "pyqldb is not installed. Run: pip install pyqldb"
            ))
            return

        ledger_name = os.environ.get("qldb_name", "fEMR-OnChain-Test")
        self.stdout.write(f"Connecting to ledger: {ledger_name} (us-west-2)...")

        try:
            driver = QldbDriver(ledger_name=ledger_name, region_name="us-west-2")

            def list_tables(txn):
                cursor = txn.execute_statement("SELECT name FROM information_schema.user_tables")
                return [row["name"] for row in cursor]

            tables = driver.execute_lambda(list_tables)

            self.stdout.write(self.style.SUCCESS(f"Connected. Tables found: {tables}"))

            for expected in ["Patient", "PatientEncounter"]:
                if expected in tables:
                    self.stdout.write(self.style.SUCCESS(f"  [OK] {expected}"))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"  [MISSING] {expected} — run 'python manage.py createadmin' to create tables."
                    ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to connect to QLDB: {e}"))
