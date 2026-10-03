from django.core.management import BaseCommand
from account.tasks import change_password_task

class Command(BaseCommand):
    help='change password'
    def add_arguments(self, parser):
        parser.add_argument('-e', nargs='+', type=str)
        parser.add_argument('-p', nargs='+', type=str)
    def handle(self, *args, **options):
        if options['e'] and options['p']:
            change_password_task.delay(options['e'], options['p'])
            return (f'If your information is correct, your password has been changed.\n'
                    f'  - Email : {options["e"][0]}\n'
                    f'  - Password : {options["p"][0]}')
        return 'arguments is missed'