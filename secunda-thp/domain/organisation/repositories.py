class OrganisationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_organizations_by_building(self, building: int) -> list[Organization]:
        return self.session.query(Organization).filter(Organization.building_id == building).all()
    
    def get_organization_by_id(self, gid: int) -> Organization:
        return self.session.query(Organization).get(gid)
    
    def get_organizations_by_name(self, name: str) -> list[Organization]:
        return self.session.query(Organization).filter(Organization.name.op('%')(name)).all()
