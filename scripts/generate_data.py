
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import yaml
import logging
import argparse
from pathlib import Path

# --- Configuration Loading ---
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data_generation.log")
    ]
)

# Set seed for reproducibility
random.seed(config["random_seed"])
np.random.seed(config["random_seed"])

SIMULATION_START_DATE = datetime.fromisoformat(config["simulation_start_date"].replace("Z", "+00:00"))

def generate_airports(num_airports, airport_codes, data_dir):
    logging.info(f"Generating {num_airports} airports...")
    selected_codes = random.sample(airport_codes, num_airports)
    airports_data = []
    for code in selected_codes:
        airports_data.append({
            "id": code,
            "name": f"Airport {code}", # Placeholder name
            "lat": np.random.uniform(8, 33),
            "lon": np.random.uniform(68, 92)
        })
    airports_df = pd.DataFrame(airports_data)
    airports_df.to_csv(data_dir / "airports.csv", index=False)
    logging.info(f"Generated {len(airports_df)} airports and saved to {data_dir / "airports.csv"}")
    return airports_df

def generate_aircraft(num_aircraft, aircraft_models, airports_df, data_dir):
    logging.info(f"Generating {num_aircraft} aircraft...")
    aircraft_data = []
    for i in range(num_aircraft):
        base = random.choice(airports_df["id"].tolist())
        aircraft_data.append({
            "tail_number": f"VT-I{str(i).zfill(2)}",
            "type": random.choice(aircraft_models),
            "base": base,
            "health_score": round(random.uniform(0.7, 1.0), 2)
        })
    aircraft_df = pd.DataFrame(aircraft_data)
    aircraft_df.to_csv(data_dir / "aircraft.csv", index=False)
    logging.info(f"Generated {len(aircraft_df)} aircraft and saved to {data_dir / "aircraft.csv"}")
    return aircraft_df

def generate_pilots(num_pilots, airports_df, data_dir):
    logging.info(f"Generating {num_pilots} pilots...")
    pilots_data = []
    for i in range(num_pilots):
        # Use SIMULATION_START_DATE for consistent time anchoring
        last_rest_end = SIMULATION_START_DATE - timedelta(hours=random.randint(12, 100))
        pilots_data.append({
            "pilot_id": f"PLT{str(i).zfill(3)}",
            "name": f"Pilot {i}",
            "base": random.choice(airports_df["id"].tolist()),
            "total_hours": random.randint(500, 10000),
            "fatigue_score": round(random.uniform(0.0, 0.4), 2),
            "last_rest_end": last_rest_end.isoformat(),
            "consecutive_night_duties": random.randint(0, 2)
        })
    pilots_df = pd.DataFrame(pilots_data)
    pilots_df.to_csv(data_dir / "pilots.csv", index=False)
    logging.info(f"Generated {len(pilots_df)} pilots and saved to {data_dir / "pilots.csv"}")
    return pilots_df

def generate_flights_with_rotations(aircraft_df, airports_df, pilots_df, config, data_dir):
    logging.info("Generating realistic aircraft rotations and flights...")
    flights_data = []
    flight_id_counter = 100

    min_flights = config["min_flights_per_rotation"]
    max_flights = config["max_flights_per_rotation"]
    min_turnaround = config["min_turnaround_time_minutes"]
    max_turnaround = config["max_turnaround_time_minutes"]
    min_flight_dur_hours = config["min_flight_duration_hours"]
    max_flight_dur_hours = config["max_flight_duration_hours"]

    all_pilot_ids = pilots_df["pilot_id"].tolist()
    current_pilot_assignments = {}

    for idx, ac in aircraft_df.iterrows():
        current_location = ac["base"]
        current_time = SIMULATION_START_DATE + timedelta(minutes=random.randint(0, 24 * 60)) # Start at a random time on day 1
        
        num_legs = random.randint(min_flights, max_flights)
        assigned_pilot = random.choice(all_pilot_ids) # Assign a pilot for the rotation initially
        current_pilot_assignments[ac["tail_number"]] = assigned_pilot

        for _ in range(num_legs):
            available_destinations = airports_df[airports_df["id"] != current_location]["id"].tolist()
            if not available_destinations:
                logging.warning(f"No available destinations from {current_location} for aircraft {ac["tail_number"]}. Breaking rotation.")
                break
            destination = random.choice(available_destinations)
            
            flight_duration = timedelta(hours=random.uniform(min_flight_dur_hours, max_flight_dur_hours))
            
            dep_time = current_time
            arr_time = dep_time + flight_duration
            
            flights_data.append({
                "flight_number": f"6E-{flight_id_counter}",
                "origin": current_location,
                "destination": destination,
                "scheduled_departure": dep_time.isoformat(),
                "scheduled_arrival": arr_time.isoformat(),
                "aircraft_tail": ac["tail_number"],
                "pilot_id": assigned_pilot,
                "status": "SCHEDULED"
            })
            
            flight_id_counter += 1
            current_location = destination
            current_time = arr_time + timedelta(minutes=random.randint(min_turnaround, max_turnaround))

    flights_df = pd.DataFrame(flights_data)
    flights_df.to_csv(data_dir / "flights.csv", index=False)
    logging.info(f"Generated {len(flights_df)} flights with realistic rotations and saved to {data_dir / "flights.csv"}")
    return flights_df

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic airline operations data.")
    parser.add_argument("--num_airports", type=int, default=config["num_airports"], help="Number of airports to generate.")
    parser.add_argument("--num_aircraft", type=int, default=config["num_aircraft"], help="Number of aircraft to generate.")
    parser.add_argument("--num_pilots", type=int, default=config["num_pilots"], help="Number of pilots to generate.")
    parser.add_argument("--output_dir", type=Path, default=Path(__file__).parent.parent / "data", help="Output directory for CSV files.")
    
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    airports_df = generate_airports(args.num_airports, config["airport_codes"], args.output_dir)
    aircraft_df = generate_aircraft(args.num_aircraft, config["aircraft_models"], airports_df, args.output_dir)
    pilots_df = generate_pilots(args.num_pilots, airports_df, args.output_dir)
    flights_df = generate_flights_with_rotations(aircraft_df, airports_df, pilots_df, config, args.output_dir)

    logging.info("Data generation complete.")

if __name__ == "__main__":
    main()
