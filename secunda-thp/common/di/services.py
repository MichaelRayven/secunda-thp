def get_session() -> Session:
    return Session(engine)

def get_organisation_service(session: Session) -> OrganisationService:
    return OrganisationService(OrganisationRepository(session))
