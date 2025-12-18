# Documentation: Data Generation Process

## 1. Purpose

The Neuro-OCC system requires a rich, realistic dataset to simulate airline operations and train its AI components. Due to the proprietary and sensitive nature of real airline data, we have developed a synthetic data generation pipeline.

This pipeline creates a coherent set of interconnected data, including:
*   A fleet of aircraft
*   A roster of pilots
*   A network of airports
*   A schedule of flights

This allows us to simulate complex operational scenarios and test the system's disruption management capabilities in a controlled environment.

## 2. Key Components

*   **`scripts/generate_data.py`**: This is the primary script responsible for executing the data generation logic. It reads the configuration, generates the data using the `Faker` library and other logic, and saves the output to CSV files.

*   **`config.yaml`**: This configuration file defines all the parameters for the data generation process. It allows for easy customization of the dataset's scale and characteristics without modifying the script's code.

## 3. How It Works

The `generate_data.py` script follows these steps:

1.  **Load Configuration**: It starts by loading the parameters from `config.yaml`.

2.  **Generate Airports**: It generates a specified number of airports, assigning them realistic IATA codes, names, and locations. The configuration allows specifying which countries to generate airports in.

3.  **Generate Aircraft**: It creates a fleet of aircraft. The types of aircraft (e.g., A320, B737) and their count are defined in the config. Each aircraft is assigned a unique tail number.

4.  **Generate Pilots**: It generates a roster of pilots, assigning each a unique ID, name, and home base. The number of pilots to generate is configurable.

5.  **Generate Flights**: This is the most complex step. The script generates a complete flight schedule for a specified date range. For each day, it creates a series of flights, ensuring a degree of logical consistency:
    *   Flights are created between the generated airports.
    *   A single aircraft operates a sequence of flights throughout the day, respecting realistic turnaround times.
    *   The script aims to create a "hub-and-spoke" like structure if the airport distribution allows it.

## 4. The `config.yaml` File

This file is central to controlling the data generation. Here are the key parameters:

```yaml
num_pilots: 50
num_aircraft: 10
num_airports: 15
date_range:
  start: '2023-10-01'
  end: '2023-10-07'
aircraft_types:
  - A320
  - B737
airport_countries:
  - IN # Using country codes
output_dir: 'data/'
```

*   `num_pilots`, `num_aircraft`, `num_airports`: Control the scale of the dataset.
*   `date_range`: Defines the period for which the flight schedule will be generated.
*   `aircraft_types`: A list of aircraft models to include in the fleet.
*   `airport_countries`: A list of country codes to generate airports from, ensuring geographical relevance.
*   `output_dir`: The directory where the generated CSV files will be saved.

## 5. Generated Data Files

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

## 6. How to Use

To generate a new dataset:

1.  **Customize the config**: Open `config.yaml` and adjust the parameters as needed.
2.  **Run the script**: Execute the following command from the root directory of the project:

    ```bash
    python scripts/generate_data.py
    ```

3.  **Check the output**: The generated CSV files will be available in the directory specified in `config.yaml`.

**Note**: The `data/` directory is included in `.gitignore` to prevent large data files from being committed to the version control system.