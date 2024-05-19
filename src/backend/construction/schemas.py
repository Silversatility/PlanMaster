from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import AutoSchema


class CalendarAutoSchema(AutoSchema):
    def get_filter_fields(self, path, method):
        if path == '/api/v1/user/calendar/':
            self.view.action = 'list'
            return self.get_filter_fields('/api/v1/user/', 'GET') + [
                coreapi.Field(
                    'week',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Week in YYYY-WW format for filtering tasks (e.g. 2018-30)'),
                ),
                coreapi.Field(
                    'month',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Month in YYYY-MM format for filtering tasks (e.g. 2018-08)'),
                ),
                coreapi.Field(
                    'start_date',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Start date for filtering tasks (e.g. 2018-08-07)'),
                ),
                coreapi.Field(
                    'end_date',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='End date for filtering tasks (e.g. 2018-09-07)'),
                ),
                coreapi.Field(
                    'task-search',
                    required=False,
                    location='query',
                    schema=coreschema.String(
                        description='Terms to search tasks by Task Name, Job Street Address or Subdivision Name',
                    ),
                ),
                coreapi.Field(
                    'task-status',
                    required=False,
                    location='query',
                    schema=coreschema.Integer(
                        description='Filter tasks by status: Tentative = 1, Pending = 2, Scheduled = 3',
                    ),
                ),
            ]
        if path == '/api/v1/job/calendar/':
            self.view.action = 'list'
            return self.get_filter_fields('/api/v1/job/', 'GET') + [
                coreapi.Field(
                    'week',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Week in YYYY-WW format for filtering tasks (e.g. 2018-30)'),
                ),
                coreapi.Field(
                    'month',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Month in YYYY-MM format for filtering tasks (e.g. 2018-08)'),
                ),
                coreapi.Field(
                    'start_date',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Start date for filtering tasks (e.g. 2018-08-07)'),
                ),
                coreapi.Field(
                    'end_date',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='End date for filtering tasks (e.g. 2018-09-07)'),
                ),
                coreapi.Field(
                    'task-search',
                    required=False,
                    location='query',
                    schema=coreschema.String(
                        description='Terms to search tasks by Task Name, Job Street Address or Subdivision Name',
                    ),
                ),
                coreapi.Field(
                    'task-status',
                    required=False,
                    location='query',
                    schema=coreschema.Integer(
                        description='Filter tasks by status: Tentative = 1, Pending = 2, Scheduled = 3',
                    ),
                ),
            ]
        if path == '/api/v1/task/calendar/':
            self.view.action = 'list'
            return self.get_filter_fields('/api/v1/task/', method) + [
                coreapi.Field(
                    'week',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Week in YYYY-WW format for filtering tasks (e.g. 2018-30)'),
                ),
                coreapi.Field(
                    'month',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Month in YYYY-MM format for filtering tasks (e.g. 2018-08)'),
                ),
                coreapi.Field(
                    'start_date',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='Start date for filtering tasks (e.g. 2018-08-07)'),
                ),
                coreapi.Field(
                    'end_date',
                    required=False,
                    location='query',
                    schema=coreschema.String(description='End date for filtering tasks (e.g. 2018-09-07)'),
                ),
            ]
        return super().get_filter_fields(path, method)
