from app.dao.letter_branding_dao import (
    dao_get_letter_branding_by_domain,
    dao_get_all_letter_branding,
    dao_create_letter_branding,
    dao_update_letter_branding
)
from app.models import LetterBranding
from tests.app.db import create_letter_branding


def test_dao_get_letter_branding_by_domain_returns_none_if_no_matching_domains(notify_db_session):
    result = dao_get_letter_branding_by_domain(domain="test.domain")
    assert not result


def test_dao_get_letter_branding_by_domain_returns_correct_brand_for_domain(notify_db_session):
    create_letter_branding(domain='gov.uk')
    test_domain_branding = create_letter_branding(
        name='test domain', filename='test-domain', domain='test.domain'
    )
    result = dao_get_letter_branding_by_domain(domain='test.domain')
    result == test_domain_branding


def test_dao_get_all_letter_branding(notify_db_session):
    hm_gov = create_letter_branding()
    test_domain = create_letter_branding(
        name='test domain', filename='test-domain', domain='test.domain'
    )

    results = dao_get_all_letter_branding()

    assert hm_gov in results
    assert test_domain in results
    assert len(results) == 2


def test_dao_get_all_letter_branding_returns_empty_list_if_no_brands_exist(notify_db):
    assert dao_get_all_letter_branding() == []


def test_dao_create_letter_branding(notify_db_session):
    data = {
        'name': 'test-logo',
        'domain': 'test.co.uk',
        'filename': 'test-logo'
    }
    assert LetterBranding.query.count() == 0
    dao_create_letter_branding(LetterBranding(**data))

    assert LetterBranding.query.count() == 1

    new_letter_branding = LetterBranding.query.first()
    assert new_letter_branding.name == data['name']
    assert new_letter_branding.domain == data['domain']
    assert new_letter_branding.filename == data['name']


def test_dao_update_letter_branding(notify_db_session):
    create_letter_branding(name='original')
    letter_branding = LetterBranding.query.first()
    assert letter_branding.name == 'original'
    dao_update_letter_branding(letter_branding.id, name='new name')
    assert LetterBranding.query.first().name == 'new name'
