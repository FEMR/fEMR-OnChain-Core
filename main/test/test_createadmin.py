from main.management.commands.createadmin import Command as AdminCommand
from main.management.commands.creategroups import Command as GroupCommand
from main.models import fEMRUser


def test_command():
    a = GroupCommand()
    a.handle()
    c = AdminCommand()
    c.handle()
