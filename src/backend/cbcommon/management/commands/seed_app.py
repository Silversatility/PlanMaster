import json
import os
import random
from collections import defaultdict
from datetime import date, timedelta
from pprint import pformat

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from faker import Faker

from construction import models as construction_models
from ... import mommy_recipes

UserModel = get_user_model()
fake = Faker()

CATEGORY_NAMES = (
    ('Exterior finishes', (
        ('Concrete', (
            'Driveway install',
            'Sidewalk install',
        )),
        ('Exterior trim', (
            'Siding install',
        )),
        ('Gutters', (
            'Gutter install',
        )),
        ('Masonry', (
            'Brick install',
            'Stucco install',
        )),
        ('Painting', (
            'Exterior painting',
        )),
    )),
    ('Foundation', (
        ('Foundation', (
            'Foundation layout',
            'Foundation forming',
            'Termite treatment',
            'Foundation inspection',
            'Foundation casting',
        )),
    )),
    ('Framing', (
        ('Framing', (
            'Framing',
            'Framing punch-out',
            'Window & door installation',
            'Framing inspection',
        )),
    )),
    ('General conditions', (
        ('Foundation', (
            'Surveying',
        )),
    )),
    ('Hardscaping', (
        ('Hardscaping', (
            'Patio install',
            'Fence install',
        )),
    )),
    ('Insulation and Drywall', (
        ('Drywall', (
            'Drywall hanging',
            'Drywall finishing',
            'Drywall sanding',
            'Drywall priming',
        )),
        ('Insulation', (
            'Insulation install- walls',
            'Insulation install- attic',
        )),
    )),
    ('Interior finishes', (
        ('Appliances', (
            'Appliance install',
        )),
        ('Cabinets', (
            'Cabinet install',
        )),
        ('Countertops', (
            'Countertop templating',
            'Countertop install',
        )),
        ('Flooring', (
            'Ceramic floor tile install',
            'Hardwood install',
            'Carpet install',
        )),
        ('Interior trim', (
            'Interior trim install',
            'Door hardware install',
            'Interior trim punch-out',
        )),
        ('Painting', (
            'Painting 1st point-up',
            'Painting 1st roll out',
            'Painting 2nd point-up',
            'Painting 2nd roll out',
            'Painting punch out',
        )),
        ('Tub & shower surrounds', (
            'Shower tile install',
            'Cultured marble install',
        )),
    )),
    ('Landscaping', (
        ('Landscaping', (
            'Irrigation install',
            'Landscaping install',
            'Sod install',
        )),
    )),
    ('Mechanical, Electrical, Plumbing', (
        ('Electrical', (
            'Electric temporary',
            'Electric rough-in',
            'Electric service',
            'Electric devices',
            'Electric finish',
            'Electrical rough inspection',
            'Electrical finish inspection',
        )),
        ('HVAC', (
            'HVAC rough',
            'HVAC finish',
            'HVAC rough inspection',
            'HVAC finish inspection',
        )),
        ('Plumbing', (
            'Plumbing underground',
            'Plumbing top-out',
            'Plumbing finish',
            'Plumbing rough inspection',
            'Plumbing finish inspection',
        )),
    )),
    ('Sitework', (
        ('Grading', (
            'Backfill',
            'Rough grading',
            'Finish grading',
        )),
        ('Plumbing', (
            'Water & sewer line install',
        )),
    )),
)


def custom_get_or_create(model, **kwargs):
    params = dict(kwargs)
    defaults = params.pop('defaults', {})
    if 'user' in params:
        params['user'] = UserModel.objects.get(email=params['user'][0])
    if 'company' in params:
        params['company'] = construction_models.Company.objects.get(name=params['company'][0])

    try:
        return model.objects.get(**params), False
    except model.DoesNotExist:
        params.update(defaults)
        return model.objects.create(**params), True


class Command(BaseCommand):
    help = 'Populate models with fake data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            action='store',
            default='initial_data',
            help='Filename to use for saving data'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Seed the superuser only'
        )

    def handle(self, *args, **options):
        self.seed_superuser()
        if not options.get('superuser'):
            self.seed_users_from_fixture(options['filename'])
            self.seed_other_models()
        self.stdout.write(self.style.SUCCESS('All done!'))

    def seed_superuser(self):
        self.stdout.write(self.style.WARNING('Seeding superuser...'))
        superuser = UserModel.objects.get_or_create(email='root@example.com', defaults={
            'first_name': 'Superuser',
            'last_name': 'Test',
            'password': mommy_recipes.HASHED_PASSWORD,
            'is_superuser': True,
            'is_staff': True,
        })[0]
        self.stdout.write('- {}: {} / {}'.format(
            superuser.get_full_name(), superuser.email, mommy_recipes.SEEDER_PASSWORD))
        self.stdout.write(self.style.SUCCESS('SUCCESS: Seeded superuser!'))

    def seed_users_from_fixture(self, filename):
        fixtures_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../../account/fixtures'))
        fname, ext = os.path.splitext(filename)
        filename = fname + (ext or '.json')
        path = os.path.join(fixtures_dir, filename)
        self.stdout.write(self.style.WARNING('Seeding users from fixture: {}...'.format(path)))

        data = []
        with open(path) as fd:
            data = json.load(fd)

        groups = defaultdict(lambda: defaultdict(list))
        for entry in data:
            if entry['model'] == 'construction.company':
                name = entry['fields'].pop('name')
                defaults = dict(entry['fields'])
                defaults['current_plan'] = construction_models.Company.PLAN_PRO
                defaults['current_balance'] = 10
                defaults['billing_address'] = fake.street_address()
                defaults['city'] = fake.city()[:20]
                defaults['state'] = fake.state_abbr(include_territories=False)
                defaults['zip'] = fake.postalcode()[:10]
                company, _ = custom_get_or_create(
                    construction_models.Company,
                    name=name,
                    type=construction_models.Company.TYPE_CONTRACTOR,
                    defaults=defaults,
                )
                groups[entry['extra']['set']]['contractor'] = company
            elif entry['model'] == 'account.user':
                email = entry['fields'].pop('email')
                custom_get_or_create(UserModel, email=email, defaults=entry['fields'])
            elif entry['model'] == 'construction.companyrole':
                if entry['extra'].get('subcontractor_name'):
                    own_role, _ = custom_get_or_create(
                        construction_models.CompanyRole, is_admin=True, **entry['fields']
                    )
                    contractor = own_role.company
                    own_role.company = construction_models.Company.objects.create(
                        name=entry['extra']['subcontractor_name'],
                        type=construction_models.Company.TYPE_SUBCONTRACTOR,
                        billing_address=contractor.billing_address,
                        address_line_2=contractor.address_line_2,
                        city=contractor.city,
                        state=contractor.state,
                        zip=contractor.zip,
                    )
                    own_role.save()
                    for other in contractor.roles.order_by('?')[:1]:
                        own_role.connections.add(other)
                    groups[entry['extra']['set']]['subcontractor'].append(own_role)
                else:
                    company_role, _ = custom_get_or_create(construction_models.CompanyRole, **entry['fields'])
                    if entry['fields'].get('is_admin'):
                        groups[entry['extra']['set']]['contractor_admin'].append(company_role)
                    elif entry['fields'].get('is_builder'):
                        groups[entry['extra']['set']]['builder'].append(company_role)
                    elif entry['fields'].get('is_superintendent'):
                        groups[entry['extra']['set']]['superintendent'].append(company_role)

        self.groups = groups
        self.stdout.write(pformat(self.groups))
        self.stdout.write(self.style.SUCCESS('SUCCESS: Seeded {} groups of users!'.format(len(self.groups))))

    def generate_start_date(self):
        start_date = date.today()
        while start_date.strftime('%w') in ['6', '0']:
            start_date = start_date + timedelta(days=1)
        return start_date

    def generate_end_date(self):
        end_date = self.generate_start_date() + timedelta(random.randint(1, 6))
        while end_date.strftime('%w') in ['6', '0']:
            end_date = end_date + timedelta(days=1)
        return end_date

    def seed_other_models(self):
        self.stdout.write(self.style.WARNING('Seeding jobs/tasks for {} groups of users...'.format(len(self.groups))))
        for group in self.groups.values():
            contractor = random.choice(group['contractor_admin']).company

            # Pre-load all Categories and Subcategories
            for category_name, subcategory_names in CATEGORY_NAMES:
                category, _ = construction_models.TaskCategory.objects.get_or_create(
                    contractor=contractor, name=category_name)
                for subcategory_name, _ in subcategory_names:
                    construction_models.TaskSubCategory.objects.get_or_create(
                        category=category, name=subcategory_name)

            for _ in range(3):  # 3 Jobs per contractor per run
                builder = random.choice(group['builder'])
                subcontractor = random.choice(group['subcontractor'])
                superintendent = random.choice(group['superintendent'])
                job = mommy_recipes.job.make(
                    subdivision=mommy_recipes.subdivision.make(company=contractor),
                    created_by=contractor,
                    owner=contractor,
                    builder=builder,
                    subcontractor=subcontractor,
                    superintendent=superintendent,
                    roles=[subcontractor, superintendent, builder],
                )

                start_date = date.today()
                for category_name, subcategory_names in random.sample(CATEGORY_NAMES, 5):
                    category = construction_models.TaskCategory.objects.get(contractor=contractor, name=category_name)
                    subcategory_groups = random.sample(subcategory_names, min(2, len(subcategory_names)))
                    for subcategory_name, task_names in subcategory_groups:
                        subcategory = construction_models.TaskSubCategory.objects.get(
                            category=category, name=subcategory_name)
                        for task_name in random.sample(task_names, min(2, len(task_names))):
                            task = mommy_recipes.task.make(
                                category=category,
                                subcategory=subcategory,
                                job=job,
                                name=task_name,
                                subcontractor=random.choice(group['subcontractor']),
                                superintendent=random.choice(group['superintendent']),
                                builder=random.choice(group['builder']),
                                start_date=self.generate_start_date(),
                                end_date=self.generate_end_date(),
                            )
                            job.roles.add(task.subcontractor, task.superintendent, task.builder)
                            task.duration = task.get_duration()
                            task.save()
                            task.make_participants()
                            for role in [task.subcontractor, task.superintendent, task.builder]:
                                mommy_recipes.contact.make(task=task, author=role.user)
                                mommy_recipes.note.make(task=task, author=role.user)
                                mommy_recipes.document.make(task=task, author=role.user, _create_files=True)
                            task.reminders.create(reminder_days=1)

                            start_date += timedelta(1)
                mommy_recipes.contact.make(job=job, author=random.choice(group['contractor_admin']).user)
                mommy_recipes.note.make(job=job, author=random.choice(group['contractor_admin']).user)
                mommy_recipes.document.make(job=job, author=random.choice(group['contractor_admin']).user)

                self.stdout.write('- Seeded job: {}'.format(job))
        self.stdout.write(self.style.SUCCESS('SUCCESS: Seeded jobs and other models!'))
