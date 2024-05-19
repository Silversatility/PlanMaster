import os
import random
from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from faker import Faker
from model_mommy.recipe import Recipe, foreign_key, related, seq

from account.models import AuthToken
from construction import models

SEEDER_PASSWORD = 'crewpass'
HASHED_PASSWORD = make_password(SEEDER_PASSWORD)
SUBDIVISION_NAMES = []
with open(os.path.join(os.path.dirname(__file__), 'management/commands/subdivisions.txt')) as fd:
    SUBDIVISION_NAMES = fd.read().splitlines()
UserModel = get_user_model()
fake = Faker()


def random_user():
    return random.choice([subcontractor, contractor_admin, superintendent, builder]).user


def emails_seq():
    counter = 1
    while True:
        yield f'test{counter}@example.com'
        counter += 1


def mobile_numbers_seq():
    for suffix in range(100, 1000):
        yield f'(202) 555-0{suffix}'


user = Recipe(
    UserModel,
    email=emails_seq(),
    mobile_number=mobile_numbers_seq(),
    first_name=fake.first_name,
    last_name=fake.last_name,
    password=HASHED_PASSWORD,
)
auth_token = Recipe(AuthToken)

contractor = Recipe(
    models.Company,
    name=fake.company,
    type=models.Company.TYPE_CONTRACTOR,
    current_plan=models.Company.PLAN_PRO,
    current_balance=10,
    billing_address=lambda: fake.street_address()[:100],
    city=lambda: fake.city()[:20],
    state=lambda: fake.state_abbr(include_territories=False),
    zip=lambda: fake.postalcode()[:10],
    saturday=True,
    sunday=True,
)
subcontractor_co = contractor.extend(type=models.Company.TYPE_SUBCONTRACTOR)

_company_role = Recipe(models.CompanyRole, company=foreign_key(contractor), user=lambda: user.make())
contractor_admin = _company_role.extend(is_admin=True, is_builder=True)
subcontractor = _company_role.extend(
    company=foreign_key(subcontractor_co), is_admin=True, is_crew_leader=True, connections=related(contractor_admin)
)
superintendent = _company_role.extend(is_superintendent=True)
builder = _company_role.extend(is_builder=True)

subdivision = Recipe(models.Subdivision, name=lambda: random.choice(SUBDIVISION_NAMES), company=foreign_key(contractor))
job = Recipe(
    models.Job,
    street_address=lambda: fake.street_address()[:100],
    city=lambda: fake.city()[:20],
    state=lambda: fake.state_abbr(include_territories=False),
    zip=lambda: fake.postalcode()[:10],
    lot_number=lambda: fake.secondary_address()[:10],
    subdivision=foreign_key(subdivision),
    created_by=foreign_key(contractor),
    owner=foreign_key(contractor),
    builder=foreign_key(builder),
    subcontractor=foreign_key(subcontractor),
    superintendent=foreign_key(superintendent),
    roles=related(subcontractor, superintendent, builder),
)

category = Recipe(models.TaskCategory, contractor=foreign_key(contractor), name=fake.catch_phrase)
subcategory = Recipe(models.TaskSubCategory, category=foreign_key(category), name=fake.catch_phrase)
task = Recipe(
    models.Task,
    name=fake.catch_phrase,
    category=foreign_key(category),
    subcategory=foreign_key(subcategory),
    job=foreign_key(job),
    start_date=seq(date.today(), timedelta(days=1)),
    end_date=seq(date.today() + timedelta(days=random.randint(1, 5)), timedelta(days=1)),
    start_time=time(9),
    end_time=time(17),
    subcontractor=foreign_key(subcontractor),
    superintendent=foreign_key(superintendent),
    builder=foreign_key(builder),
)
participation = Recipe(models.Participation, task=foreign_key(task), user=lambda: user.make())
contact = Recipe(
    models.Contact, email=fake.email, mobile_number=mobile_numbers_seq(), name=fake.name, author=lambda: user.make())
note = Recipe(models.Note, text=fake.paragraph, author=lambda: user.make())
document = Recipe(models.Document, author=lambda: user.make(), _create_files=True)
message = Recipe(models.Message, task=foreign_key(task), user=lambda: user.make())
