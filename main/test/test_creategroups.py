from main.management.commands.creategroups import Command


def test_command():
    c = Command()
    c.handle()
