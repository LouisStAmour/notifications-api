from sqlalchemy.sql.expression import func

from app import db
from app.dao.dao_utils import transactional, version_class
from app.models import (
    Organisation,
    Domain,
    InvitedOrganisationUser,
    Service,
    User
)


def dao_get_organisations():
    return Organisation.query.order_by(
        Organisation.active.desc(), Organisation.name.asc()
    ).all()


def dao_count_organsations_with_live_services():
    return db.session.query(Organisation.id).join(Organisation.services).filter(
        Service.active.is_(True),
        Service.restricted.is_(False),
        Service.count_as_live.is_(True),
    ).distinct().count()


def dao_get_organisation_services(organisation_id):
    return Organisation.query.filter_by(
        id=organisation_id
    ).one().services


def dao_get_organisation_by_id(organisation_id):
    return Organisation.query.filter_by(id=organisation_id).one()


def dao_get_organisation_by_email_address(email_address):

    email_address = email_address.lower().replace('.gsi.gov.uk', '.gov.uk')

    for domain in Domain.query.order_by(func.char_length(Domain.domain).desc()).all():

        if (
            email_address.endswith("@{}".format(domain.domain)) or
            email_address.endswith(".{}".format(domain.domain))
        ):
            return Organisation.query.filter_by(id=domain.organisation_id).one()

    return None


def dao_get_organisation_by_service_id(service_id):
    return Organisation.query.join(Organisation.services).filter_by(id=service_id).first()


@transactional
def dao_create_organisation(organisation):
    db.session.add(organisation)


@transactional
def dao_update_organisation(organisation_id, **kwargs):

    domains = kwargs.pop('domains', None)

    num_updated = Organisation.query.filter_by(id=organisation_id).update(
        kwargs
    )

    if isinstance(domains, list):

        Domain.query.filter_by(organisation_id=organisation_id).delete()

        db.session.bulk_save_objects([
            Domain(domain=domain.lower(), organisation_id=organisation_id)
            for domain in domains
        ])

    if 'organisation_type' in kwargs:
        organisation = Organisation.query.get(organisation_id)
        if organisation.services:
            _update_org_type_for_organisation_services(organisation)

    return num_updated


@version_class(Service)
def _update_org_type_for_organisation_services(organisation):
    for service in organisation.services:
        service.organisation_type = organisation.organisation_type
        db.session.add(service)


@transactional
@version_class(Service)
def dao_add_service_to_organisation(service, organisation_id):
    organisation = Organisation.query.filter_by(
        id=organisation_id
    ).one()

    organisation.services.append(service)
    service.organisation_type = organisation.organisation_type
    db.session.add(service)


def dao_get_invited_organisation_user(user_id):
    return InvitedOrganisationUser.query.filter_by(id=user_id).one()


def dao_get_users_for_organisation(organisation_id):
    return User.query.filter(
        User.organisations.any(id=organisation_id),
        User.state == 'active'
    ).order_by(User.created_at).all()


@transactional
def dao_add_user_to_organisation(organisation_id, user_id):
    organisation = dao_get_organisation_by_id(organisation_id)
    user = User.query.filter_by(id=user_id).one()
    user.organisations.append(organisation)
    db.session.add(organisation)
    return user
