# Documentation: Reinforcement Learning Environment & Orchestrator Agent

## 1. Purpose: Optimizing Disruption Recovery

While the Proposer-Verifier loop ensures that any single recovery action is valid, the broader challenge is to find the *optimal sequence* of actions to resolve a disruption. Making a locally optimal choice (e.g., delaying one flight) might lead to a globally suboptimal outcome (e.g., a cascade of cancellations later).

This is where Reinforcement Learning (RL) comes in. The **Orchestrator Agent** is an RL agent trained to make strategic decisions that minimize the overall cost of a disruption. It learns a policy that balances competing priorities, such as:
*   Minimizing passenger delays.
*   Avoiding costly cancellations.
*   Ensuring crew assignments are always legal.

The agent is trained in a custom-built simulation environment that reflects the dynamics of airline operations.

## 2. Key Components

*   **`brain/recovery_env.py`**: This file defines the `AirlineRecoveryEnv`, a custom environment compatible with the [Gymnasium](https://gymnasium.farama.org/) library. It provides the framework for the agent to interact with the airline simulation, take actions, and receive feedback in the form of rewards or costs.

## 3. The Reinforcement Learning Problem

The task of disruption recovery is framed as an RL problem with the following components:

*   **Goal**: The agent's goal is to learn a policy (a strategy for choosing actions) that minimizes a **Hamiltonian Cost Function**. This function represents the total negative impact of a disruption, and the agent is rewarded for keeping this cost low.

*   **State (`Observation`)**: The "state" is the information the agent uses to make decisions. In the current implementation, this is a simplified 10-element array of floating-point numbers representing a high-level overview of the operational health, such as average delay, number of cancellations, and number of crew violations.

*   **Actions**: The agent can choose from a discrete set of high-level recovery actions for any given flight:
    *   `0`: **No Action** - Let the flight proceed as planned.
    *   `1`: **Delay** - Delay the flight by a fixed amount (e.g., 60 minutes).
    *   `2`: **Cancel** - Cancel the flight.
    *   `3`: **Swap Aircraft** - (Placeholder for future implementation).
    *   `4`: **Swap Crew** - Attempt to re-assign the crew. This action triggers a call to the `FDTLValidator` to ensure the swap is legal.

*   **Reward (`-Cost`)**: The agent's performance is measured by a cost function. The reward given to the agent is the *negative* of this cost, meaning the agent is incentivized to take actions that result in a lower total cost.

## 4. The Hamiltonian Cost Function

The core of the RL environment is the cost function, which quantifies how "bad" a particular outcome is. It is a weighted sum of the key negative business impacts:

**`Cost = (w_delay * total_delay) + (w_cancel * num_cancellations) + (w_violation * num_violations)`**

The weights for this function (`w_delay`, `w_cancel`, `w_violation`) are defined in `config.yaml`, allowing us to tune the agent's priorities.

```yaml
# from config.yaml
cost_weights:
  w_delay: 1.0       # Cost per minute of delay
  w_cancel: 500.0    # Cost per cancellation
  w_violation: 1000.0 # High penalty for regulatory violation
```

By assigning a very high weight to `w_violation`, we strongly discourage the agent from ever making illegal crew assignments, even if it means incurring higher delay or cancellation costs.

## 5. How It Works

The training process involves the agent repeatedly interacting with the `AirlineRecoveryEnv`:

1.  **Reset**: The environment is reset to an initial state, representing the start of a disruption scenario.
2.  **Observe**: The agent receives the current state of the airline operations.
3.  **Act**: The agent chooses an action based on its current policy.
4.  **Step**: The `step` function in the environment executes the chosen action.
    *   It calculates the immediate cost of the action (e.g., adds delay minutes or increments the cancellation count).
    *   If the action involves a crew swap, it calls the `FDTLValidator` to check for compliance. A failed validation results in a high `w_violation` penalty.
    *   It calculates the total cost and returns it to the agent as a negative reward.
5.  **Learn**: The agent updates its policy based on the reward received, learning which actions lead to lower costs in the long run.
6.  This loop repeats for thousands or millions of steps until the agent's policy converges on an optimal strategy.

## 6. How to Train the Agent

Since `AirlineRecoveryEnv` is a standard Gymnasium environment, it can be trained using any major RL library, such as [Stable Baselines3](https://stable-baselines3.readthedocs.io/en/master/) or [Ray RLlib](https://docs.ray.io/en/latest/rllib/index.html).

A typical training script (not yet implemented) would look something like this:

```python
# Fictional training script
import gymnasium as gym
from stable_baselines3 import PPO
from brain.recovery_env import AirlineRecoveryEnv

# 1. Create the environment
env = AirlineRecoveryEnv()

# 2. Instantiate the RL model (e.g., PPO)
model = PPO("MlpPolicy", env, verbose=1)

# 3. Train the model
model.learn(total_timesteps=100000)

# 4. Save the trained model
model.save("airline_orchestrator")
```