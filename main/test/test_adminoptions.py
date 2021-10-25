from main.management.commands.adminoptions import Command, OPTIONS


def test_command():
    c = Command()
    c.handle()
