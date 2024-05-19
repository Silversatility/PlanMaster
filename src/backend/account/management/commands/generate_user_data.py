import os
import string
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from account.models import User
from cbcommon.mommy_recipes import mobile_numbers_seq
from construction.models import Company, CompanyRole


def set_codes(amount):
    if amount <= 0:
        return

    for i in range(1, amount + 1):
        yield codify(i)


def codify(number):
    letters = string.ascii_lowercase
    base = len(letters)
    s = ''
    n = number
    while n // base > 0:
        s = letters[(n % base)] + s
        n = n//base

    s = letters[(n % base) - 1] + s
    return s


class Command(BaseCommand):
    help = 'Generates a fixture csv file that can be loaded as is, or used by other command to seed users.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sets',
            action='store',
            dest='set_count',
            type=int,
            default=5,
            help='Amount of sets to create'
        )

        parser.add_argument(
            '--fixture',
            action='store_true',
            default=False,
            help='Generate fixture?'
        )

        parser.add_argument(
            '--password',
            action='store',
            default='crewpass',
            help='Password'
        )

        parser.add_argument(
            '--filename',
            action='store',
            default='initial_data',
            help='Filename to use for saving data'
        )

        parser.add_argument(
            '--compact',
            action='store_true',
            default=False,
            help='Minimizes amount of whitespace'
        )

    def handle(self, *args, **options):
        user_data = self.generate_user_fixtures(options['set_count'], options['password'], options['fixture'])
        self.save(user_data, options['filename'], compact=options['compact'])

        self.stdout.write(self.style.SUCCESS('Success!'))

    def generate_user_fixtures(self, set_count, password, is_fixture):
        self.stdout.write(self.style.WARNING('Generating new set of user fixtures'))
        fake = Faker()

        hashed_password = make_password(password)

        fixtures = []

        fixture_fields = {
            "is_active": True,
            "is_staff": False,
            "date_joined": timezone.now()
        }
        contractor_names = [
            'ABC Construction',
            'Beta Crew',
            'Construction Inc.',
            'Daily Work',
            'Excellent Constructors',
        ]

        roles_per_set = {
            'admin': 1,
            'superintendent': 5,
            'builder': 5,
            'subcontractor': 5,
        }

        mobile_numbers = mobile_numbers_seq()
        for index, code in enumerate(set_codes(set_count)):
            contractor_name = contractor_names[index % 5]
            if index >= 5:
                contractor_name = f"{code.upper()} {contractor_name}"
            fixtures.append({
                'model': 'construction.company',
                'fields': {'name': contractor_name, 'type': Company.TYPE_CONTRACTOR},
                'extra': {'set': code}
            })

            for role, role_count in roles_per_set.items():
                for x in range(1, role_count + 1):
                    fields = {
                        "email": f"{role}{x}@{code}.example.com",
                        "mobile_number": next(mobile_numbers),
                        "first_name": fake.first_name(),
                        "last_name": fake.last_name(),
                        "password": hashed_password,
                        "enable_text_notifications": True,
                        "enable_email_notifications": True,
                    }
                    extra = {
                        'type': role,
                        'password': password,
                        'set': code,
                    }

                    if is_fixture:
                        fields.update(fixture_fields)

                    user = {'model': 'account.user', 'fields': fields, 'extra': extra}
                    fixtures.append(user)

                    role_fields = {'company': [contractor_name], 'user': [fields['email']]}
                    if role == 'admin':
                        role_fields['is_admin'] = True
                        role_fields['is_builder'] = True
                    if role == 'builder':
                        role_fields['is_builder'] = True
                    if role == 'superintendent':
                        role_fields['is_superintendent'] = True
                    if role == 'subcontractor':
                        role_fields['is_crew_leader'] = True
                        extra['subcontractor_name'] = ' '.join([fields['first_name'], fields['last_name'], 'Services'])
                    fixtures.append({
                        'model': 'construction.companyrole',
                        'fields': role_fields,
                        'extra': extra,
                    })

        return fixtures

    def save(self, data, filename, compact=False):
        (fname, ext) = os.path.splitext(filename)
        ext = ext or '.json'

        cmd_dir = os.path.dirname(os.path.realpath(__file__))
        fixtures_dir = os.path.realpath(os.path.join(cmd_dir, '../../fixtures'))

        os.makedirs(fixtures_dir, exist_ok=True)

        filename = f"{fname}{ext}"

        if compact:
            json_args = {}
        else:
            json_args = {"indent": 4}

        with open(os.path.join(fixtures_dir, filename), 'w') as fd:
            fd.write(json.dumps(data, **json_args))
