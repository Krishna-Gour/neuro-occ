# Documentation: Mamba Predictive Maintenance - Fleet Health Monitoring

## 1. Purpose: Proactive Aircraft Maintenance

In airline operations, unexpected aircraft maintenance issues are a major source of disruptions. Traditional maintenance schedules are reactive or based on fixed intervals, but modern aircraft generate vast amounts of sensor data that can predict failures before they occur.

The **Mamba Predictive Maintenance** component uses State Space Models (SSMs) to analyze high-frequency sensor data from aircraft systems. This allows Neuro-OCC to assess fleet health in real-time and preemptively identify aircraft that might need maintenance, preventing delays and cancellations.

## 2. Why Mamba SSMs?

State Space Models like Mamba are particularly well-suited for time-series prediction tasks because:

*   **Efficiency**: They can process long sequences of sensor data with linear complexity, making them suitable for real-time monitoring.
*   **Memory**: They maintain state across time steps, capturing temporal dependencies in sensor readings.
*   **Scalability**: They can handle multiple sensor inputs simultaneously (vibration, temperature, pressure, etc.).

## 3. Key Components

*   **`brain/mamba_sentinel.py`**: Contains the `SimpleMambaSimulator` class, which implements a simplified Mamba-like model using PyTorch. This serves as a proof-of-concept for predictive maintenance.
*   **`brain/sentinel_Mamba.py`**: Implements a more advanced Mamba model using the `mamba_ssm` library, providing a production-ready SSM for sequence modeling.

## 4. How It Works

### Sensor Data Ingestion
The system assumes access to high-frequency sensor data from aircraft systems:
- Vibration sensors
- Temperature readings
- Pressure measurements
- Engine performance metrics
- Hydraulic system data

### Model Architecture

#### SimpleMambaSimulator
```python
class SimpleMambaSimulator(nn.Module):
    def __init__(self, input_dim=10, hidden_dim=32):
        super(SimpleMambaSimulator, self).__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
```

This simplified version uses a GRU (Gated Recurrent Unit) as a proxy for Mamba's state space operations. It processes sequences of sensor data and outputs a health score between 0 and 1.

#### SentinelMamba
```python
class SentinelMamba(nn.Module):
    def __init__(self, d_model, d_state, d_conv, expand, num_classes):
        super(SentinelMamba, self).__init__()
        self.mamba = Mamba(d_model=d_model, d_state=d_state, d_conv=d_conv, expand=expand)
        self.fc = nn.Linear(d_model, num_classes)
```

This uses the actual Mamba SSM implementation for more accurate modeling.

### Health Score Calculation
The model processes a sequence of sensor readings and outputs a health score:
- **1.0**: Aircraft is in perfect health
- **0.0**: Immediate maintenance required
- **0.5-0.8**: Monitor closely

### Integration with Neuro-OCC
When a disruption occurs:
1. The Mamba agent queries sensor data for all aircraft in the affected routes
2. It computes health scores for each aircraft
3. Aircraft with low health scores are flagged for potential maintenance-related delays
4. The Neuro-Symbolic agent considers this information when proposing recovery plans

## 5. Usage Example

```python
from brain.mamba_sentinel import get_health_score

# Get health score for aircraft VT-I01
score = get_health_score("VT-I01", sensor_history_data)
print(f"Aircraft health score: {score:.3f}")
```

## 6. Future Enhancements

*   **Real Sensor Integration**: Connect to actual aircraft telemetry systems
*   **Multi-Modal Inputs**: Incorporate maintenance logs, flight history, and weather data
*   **Anomaly Detection**: Beyond health scoring, detect specific failure modes
*   **Edge Deployment**: Run models on aircraft systems for real-time monitoring

## 7. Dependencies

*   `torch`: PyTorch for neural network operations
*   `mamba_ssm`: Official Mamba SSM implementation (for SentinelMamba)