from main.management.commands.adminoptions import Command


def test_command():
    c = Command()
    c.handle()
