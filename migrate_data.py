import pandas as pd
from database import SessionLocal, Pilot, Aircraft, Flight, Airport
from datetime import datetime

def migrate_data():
    session = SessionLocal()
    
    # Migrate airports
    airports_df = pd.read_csv('data/airports.csv')
    for _, row in airports_df.iterrows():
        airport = Airport(
            id=row['id'],
            name=row['name'],
            lat=row['lat'],
            lon=row['lon']
        )
        session.add(airport)
    
    # Migrate pilots
    pilots_df = pd.read_csv('data/pilots.csv')
    for _, row in pilots_df.iterrows():
        pilot = Pilot(
            pilot_id=row['pilot_id'],
            name=row['name'],
            base=row['base'],
            total_hours=row['total_hours'],
            fatigue_score=row['fatigue_score'],
            last_rest_end=datetime.fromisoformat(row['last_rest_end']),
            consecutive_night_duties=row['consecutive_night_duties']
        )
        session.add(pilot)
    
    # Migrate aircraft
    aircraft_df = pd.read_csv('data/aircraft.csv')
    for _, row in aircraft_df.iterrows():
        aircraft = Aircraft(
            tail_number=row['tail_number'],
            type=row['type'],
            base=row['base'],
            health_score=row['health_score']
        )
        session.add(aircraft)
    
    # Migrate flights
    flights_df = pd.read_csv('data/flights.csv', dtype={'flight_number': str})
    for _, row in flights_df.iterrows():
        flight = Flight(
            flight_number=row['flight_number'],
            origin=row['origin'],
            destination=row['destination'],
            scheduled_departure=datetime.fromisoformat(row['scheduled_departure']),
            scheduled_arrival=datetime.fromisoformat(row['scheduled_arrival']),
            aircraft_tail=row['aircraft_tail'],
            pilot_id=row['pilot_id'],
            status=row['status']
        )
        session.add(flight)
    
    session.commit()
    session.close()
    print("Data migration completed.")

if __name__ == "__main__":
    migrate_data()