"""Script to populate database with test data.

Includes nested activities, organizations, and buildings.
"""

from sqlalchemy.orm import Session

from db import get_session
from models import Activity, Building, Organization, OrganizationPhone


def create_activities(session: Session) -> dict[str, Activity]:
    """Create nested activities with parent-child relationships."""
    activities = {}

    # Top-level activities
    activities['Services'] = Activity(name='Services', parent_id=None)
    activities['Retail'] = Activity(name='Retail', parent_id=None)
    activities['Food'] = Activity(name='Food & Dining', parent_id=None)
    activities['Healthcare'] = Activity(name='Healthcare', parent_id=None)
    activities['Education'] = Activity(name='Education', parent_id=None)

    session.add_all(activities.values())
    session.flush()

    # Second level activities
    activities['Beauty'] = Activity(
        name='Beauty & Personal Care',
        parent_id=activities['Services'].id,
    )
    activities['Auto'] = Activity(
        name='Automotive Services',
        parent_id=activities['Services'].id,
    )
    activities['Legal'] = Activity(
        name='Legal Services',
        parent_id=activities['Services'].id,
    )
    activities['IT'] = Activity(
        name='IT Services',
        parent_id=activities['Services'].id,
    )

    activities['Supermarket'] = Activity(
        name='Supermarket',
        parent_id=activities['Retail'].id,
    )
    activities['Clothing'] = Activity(
        name='Clothing Store',
        parent_id=activities['Retail'].id,
    )
    activities['Electronics'] = Activity(
        name='Electronics Store',
        parent_id=activities['Retail'].id,
    )

    activities['Restaurant'] = Activity(
        name='Restaurant',
        parent_id=activities['Food'].id,
    )
    activities['Cafe'] = Activity(
        name='Cafe',
        parent_id=activities['Food'].id,
    )
    activities['FastFood'] = Activity(
        name='Fast Food',
        parent_id=activities['Food'].id,
    )

    activities['Hospital'] = Activity(
        name='Hospital',
        parent_id=activities['Healthcare'].id,
    )
    activities['Pharmacy'] = Activity(
        name='Pharmacy',
        parent_id=activities['Healthcare'].id,
    )
    activities['Dentist'] = Activity(
        name='Dental Clinic',
        parent_id=activities['Healthcare'].id,
    )

    activities['School'] = Activity(
        name='School',
        parent_id=activities['Education'].id,
    )
    activities['University'] = Activity(
        name='University',
        parent_id=activities['Education'].id,
    )

    session.add_all(
        [
            activities['Beauty'],
            activities['Auto'],
            activities['Legal'],
            activities['IT'],
            activities['Supermarket'],
            activities['Clothing'],
            activities['Electronics'],
            activities['Restaurant'],
            activities['Cafe'],
            activities['FastFood'],
            activities['Hospital'],
            activities['Pharmacy'],
            activities['Dentist'],
            activities['School'],
            activities['University'],
        ],
    )
    session.flush()

    # Third level activities (nested deeper)
    activities['HairSalon'] = Activity(
        name='Hair Salon',
        parent_id=activities['Beauty'].id,
    )
    activities['NailSalon'] = Activity(
        name='Nail Salon',
        parent_id=activities['Beauty'].id,
    )
    activities['Spa'] = Activity(
        name='Spa & Wellness',
        parent_id=activities['Beauty'].id,
    )

    activities['CarRepair'] = Activity(
        name='Car Repair Shop',
        parent_id=activities['Auto'].id,
    )
    activities['CarWash'] = Activity(
        name='Car Wash',
        parent_id=activities['Auto'].id,
    )

    activities['LawFirm'] = Activity(
        name='Law Firm',
        parent_id=activities['Legal'].id,
    )
    activities['Notary'] = Activity(
        name='Notary Public',
        parent_id=activities['Legal'].id,
    )

    activities['Software'] = Activity(
        name='Software Development',
        parent_id=activities['IT'].id,
    )
    activities['Hardware'] = Activity(
        name='Hardware Support',
        parent_id=activities['IT'].id,
    )

    # Fourth level (very nested)
    activities['BarberShop'] = Activity(
        name='Barber Shop',
        parent_id=activities['HairSalon'].id,
    )
    activities['WomenHair'] = Activity(
        name='Women Hair Salon',
        parent_id=activities['HairSalon'].id,
    )

    session.add_all(
        [
            activities['HairSalon'],
            activities['NailSalon'],
            activities['Spa'],
            activities['CarRepair'],
            activities['CarWash'],
            activities['LawFirm'],
            activities['Notary'],
            activities['Software'],
            activities['Hardware'],
            activities['BarberShop'],
            activities['WomenHair'],
        ],
    )
    session.commit()
    # Refresh all activities to ensure they're up to date
    for activity in activities.values():
        session.refresh(activity)

    return activities


def create_buildings(session: Session) -> list[Building]:
    """Create buildings in different areas with geolocations."""
    # Using WKT format for geography points (POINT(longitude latitude))
    buildings_data = [
        {
            'address': '123 Main Street, Downtown',
            'geolocation': 'POINT(-122.4194 37.7749)',  # San Francisco
        },
        {
            'address': '456 Oak Avenue, Central District',
            'geolocation': 'POINT(-122.4195 37.7750)',
        },
        {
            'address': '789 Pine Street, Business District',
            'geolocation': 'POINT(-122.4196 37.7751)',
        },
        {
            'address': '321 Elm Road, Residential Area',
            'geolocation': 'POINT(-122.4200 37.7760)',
        },
        {
            'address': '654 Maple Drive, Shopping District',
            'geolocation': 'POINT(-122.4180 37.7740)',
        },
        {
            'address': '987 Cedar Lane, University District',
            'geolocation': 'POINT(-122.4210 37.7770)',
        },
        {
            'address': '147 Birch Way, Medical District',
            'geolocation': 'POINT(-122.4220 37.7780)',
        },
        {
            'address': '258 Spruce Court, Tech Hub',
            'geolocation': 'POINT(-122.4170 37.7730)',
        },
        {
            'address': '369 Willow Street, Entertainment Zone',
            'geolocation': 'POINT(-122.4230 37.7790)',
        },
        {
            'address': '741 Ash Boulevard, Industrial Area',
            'geolocation': 'POINT(-122.4240 37.7800)',
        },
    ]

    buildings = []
    for data in buildings_data:
        building = Building(
            address=data['address'],
            geolocation=data['geolocation'],
        )
        buildings.append(building)
        session.add(building)

    session.commit()
    # Refresh all buildings to ensure they're up to date
    for building in buildings:
        session.refresh(building)
    return buildings


def create_organizations(
    session: Session,
    activities: dict[str, Activity],
    buildings: list[Building],
) -> list[Organization]:
    """Create organizations with various activities and phone numbers."""
    organizations_data = [
        {
            'name': 'Downtown Beauty Center',
            'building_index': 0,
            'activities': ['Beauty', 'HairSalon', 'WomenHair'],
            'phones': ['+1-555-0101', '+1-555-0102'],
        },
        {
            'name': 'Main Street Auto Repair',
            'building_index': 1,
            'activities': ['Auto', 'CarRepair'],
            'phones': ['+1-555-0201'],
        },
        {
            'name': 'Oak Avenue Supermarket',
            'building_index': 1,
            'activities': ['Retail', 'Supermarket'],
            'phones': ['+1-555-0301', '+1-555-0302', '+1-555-0303'],
        },
        {
            'name': 'Pine Legal Associates',
            'building_index': 2,
            'activities': ['Legal', 'LawFirm'],
            'phones': ['+1-555-0401', '+1-555-0402'],
        },
        {
            'name': 'Elm Italian Restaurant',
            'building_index': 3,
            'activities': ['Food', 'Restaurant'],
            'phones': ['+1-555-0501'],
        },
        {
            'name': 'Maple Electronics Store',
            'building_index': 4,
            'activities': ['Retail', 'Electronics'],
            'phones': ['+1-555-0601', '+1-555-0602'],
        },
        {
            'name': 'University Medical Center',
            'building_index': 5,
            'activities': ['Healthcare', 'Hospital'],
            'phones': ['+1-555-0701', '+1-555-0702', '+1-555-0703'],
        },
        {
            'name': 'Spruce Tech Solutions',
            'building_index': 7,
            'activities': ['IT', 'Software'],
            'phones': ['+1-555-0801'],
        },
        {
            'name': 'Willow Street Cafe',
            'building_index': 8,
            'activities': ['Food', 'Cafe'],
            'phones': ['+1-555-0901', '+1-555-0902'],
        },
        {
            'name': 'Ash Pharmacy',
            'building_index': 9,
            'activities': ['Healthcare', 'Pharmacy'],
            'phones': ['+1-555-1001'],
        },
        # Organizations using deeply nested activities
        {
            'name': 'Elite Barber Shop',
            'building_index': 0,
            'activities': ['Services', 'Beauty', 'HairSalon', 'BarberShop'],
            'phones': ['+1-555-1101'],
        },
        {
            'name': 'Quick Car Wash',
            'building_index': 1,
            'activities': ['Services', 'Auto', 'CarWash'],
            'phones': ['+1-555-1201', '+1-555-1202'],
        },
        {
            'name': 'Luxury Nail Salon',
            'building_index': 4,
            'activities': ['Services', 'Beauty', 'NailSalon'],
            'phones': ['+1-555-1301'],
        },
        {
            'name': 'City Dental Clinic',
            'building_index': 6,
            'activities': ['Healthcare', 'Dentist'],
            'phones': ['+1-555-1401', '+1-555-1402'],
        },
        {
            'name': 'Central Notary Office',
            'building_index': 2,
            'activities': ['Services', 'Legal', 'Notary'],
            'phones': ['+1-555-1501'],
        },
        {
            'name': 'Tech Hardware Support',
            'building_index': 7,
            'activities': ['Services', 'IT', 'Hardware'],
            'phones': ['+1-555-1601'],
        },
        {
            'name': 'Wellness Spa Center',
            'building_index': 3,
            'activities': ['Services', 'Beauty', 'Spa'],
            'phones': ['+1-555-1701', '+1-555-1702', '+1-555-1703'],
        },
        {
            'name': 'Fashion Clothing Store',
            'building_index': 4,
            'activities': ['Retail', 'Clothing'],
            'phones': ['+1-555-1801'],
        },
        {
            'name': 'Fast Burger Joint',
            'building_index': 8,
            'activities': ['Food', 'FastFood'],
            'phones': ['+1-555-1901'],
        },
        {
            'name': 'Community School',
            'building_index': 5,
            'activities': ['Education', 'School'],
            'phones': ['+1-555-2001', '+1-555-2002'],
        },
    ]

    organizations = []
    for data in organizations_data:
        organization = Organization(
            name=data['name'],
            building_id=buildings[data['building_index']].id,
        )

        # Add activities (some use deeply nested activities)
        org_activities = [activities[key] for key in data['activities']]
        organization.activities = org_activities

        # Add phone numbers
        organization.phones = [OrganizationPhone(phone_number=phone) for phone in data['phones']]

        organizations.append(organization)
        session.add(organization)

    session.commit()
    # Refresh all organizations to ensure they're up to date
    for organization in organizations:
        session.refresh(organization)
    return organizations


def main():
    """Main function to populate the database."""
    print('Starting database population...')

    # Get a session
    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        # Check if data already exists
        existing_activities = session.query(Activity).count()
        existing_buildings = session.query(Building).count()
        existing_organizations = session.query(Organization).count()

        if existing_activities > 0 or existing_buildings > 0 or existing_organizations > 0:
            response = input(
                'Database already contains data. '
                'Do you want to clear it and start fresh? (yes/no): ',
            )
            if response.lower() == 'yes':
                print('Clearing existing data...')
                session.query(OrganizationPhone).delete()
                session.query(Organization).delete()
                session.query(Building).delete()
                session.query(Activity).delete()
                session.commit()
                print('Existing data cleared.')
            else:
                print('Keeping existing data. Exiting.')
                return

        print('Creating activities...')
        activities = create_activities(session)
        print(f'Created {len(activities)} activities')

        print('Creating buildings...')
        buildings = create_buildings(session)
        print(f'Created {len(buildings)} buildings')

        print('Creating organizations...')
        organizations = create_organizations(session, activities, buildings)
        print(f'Created {len(organizations)} organizations')

        print('Database population completed successfully!')
        print('\nSummary:')
        print(f'  - Activities: {len(activities)} (with nested hierarchies)')
        print(f'  - Buildings: {len(buildings)} (in different areas)')
        print(f'  - Organizations: {len(organizations)} (with various activities)')

    except Exception as e:
        session.rollback()
        print(f'Error populating database: {e}')
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
