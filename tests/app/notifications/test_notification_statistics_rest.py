import json
from datetime import (date, timedelta)
from flask import url_for
from tests import create_authorization_header
from tests.app.conftest import sample_notification_statistics as create_sample_notification_statistics


def test_get_notification_statistics(
    notify_api,
    notify_db,
    notify_db_session,
    sample_template,
    sample_email_template
):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:

            path = '/service/{}/notifications-statistics'.format(sample_email_template.service)

            auth_header = create_authorization_header(
                service_id=sample_email_template.service_id)

            response = client.get(path, headers=[auth_header])
            assert response.status_code == 404

            stats = json.loads(response.get_data(as_text=True))
            assert stats['result'] == 'error'
            assert stats['message'] == 'No result found'


def test_get_week_aggregate_statistics(notify_api,
                                       notify_db,
                                       notify_db_session,
                                       sample_service):
    with notify_api.test_request_context():
        sample_notification_statistics = create_sample_notification_statistics(
            notify_db,
            notify_db_session,
            day=date(date.today().year, 4, 1))
        with notify_api.test_client() as client:
            endpoint = url_for(
                'notifications-statistics.get_notification_statistics_for_service_seven_day_aggregate',
                service_id=sample_service.id)
            auth_header = create_authorization_header(
                service_id=sample_service.id)

            resp = client.get(endpoint, headers=[auth_header])
            assert resp.status_code == 200
            json_resp = json.loads(resp.get_data(as_text=True))
            week_len_index = len(json_resp['data']) - 1
            assert json_resp['data'][week_len_index]['emails_requested'] == 2
            assert json_resp['data'][week_len_index]['sms_requested'] == 2
            assert json_resp['data'][week_len_index]['week_start'] == date(date.today().year, 4, 1).strftime('%Y-%m-%d')
            assert json_resp['data'][week_len_index]['week_end'] == date(date.today().year, 4, 7).strftime('%Y-%m-%d')


def test_get_week_aggregate_statistics_date_from(notify_api,
                                                 notify_db,
                                                 notify_db_session,
                                                 sample_service):
    with notify_api.test_request_context():
        sample_notification_statistics = create_sample_notification_statistics(
            notify_db,
            notify_db_session,
            day=date(date.today().year, 4, 1))
        date_from_str = date(date.today().year, 4, 1).strftime('%Y-%m-%d')
        with notify_api.test_client() as client:
            endpoint = url_for(
                'notifications-statistics.get_notification_statistics_for_service_seven_day_aggregate',
                service_id=sample_service.id,
                date_from=date_from_str)
            auth_header = create_authorization_header(
                service_id=sample_service.id)

            resp = client.get(endpoint, headers=[auth_header])
            assert resp.status_code == 200
            json_resp = json.loads(resp.get_data(as_text=True))
            week_len_index = len(json_resp['data']) - 1
            assert json_resp['data'][week_len_index]['emails_requested'] == 2
            assert json_resp['data'][week_len_index]['sms_requested'] == 2
            assert json_resp['data'][week_len_index]['week_start'] == date_from_str
            assert json_resp['data'][week_len_index]['week_end'] == date(date.today().year, 4, 7).strftime('%Y-%m-%d')


def test_get_week_aggregate_statistics_date_in_future(notify_api,
                                                      notify_db,
                                                      notify_db_session,
                                                      sample_service):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            endpoint = url_for(
                'notifications-statistics.get_notification_statistics_for_service_seven_day_aggregate',
                service_id=sample_service.id,
                date_from=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'))
            auth_header = create_authorization_header(
                service_id=sample_service.id)

            resp = client.get(endpoint, headers=[auth_header])
            assert resp.status_code == 400
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['result'] == 'error'
            assert json_resp['message']['date_from'][0] == 'Date cannot be in the future'


def test_get_week_aggregate_statistics_invalid_week_count(notify_api,
                                                          notify_db,
                                                          notify_db_session,
                                                          sample_service):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            endpoint = url_for(
                'notifications-statistics.get_notification_statistics_for_service_seven_day_aggregate',
                service_id=sample_service.id,
                week_count=-1)
            auth_header = create_authorization_header(
                service_id=sample_service.id)

            resp = client.get(endpoint, headers=[auth_header])
            assert resp.status_code == 400
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['result'] == 'error'
            assert json_resp['message']['week_count'][0] == 'Not a positive integer'