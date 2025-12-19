# Reinforcement Learning Environment & Orchestrator Agent - Production Optimization

## 1. Purpose: Optimizing Disruption Recovery in Production

While the Proposer-Verifier loop ensures that any single recovery action is valid, the broader challenge is to find the *optimal sequence* of actions to resolve a disruption. Making a locally optimal choice (e.g., delaying one flight) might lead to a globally suboptimal outcome (e.g., a cascade of cancellations later).

This is where Reinforcement Learning (RL) comes in. The **Orchestrator Agent** is an RL agent trained to make strategic decisions that minimize the overall cost of a disruption. It learns a policy that balances competing priorities, such as:
*   Minimizing passenger delays.
*   Avoiding costly cancellations.
*   Ensuring crew assignments are always legal.
*   Optimizing resource utilization.

The agent is trained in a custom-built simulation environment that reflects the dynamics of airline operations, now integrated into the Neuro-OCC 2.0 production system.

## 2. Production System Integration

The RL orchestrator is fully integrated into Neuro-OCC 2.0:

- **Automated Training**: RL agents trained during system initialization
- **Real-time Optimization**: Production deployment uses trained policies
- **Performance Monitoring**: RL decision quality tracking and metrics
- **Continuous Learning**: Online learning from production outcomes
- **A/B Testing**: Compare different RL strategies in production

## 3. Key Components

*   **`brain/recovery_env.py`**: This file defines the `AirlineRecoveryEnv`, a custom environment compatible with the [Gymnasium](https://gymnasium.farama.org/) library. It provides the framework for the agent to interact with the airline simulation, take actions, and receive feedback in the form of rewards or costs.

*   **Production Integration**: Connected to MCP servers for real-time data
*   **Multi-agent Coordination**: Works with neuro-symbolic components
*   **Scalable Training**: Distributed training capabilities

## 4. The Reinforcement Learning Problem

The task of disruption recovery is framed as an RL problem with the following components:

*   **Goal**: The agent's goal is to learn a policy (a strategy for choosing actions) that minimizes a **Hamiltonian Cost Function**. This function represents the total negative impact of a disruption, and the agent is rewarded for keeping this cost low.

*   **State (`Observation`)**: The "state" is the information the agent uses to make decisions. In the production implementation, this includes:
    - Real-time flight network status from MCP servers
    - Crew availability and fatigue levels
    - Aircraft health scores from Mamba models
    - Current disruption impact metrics
    - Historical performance data

*   **Actions**: The agent can choose from a discrete set of high-level recovery actions for any given flight:
    *   `0`: **No Action** - Let the flight proceed as planned.
    *   `1`: **Delay** - Delay the flight by a configurable amount.
    *   `2`: **Cancel** - Cancel the flight (high cost penalty).
    *   `3`: **Swap Aircraft** - Reassign to healthier aircraft.
    *   `4`: **Swap Crew** - Attempt legal crew reassignment (validated by DGCA rules).
    *   `5`: **Reroute** - Change flight path to avoid disruption.
    *   `6`: **Consolidate** - Merge with another flight to optimize capacity.

*   **Reward (`-Cost`)**: The agent's performance is measured by a cost function. The reward given to the agent is the *negative* of this cost, meaning the agent is incentivized to take actions that result in a lower total cost.

## 5. Advanced Cost Function

The core of the RL environment is the multi-objective cost function, which quantifies disruption impact:

**`Cost = (w_delay × total_delay_minutes) + (w_cancel × num_cancellations) + (w_violation × num_violations) + (w_resource × resource_inefficiency) + (w_passenger × passenger_impact)`**

The weights for this function are defined in `config.yaml`, allowing optimization for different priorities:

```yaml
# from config.yaml - Production weights
cost_weights:
  w_delay: 1.0         # Cost per minute of delay
  w_cancel: 500.0      # Cost per cancellation
  w_violation: 1000.0  # High penalty for regulatory violation
  w_resource: 50.0     # Cost for inefficient resource use
  w_passenger: 10.0    # Cost per affected passenger
```

By assigning a very high weight to `w_violation`, we strongly discourage the agent from ever making illegal crew assignments, even if it means incurring higher delay or cancellation costs.

## 6. Production Training Architecture

### Distributed Training
The training process uses production-grade RL frameworks:

```python
# Production training setup
import gymnasium as gym
from stable_baselines3 import PPO
from brain.recovery_env import AirlineRecoveryEnv

# 1. Create production environment with MCP integration
env = AirlineRecoveryEnv(
    mcp_servers={
        'crew': 'http://localhost:8001',
        'fleet': 'http://localhost:8002',
        'regulatory': 'http://localhost:8003'
    },
    config_path='config.yaml'
)

# 2. Advanced RL model with custom architecture
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    verbose=1
)

# 3. Train with production data
model.learn(total_timesteps=1000000)  # Extended training

# 4. Save production model
model.save("models/airline_orchestrator_v2")
```

### Training Enhancements
- **Curriculum Learning**: Start with simple disruptions, progress to complex scenarios
- **Domain Randomization**: Train on varied airline network configurations
- **Multi-objective Optimization**: Balance competing business priorities
- **Safety Constraints**: Hard constraints on regulatory compliance

## 7. Production Deployment

### Model Serving
- **ONNX Export**: Optimized models for production inference
- **Model Versioning**: A/B testing of different trained models
- **Performance Monitoring**: Inference latency and accuracy tracking
- **Automatic Updates**: Continuous learning from production feedback

### Real-time Integration
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Disruption    │───▶│   RL Orchestrator│───▶│   Action         │
│   Detected      │    │   (Production)   │    │   Selection      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   State Vector  │    │   Policy         │    │   Validation    │
│   (MCP Data)    │    │   Inference      │    │   (Symbolic)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Decision Pipeline
1. **State Construction**: Gather real-time state from all MCP servers
2. **Policy Inference**: RL model selects optimal action sequence
3. **Validation**: Symbolic verifier ensures compliance
4. **Execution**: Actions implemented through Brain API
5. **Feedback Loop**: Outcomes fed back for continuous learning

## 8. Performance Metrics

### Training Metrics
- **Convergence**: Policy improvement over training episodes
- **Sample Efficiency**: Learning speed and data requirements
- **Stability**: Consistent performance across disruption types
- **Generalization**: Performance on unseen scenarios

### Production Metrics
- **Decision Quality**: Cost reduction vs. baseline strategies
- **Response Time**: Real-time action selection performance
- **Compliance Rate**: Percentage of regulatory-compliant decisions
- **Business Impact**: Actual cost savings and passenger impact reduction

## 9. Advanced Features

### Multi-Agent RL
- **Hierarchical Policies**: High-level strategy with low-level execution
- **Cooperative Agents**: Multiple RL agents for different disruption types
- **Adversarial Training**: Robustness against unexpected scenarios
- **Transfer Learning**: Apply learning from one network to another

### Integration with Neuro-Symbolic System
- **Hybrid Decisions**: RL guides LLM proposer toward better solutions
- **Explainable Actions**: RL decisions augmented with symbolic explanations
- **Safety Guarantees**: Symbolic constraints on RL action space
- **Performance Bounds**: Theoretical guarantees on decision quality

## 10. Future Enhancements

### Advanced RL Techniques
- **Model-Based RL**: Learn world model for better planning
- **Meta-Learning**: Adapt quickly to new disruption types
- **Offline RL**: Learn from historical disruption data
- **Multi-Task Learning**: Handle multiple airline networks simultaneously

### Production Scaling
- **Distributed Inference**: Scale to handle multiple concurrent disruptions
- **Edge Deployment**: Run RL models on airport systems
- **Federated Learning**: Train on data from multiple airlines (privacy-preserving)
- **Real-time Adaptation**: Online learning from live operations

## 11. Research Applications

The RL environment serves as a research platform for:

- **AI Safety**: Studying safe decision-making in critical systems
- **Explainable AI**: Making RL decisions interpretable for humans
- **Multi-Objective Optimization**: Balancing competing business objectives
- **Robustness**: Handling uncertainty in complex operational environments

This production-ready RL system transforms disruption recovery from reactive problem-solving to proactive, optimized decision-making that learns and improves over time.