"""
Training Script for RL Agent in Neuro-OCC

This script trains a Reinforcement Learning agent using the AirlineRecoveryEnv
environment. Once trained, the model can be integrated into brain_api.py to
generate optimized recovery proposals.

Requirements:
    pip install stable-baselines3 gymnasium torch tensorboard

Usage:
    python scripts/train_rl_agent.py
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from brain.recovery_env import AirlineRecoveryEnv
import torch
from loguru import logger

def make_env():
    """Create and wrap the environment"""
    def _init():
        return AirlineRecoveryEnv()
    return _init

def train_ppo_agent(total_timesteps=100000, save_path="models/rl_recovery_ppo"):
    """
    Train a PPO agent for airline recovery optimization
    
    PPO (Proximal Policy Optimization) is good for:
    - Continuous improvement
    - Stable training
    - Complex action spaces
    """
    logger.info("Starting PPO training...")
    
    # Create vectorized environment
    env = DummyVecEnv([make_env()])
    
    # Create callbacks
    os.makedirs("models/checkpoints", exist_ok=True)
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="models/checkpoints",
        name_prefix="rl_recovery_ppo"
    )
    
    eval_env = DummyVecEnv([make_env()])
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="models/best",
        log_path="models/logs",
        eval_freq=5000,
        deterministic=True,
        render=False
    )
    
    # Initialize PPO agent
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
        verbose=1,
        tensorboard_log="./tensorboard_logs/"
    )
    
    # Train the agent
    logger.info(f"Training for {total_timesteps} timesteps...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=[checkpoint_callback, eval_callback]
    )
    
    # Save the final model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    logger.info(f"Model saved to {save_path}")
    
    return model

def train_dqn_agent(total_timesteps=100000, save_path="models/rl_recovery_dqn"):
    """
    Train a DQN agent for airline recovery optimization
    
    DQN (Deep Q-Network) is good for:
    - Discrete action spaces
    - Value-based learning
    - Sample efficiency
    """
    logger.info("Starting DQN training...")
    
    # Create environment
    env = AirlineRecoveryEnv()
    
    # Create callbacks
    os.makedirs("models/checkpoints", exist_ok=True)
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="models/checkpoints",
        name_prefix="rl_recovery_dqn"
    )
    
    # Initialize DQN agent
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-4,
        buffer_size=50000,
        learning_starts=1000,
        batch_size=32,
        tau=1.0,
        gamma=0.99,
        train_freq=4,
        gradient_steps=1,
        target_update_interval=1000,
        exploration_fraction=0.1,
        exploration_final_eps=0.05,
        verbose=1,
        tensorboard_log="./tensorboard_logs/"
    )
    
    # Train the agent
    logger.info(f"Training for {total_timesteps} timesteps...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=checkpoint_callback
    )
    
    # Save the final model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    logger.info(f"Model saved to {save_path}")
    
    return model

def test_trained_model(model_path, num_episodes=10):
    """Test a trained model and report performance"""
    logger.info(f"Testing model from {model_path}")
    
    # Determine model type from path
    if "ppo" in model_path.lower():
        model = PPO.load(model_path)
    elif "dqn" in model_path.lower():
        model = DQN.load(model_path)
    else:
        raise ValueError("Unknown model type. Use 'ppo' or 'dqn' in filename")
    
    env = AirlineRecoveryEnv()
    
    total_rewards = []
    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            done = done or truncated
        
        total_rewards.append(episode_reward)
        logger.info(f"Episode {episode + 1}: Reward = {episode_reward:.2f}")
    
    avg_reward = sum(total_rewards) / len(total_rewards)
    logger.info(f"\nAverage Reward over {num_episodes} episodes: {avg_reward:.2f}")
    
    return avg_reward

def main():
    """Main training workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train RL agent for airline recovery")
    parser.add_argument("--algorithm", type=str, default="ppo", choices=["ppo", "dqn"],
                      help="RL algorithm to use")
    parser.add_argument("--timesteps", type=int, default=100000,
                      help="Total training timesteps")
    parser.add_argument("--test", type=str, default=None,
                      help="Path to trained model to test")
    
    args = parser.parse_args()
    
    if args.test:
        # Test existing model
        test_trained_model(args.test)
    else:
        # Train new model
        if args.algorithm == "ppo":
            model = train_ppo_agent(total_timesteps=args.timesteps)
        elif args.algorithm == "dqn":
            model = train_dqn_agent(total_timesteps=args.timesteps)
        
        # Test the trained model
        logger.info("\nTesting trained model...")
        model_path = f"models/rl_recovery_{args.algorithm}"
        test_trained_model(model_path)

if __name__ == "__main__":
    logger.add("rl_training.log", rotation="10 MB")
    logger.info("="*50)
    logger.info("RL Agent Training for Neuro-OCC")
    logger.info("="*50)
    
    main()
