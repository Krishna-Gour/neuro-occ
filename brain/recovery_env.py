import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import yaml
import os
from dgca_rules.validator import FDTLValidator
from database import SessionLocal, Flight, Aircraft, Pilot

class AirlineRecoveryEnv(gym.Env):
    """
    Custom Gymnasium environment for Airline Recovery.
    Strategy: Crawl (Single Orchestrator Agent)
    Goal: Minimize Cost Function (Hamiltonian)
    """
    def __init__(self, config_path='config.yaml'):
        super(AirlineRecoveryEnv, self).__init__()
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.weights = self.config['cost_weights']
        self.validator = FDTLValidator(config_path=config_path)
        
        # Load data from database
        session = SessionLocal()
        try:
            self.flights = session.query(Flight).all()
            self.aircraft = session.query(Aircraft).all()
            self.pilots = session.query(Pilot).all()
        finally:
            session.close()
        
        # Convert to DataFrames for compatibility (or keep as objects)
        # For now, keep as lists of objects
        
        # Action space: 0=No Action, 1=Delay, 2=Cancel, 3=Swap Aircraft, 4=Swap Crew
        self.action_space = spaces.Discrete(5)
        
        # Observation space: Simplified state
        # (Average Delay, Crew Violation Count, Cancellation Count, Aircraft Health, etc.)
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)
        
        self.state = np.zeros(10)
        self.current_flight_idx = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.zeros(10)
        self.current_flight_idx = 0
        return self.state.astype(np.float32), {}

    def step(self, action):
        # Current flight being considered for recovery
        flight = self.flights[self.current_flight_idx]
        
        delay = 0
        n_cx = 0
        v_crew = 0
        
        if action == 1: # Delay
            delay = 60 # Assume 60 min delay for simplicity
        elif action == 2: # Cancel
            n_cx = 1
        elif action == 4: # Swap Crew (Check compliance)
            # Simulate a swap and verify
            pilot_id = flight.pilot_id
            # Find pilot data
            pilot = next((p for p in self.pilots if p.pilot_id == pilot_id), None)
            if pilot:
                pilot_data = {
                    "daily_flight_hours": 6,  # Mock - would need to calculate from flights
                    "consecutive_night_duties": pilot.consecutive_night_duties,
                    "hours_since_last_rest": 12,  # Mock
                    "weekly_flight_hours": 20  # Mock
                }
                proposed_flight = {"duration_hours": 3}
                compliant, reason = self.validator.validate_assignment(pilot_data, proposed_flight)
                if not compliant:
                    v_crew = 1 # Violation!
        
        # Hamiltonian Cost Function Calculation
        # C = (w_delay * delay) + (w_cancel * n_cx) + (w_violation * v_crew)
        cost = (self.weights['w_delay'] * delay) + \
               (self.weights['w_cancel'] * n_cx) + \
               (self.weights['w_violation'] * v_crew)
        
        reward = -cost
        
        self.current_flight_idx += 1
        done = self.current_flight_idx >= len(self.flights)
        
        # Update state (mock)
        self.state = np.random.rand(10)
        
        return self.state.astype(np.float32), reward, done, False, {"violation": v_crew > 0}

if __name__ == "__main__":
    env = AirlineRecoveryEnv()
    obs, info = env.reset()
    print(f"Single Orchestrator Env Initialized. Action Space: {env.action_space}")
    for _ in range(3):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"Action: {action}, Reward: {reward:.2f}, Violation: {info['violation']}")
