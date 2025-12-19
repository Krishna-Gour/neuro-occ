# Data Generation Process - Production-Ready Synthetic Data Pipeline

## 1. Purpose

**Neuro-OCC 2.0** requires a rich, realistic dataset to simulate airline operations and train its AI components. Due to the proprietary and sensitive nature of real airline data, we have developed a production-ready synthetic data generation pipeline that is fully integrated into the automated deployment system.

This pipeline creates a coherent set of interconnected data, including:
*   A fleet of aircraft
*   A roster of pilots
*   A network of airports
*   A schedule of flights

This allows us to simulate complex operational scenarios and test the system's disruption management capabilities in a controlled environment.

## 2. Production Integration

The data generation is fully automated in the Neuro-OCC 2.0 deployment:

- **Automated Execution**: Data generation runs automatically during `./start.sh`
- **MCP Server Integration**: Generated data is loaded into MCP servers for real-time access
- **Validation Pipeline**: Generated data is validated before system startup
- **Scalable Configuration**: Easy scaling for different deployment sizes

## 3. Key Components

*   **`scripts/generate_data.py`**: This is the primary script responsible for executing the data generation logic. It reads the configuration, generates the data using the `Faker` library and other logic, and saves the output to CSV files.

*   **`config.yaml`**: This configuration file defines all the parameters for the data generation process. It allows for easy customization of the dataset's scale and characteristics without modifying the script's code.

*   **Automated Pipeline**: Integrated into the startup script for seamless deployment

## 4. How It Works

The `generate_data.py` script follows these steps:

1.  **Load Configuration**: It starts by loading the parameters from `config.yaml`.

2.  **Generate Airports**: It generates a specified number of airports, assigning them realistic IATA codes, names, and locations. The configuration allows specifying which countries to generate airports in.

3.  **Generate Aircraft**: It creates a fleet of aircraft. The types of aircraft (e.g., A320, B737) and their count are defined in the config. Each aircraft is assigned a unique tail number.

4.  **Generate Pilots**: It generates a roster of pilots, assigning each a unique ID, name, and home base. The number of pilots to generate is configurable.

5.  **Generate Flights**: This is the most complex step. The script generates a complete flight schedule for a specified date range. For each day, it creates a series of flights, ensuring a degree of logical consistency:
    *   Flights are created between the generated airports.
    *   A single aircraft operates a sequence of flights throughout the day, respecting realistic turnaround times.
    *   The script aims to create a "hub-and-spoke" like structure if the airport distribution allows it.

6.  **Data Validation**: Automated validation ensures data integrity before system startup

7.  **MCP Loading**: Generated data is automatically loaded into MCP servers

## 5. The `config.yaml` File

This file is central to controlling the data generation. Here are the key parameters:

```yaml
# Data Generation Parameters
num_pilots: 500
num_aircraft: 100
num_airports: 30
simulation_start_date: "2025-12-01T00:00:00Z"

# Aircraft Configuration
aircraft_models:
  - "Airbus A320"
  - "Boeing 737-800"
  - "Airbus A321"
  - "Boeing 777-300ER"

# Airport Configuration
airport_codes:
  - "DEL"  # Delhi
  - "BOM"  # Mumbai
  - "BLR"  # Bangalore
  - "MAA"  # Chennai
  - "CCU"  # Kolkata
  - "HYD"  # Hyderabad

# Flight Generation Parameters
min_flights_per_rotation: 2
max_flights_per_rotation: 5
min_turnaround_time_minutes: 45
max_turnaround_time_minutes: 90
min_flight_duration_hours: 0.75
max_flight_duration_hours: 4.0

# Output Configuration
output_dir: 'data/'
```

*   `num_pilots`, `num_aircraft`, `num_airports`: Control the scale of the dataset.
*   `simulation_start_date`: Reference date for all generated timestamps.
*   `aircraft_models`: Available aircraft types in the fleet.
*   `airport_codes`: Specific airports to include in the network.
*   `min/max_flights_per_rotation`: Range for daily aircraft utilization.
*   `turnaround_time_minutes`: Ground time between flights.
*   `flight_duration_hours`: Realistic flight duration range.
*   `output_dir`: The directory where the generated CSV files will be saved.

## 6. Generated Data Files

The script produces the following files in the specified `output_dir` (typically `data/`):

*   **`airports.csv`**:
    *   `iata_code`: Unique 3-letter code (e.g., "DEL").
    *   `name`: Full name of the airport.
    *   `city`, `country`: Location of the airport.

*   **`aircraft.csv`**:
    *   `tail_number`: Unique identifier for the aircraft (e.g., "VT-XYZ").
    *   `type`: Model of the aircraft (e.g., "A320").
    *   `home_base`: The IATA code of its home airport.

*   **`pilots.csv`**:
    *   `pilot_id`: Unique identifier for the pilot.
    *   `name`: Full name of the pilot.
    *   `home_base`: The IATA code of their home airport.

*   **`flights.csv`**:
    *   `flight_id`: Unique identifier for the flight.
    *   `departure_airport`, `arrival_airport`: IATA codes.
    *   `departure_time`, `arrival_time`: Scheduled times in UTC.
    *   `aircraft_id`: Tail number of the assigned aircraft.
    *   `pilot_id`: (Initially empty) To be assigned during simulation.

## 7. Automated Production Usage

Data generation is fully automated in the production deployment:

```bash
# Single command starts everything including data generation
./start.sh

# This automatically:
# 1. Sets up Python environment
# 2. Generates synthetic data
# 3. Loads data into MCP servers
# 4. Starts all services
# 5. Performs health checks
```

## 8. Manual Data Generation (Development)

To generate a new dataset manually:

1.  **Customize the config**: Open `config.yaml` and adjust the parameters as needed.
2.  **Run the script**: Execute the following command from the root directory of the project:

    ```bash
    python scripts/generate_data.py
    ```

3.  **Check the output**: The generated CSV files will be available in the directory specified in `config.yaml`.

**Note**: The `data/` directory is included in `.gitignore` to prevent large data files from being committed to the version control system.

## 9. Data Quality Assurance

The production system includes automated data validation:

- **Integrity Checks**: Ensures all referenced entities exist
- **Consistency Validation**: Verifies flight schedules are realistic
- **MCP Loading Verification**: Confirms data is properly loaded into servers
- **Performance Metrics**: Tracks data generation and loading times

## 10. Scaling Considerations

For different deployment sizes:

- **Development**: 50 pilots, 10 aircraft, 15 airports
- **Staging**: 200 pilots, 50 aircraft, 25 airports
- **Production**: 500+ pilots, 100+ aircraft, 30+ airports

Configuration can be adjusted in `config.yaml` and redeployed with `./start.sh`.