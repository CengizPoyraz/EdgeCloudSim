#!/usr/bin/env python3
"""
Energy-Aware Task Offloading with Deadline Constraints
EdgeCloudSim-compatible Simulation Implementation

This Python implementation simulates the energy-aware task offloading problem
with the same logic as the Java implementation, providing immediate results
for analysis and visualization.

Engineering Problem: Mobile devices have limited battery life, but applications 
increasingly require computational resources. We need to balance:
- Energy consumption on mobile devices
- Meeting application deadlines  
- Efficient use of edge server resources

Author: EdgeCloudSim Energy-Aware Scenario
"""

import numpy as np
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json
import os

# ============================================================================
# Configuration Constants (matching EdgeCloudSim parameters)
# ============================================================================

class DeviceType(Enum):
    MOBILE = 0
    EDGE = 1
    CLOUD = 2

@dataclass
class SimulationConfig:
    """Simulation configuration parameters"""
    simulation_time: float = 1200.0  # 20 minutes in seconds
    warm_up_period: float = 120.0    # 2 minutes warm-up
    
    # Mobile device power consumption (Watts)
    mobile_power_idle: float = 0.5
    mobile_power_active: float = 2.5
    mobile_power_transmit: float = 1.5
    
    # Processing capabilities (MIPS)
    mobile_mips: float = 1000.0
    edge_mips: float = 10000.0
    cloud_mips: float = 40000.0
    
    # Network configuration (Mbps)
    wlan_bandwidth: float = 100.0
    wan_bandwidth: float = 50.0
    wan_propagation_delay: float = 0.1
    
    # Edge infrastructure
    num_edge_servers: int = 5
    vms_per_edge_server: int = 2
    
    # EADC algorithm parameters
    alpha: float = 0.5  # Weight for time objective
    beta: float = 0.5   # Weight for energy objective

@dataclass
class ApplicationType:
    """Application type with characteristics"""
    name: str
    usage_percentage: float
    delay_sensitivity: float
    max_delay_requirement: float
    poisson_interarrival: float
    data_upload: float    # KB
    data_download: float  # KB
    task_length: float    # Million Instructions

# Define application types matching EdgeCloudSim configuration
APPLICATION_TYPES = [
    ApplicationType("REALTIME_AR", 30, 0.9, 0.1, 2, 50, 100, 500),
    ApplicationType("INTERACTIVE_GAMING", 25, 0.7, 0.3, 3, 30, 80, 800),
    ApplicationType("IMAGE_PROCESSING", 25, 0.4, 1.0, 5, 200, 50, 2000),
    ApplicationType("DATA_SYNC", 20, 0.2, 3.0, 10, 500, 100, 500)
]

@dataclass
class Task:
    """Represents a computational task"""
    task_id: int
    mobile_device_id: int
    app_type: ApplicationType
    creation_time: float
    task_length: float       # MI
    input_size: float        # KB
    output_size: float       # KB
    deadline: float          # seconds
    delay_sensitivity: float
    
    # Results
    offload_decision: Optional[DeviceType] = None
    start_time: Optional[float] = None
    finish_time: Optional[float] = None
    service_time: Optional[float] = None
    energy_consumed: Optional[float] = None
    deadline_met: Optional[bool] = None
    failed: bool = False

@dataclass
class EdgeServer:
    """Edge server with utilization tracking"""
    server_id: int
    current_utilization: float = 0.0
    tasks_in_queue: int = 0

@dataclass
class SimulationResults:
    """Stores simulation results for analysis"""
    policy: str
    num_devices: int
    iteration: int
    
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    
    avg_service_time: float = 0.0
    avg_energy_consumption: float = 0.0
    deadline_satisfaction_rate: float = 0.0
    avg_edge_utilization: float = 0.0
    
    local_executions: int = 0
    edge_executions: int = 0
    cloud_executions: int = 0
    
    # Per-application type metrics
    app_type_metrics: Dict = field(default_factory=dict)

# ============================================================================
# Task Offloading Algorithms
# ============================================================================

class OffloadingAlgorithm:
    """Base class for offloading algorithms"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        
    def decide(self, task: Task, edge_servers: List[EdgeServer]) -> DeviceType:
        raise NotImplementedError
    
    def calculate_local_energy(self, task_length: float) -> float:
        """Calculate energy for local execution"""
        execution_time = task_length / self.config.mobile_mips
        return self.config.mobile_power_active * execution_time
    
    def calculate_offload_energy(self, data_size: float, task_length: float, is_cloud: bool = False) -> float:
        """Calculate energy for offloading (transmission + idle waiting)"""
        bandwidth = self.config.wan_bandwidth if is_cloud else self.config.wlan_bandwidth
        transmission_time = (data_size * 8) / (bandwidth * 1000)  # Convert to seconds
        
        processing_mips = self.config.cloud_mips if is_cloud else self.config.edge_mips
        idle_time = task_length / processing_mips
        
        return self.config.mobile_power_transmit * transmission_time + self.config.mobile_power_idle * idle_time
    
    def estimate_local_time(self, task: Task) -> float:
        """Estimate local execution time"""
        return task.task_length / self.config.mobile_mips
    
    def estimate_edge_time(self, task: Task, edge_servers: List[EdgeServer]) -> float:
        """Estimate edge execution time including transmission and queuing"""
        data_size = task.input_size + task.output_size
        transmission_delay = (data_size * 8) / (self.config.wlan_bandwidth * 1000)
        processing_time = task.task_length / self.config.edge_mips
        
        avg_utilization = np.mean([s.current_utilization for s in edge_servers])
        queuing_delay = (avg_utilization / 100) * processing_time * 0.5
        
        return transmission_delay + processing_time + queuing_delay
    
    def estimate_cloud_time(self, task: Task) -> float:
        """Estimate cloud execution time including WAN delay"""
        data_size = task.input_size + task.output_size
        transmission_delay = (data_size * 8) / (self.config.wan_bandwidth * 1000) + self.config.wan_propagation_delay * 2
        processing_time = task.task_length / self.config.cloud_mips
        
        return transmission_delay + processing_time


class RandomAlgorithm(OffloadingAlgorithm):
    """Random offloading decision"""
    
    def decide(self, task: Task, edge_servers: List[EdgeServer]) -> DeviceType:
        r = random.random()
        if r < 0.33:
            return DeviceType.MOBILE
        elif r < 0.66:
            return DeviceType.EDGE
        else:
            return DeviceType.CLOUD


class GreedyEnergyAlgorithm(OffloadingAlgorithm):
    """Greedy algorithm prioritizing energy minimization"""
    
    def decide(self, task: Task, edge_servers: List[EdgeServer]) -> DeviceType:
        data_size = task.input_size + task.output_size
        
        local_energy = self.calculate_local_energy(task.task_length)
        edge_energy = self.calculate_offload_energy(data_size, task.task_length, is_cloud=False)
        cloud_energy = self.calculate_offload_energy(data_size * 1.5, task.task_length, is_cloud=True)
        
        energies = {
            DeviceType.MOBILE: local_energy,
            DeviceType.EDGE: edge_energy,
            DeviceType.CLOUD: cloud_energy
        }
        
        # Return the option with minimum energy
        return min(energies, key=energies.get)


class GreedyDeadlineAlgorithm(OffloadingAlgorithm):
    """Greedy algorithm prioritizing deadline satisfaction"""
    
    def decide(self, task: Task, edge_servers: List[EdgeServer]) -> DeviceType:
        local_time = self.estimate_local_time(task)
        edge_time = self.estimate_edge_time(task, edge_servers)
        cloud_time = self.estimate_cloud_time(task)
        
        times = {
            DeviceType.MOBILE: local_time,
            DeviceType.EDGE: edge_time,
            DeviceType.CLOUD: cloud_time
        }
        
        # Filter options that meet deadline, prefer fastest
        deadline_options = {k: v for k, v in times.items() if v <= task.deadline}
        
        if deadline_options:
            return min(deadline_options, key=deadline_options.get)
        else:
            # If no option meets deadline, return fastest
            return min(times, key=times.get)


class EdgeOnlyAlgorithm(OffloadingAlgorithm):
    """Always offload to edge"""
    
    def decide(self, task: Task, edge_servers: List[EdgeServer]) -> DeviceType:
        avg_utilization = np.mean([s.current_utilization for s in edge_servers])
        if avg_utilization > 95:
            return DeviceType.CLOUD  # Fallback to cloud if edge overloaded
        return DeviceType.EDGE


class EADCAlgorithm(OffloadingAlgorithm):
    """
    Energy-Aware Deadline-Constrained (EADC) Algorithm
    
    This is our proposed algorithm that intelligently balances:
    1. Energy consumption on mobile devices
    2. Meeting application deadlines
    3. Edge server resource utilization
    
    Key Features:
    - Adaptive weighting based on delay sensitivity
    - Utility function combining time and energy objectives
    - Load-aware edge server selection
    - Fallback strategy when no option meets deadline
    """
    
    def decide(self, task: Task, edge_servers: List[EdgeServer]) -> DeviceType:
        data_size = task.input_size + task.output_size
        
        # Estimate execution times
        local_time = self.estimate_local_time(task)
        edge_time = self.estimate_edge_time(task, edge_servers)
        cloud_time = self.estimate_cloud_time(task)
        
        # Calculate energy consumption
        local_energy = self.calculate_local_energy(task.task_length)
        edge_energy = self.calculate_offload_energy(data_size, task.task_length, is_cloud=False)
        cloud_energy = self.calculate_offload_energy(data_size * 1.5, task.task_length, is_cloud=True)
        
        # Check deadline constraints
        deadline = task.deadline
        local_meets_deadline = local_time <= deadline
        edge_meets_deadline = edge_time <= deadline
        cloud_meets_deadline = cloud_time <= deadline
        
        # Adaptive weights based on delay sensitivity
        adaptive_alpha = self.config.alpha * (1 + task.delay_sensitivity)
        adaptive_beta = self.config.beta * (1 - task.delay_sensitivity)
        
        # Calculate utility scores (lower is better)
        def calculate_score(time, energy, meets_deadline):
            if not meets_deadline:
                return float('inf')
            normalized_time = time / deadline
            max_energy = self.config.mobile_power_active * 10
            normalized_energy = energy / max_energy
            return adaptive_alpha * normalized_time + adaptive_beta * normalized_energy
        
        local_score = calculate_score(local_time, local_energy, local_meets_deadline)
        edge_score = calculate_score(edge_time, edge_energy, edge_meets_deadline)
        cloud_score = calculate_score(cloud_time, cloud_energy, cloud_meets_deadline)
        
        # Apply load-balancing penalty for edge
        avg_utilization = np.mean([s.current_utilization for s in edge_servers])
        if avg_utilization > 85:
            edge_score *= (1 + (avg_utilization - 85) / 100)
        
        scores = {
            DeviceType.MOBILE: local_score,
            DeviceType.EDGE: edge_score,
            DeviceType.CLOUD: cloud_score
        }
        
        # Select option with best score
        best_option = min(scores, key=scores.get)
        
        # Fallback if no option meets deadline
        if scores[best_option] == float('inf'):
            times = {DeviceType.MOBILE: local_time, DeviceType.EDGE: edge_time, DeviceType.CLOUD: cloud_time}
            best_option = min(times, key=times.get)
        
        return best_option


# ============================================================================
# Simulation Engine
# ============================================================================

class EnergyAwareSimulator:
    """Main simulation engine"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.algorithms = {
            "RANDOM": RandomAlgorithm(config),
            "GREEDY_ENERGY": GreedyEnergyAlgorithm(config),
            "GREEDY_DEADLINE": GreedyDeadlineAlgorithm(config),
            "EDGE_ONLY": EdgeOnlyAlgorithm(config),
            "EADC": EADCAlgorithm(config)
        }
    
    def generate_tasks(self, num_devices: int, duration: float) -> List[Task]:
        """Generate tasks based on application mix and Poisson arrivals"""
        tasks = []
        task_id = 0
        
        # Assign applications to devices
        device_apps = {}
        for device_id in range(num_devices):
            r = random.random() * 100
            cumulative = 0
            for app_type in APPLICATION_TYPES:
                cumulative += app_type.usage_percentage
                if r <= cumulative:
                    device_apps[device_id] = app_type
                    break
        
        # Generate tasks for each device
        for device_id, app_type in device_apps.items():
            current_time = random.random() * app_type.poisson_interarrival
            
            while current_time < duration:
                # Add some variation to task parameters
                task_length = app_type.task_length * (0.8 + random.random() * 0.4)
                input_size = app_type.data_upload * (0.8 + random.random() * 0.4)
                output_size = app_type.data_download * (0.8 + random.random() * 0.4)
                deadline = app_type.max_delay_requirement * (0.9 + random.random() * 0.2)
                
                task = Task(
                    task_id=task_id,
                    mobile_device_id=device_id,
                    app_type=app_type,
                    creation_time=current_time,
                    task_length=task_length,
                    input_size=input_size,
                    output_size=output_size,
                    deadline=deadline,
                    delay_sensitivity=app_type.delay_sensitivity
                )
                tasks.append(task)
                task_id += 1
                
                # Poisson inter-arrival time
                interarrival = -app_type.poisson_interarrival * np.log(1 - random.random())
                current_time += max(0.1, interarrival)
        
        # Sort tasks by creation time
        tasks.sort(key=lambda t: t.creation_time)
        return tasks
    
    def execute_task(self, task: Task, decision: DeviceType, edge_servers: List[EdgeServer], 
                    algorithm: OffloadingAlgorithm) -> Task:
        """Execute a task and calculate metrics"""
        task.offload_decision = decision
        task.start_time = task.creation_time
        
        data_size = task.input_size + task.output_size
        
        if decision == DeviceType.MOBILE:
            # Local execution
            service_time = algorithm.estimate_local_time(task)
            energy = algorithm.calculate_local_energy(task.task_length)
            
        elif decision == DeviceType.EDGE:
            # Edge execution
            service_time = algorithm.estimate_edge_time(task, edge_servers)
            energy = algorithm.calculate_offload_energy(data_size, task.task_length, is_cloud=False)
            
            # Update edge server utilization
            server_idx = random.randint(0, len(edge_servers) - 1)
            edge_servers[server_idx].current_utilization = min(100, 
                edge_servers[server_idx].current_utilization + random.random() * 5)
            
        else:  # CLOUD
            # Cloud execution
            service_time = algorithm.estimate_cloud_time(task)
            energy = algorithm.calculate_offload_energy(data_size * 1.5, task.task_length, is_cloud=True)
        
        # Add some randomness to simulate real conditions
        service_time *= (0.9 + random.random() * 0.2)
        energy *= (0.9 + random.random() * 0.2)
        
        task.service_time = service_time
        task.energy_consumed = energy
        task.finish_time = task.start_time + service_time
        task.deadline_met = service_time <= task.deadline
        
        # Simulate task failure probability (higher under load)
        avg_util = np.mean([s.current_utilization for s in edge_servers])
        failure_prob = 0.01 + (avg_util / 100) * 0.05
        if random.random() < failure_prob:
            task.failed = True
        
        return task
    
    def run_simulation(self, policy: str, num_devices: int, iteration: int) -> SimulationResults:
        """Run a single simulation"""
        algorithm = self.algorithms[policy]
        
        # Initialize edge servers
        edge_servers = [EdgeServer(i) for i in range(self.config.num_edge_servers)]
        
        # Generate tasks
        tasks = self.generate_tasks(num_devices, self.config.simulation_time)
        
        # Process tasks
        for task in tasks:
            # Skip warm-up period tasks for statistics
            if task.creation_time < self.config.warm_up_period:
                continue
            
            # Make offloading decision
            decision = algorithm.decide(task, edge_servers)
            
            # Execute task
            self.execute_task(task, decision, edge_servers, algorithm)
            
            # Decay edge utilization over time
            for server in edge_servers:
                server.current_utilization = max(0, server.current_utilization - random.random() * 2)
        
        # Calculate results (excluding warm-up period)
        valid_tasks = [t for t in tasks if t.creation_time >= self.config.warm_up_period and t.offload_decision is not None]
        
        results = SimulationResults(
            policy=policy,
            num_devices=num_devices,
            iteration=iteration
        )
        
        if valid_tasks:
            completed_tasks = [t for t in valid_tasks if not t.failed]
            failed_tasks = [t for t in valid_tasks if t.failed]
            
            results.total_tasks = len(valid_tasks)
            results.completed_tasks = len(completed_tasks)
            results.failed_tasks = len(failed_tasks)
            
            if completed_tasks:
                results.avg_service_time = np.mean([t.service_time for t in completed_tasks])
                results.avg_energy_consumption = np.mean([t.energy_consumed for t in completed_tasks])
                results.deadline_satisfaction_rate = np.mean([1 if t.deadline_met else 0 for t in completed_tasks])
            
            results.avg_edge_utilization = np.mean([s.current_utilization for s in edge_servers])
            
            results.local_executions = sum(1 for t in valid_tasks if t.offload_decision == DeviceType.MOBILE)
            results.edge_executions = sum(1 for t in valid_tasks if t.offload_decision == DeviceType.EDGE)
            results.cloud_executions = sum(1 for t in valid_tasks if t.offload_decision == DeviceType.CLOUD)
            
            # Per-application metrics
            for app_type in APPLICATION_TYPES:
                app_tasks = [t for t in completed_tasks if t.app_type.name == app_type.name]
                if app_tasks:
                    results.app_type_metrics[app_type.name] = {
                        'count': len(app_tasks),
                        'avg_service_time': np.mean([t.service_time for t in app_tasks]),
                        'avg_energy': np.mean([t.energy_consumed for t in app_tasks]),
                        'deadline_rate': np.mean([1 if t.deadline_met else 0 for t in app_tasks])
                    }
        
        return results


def run_full_simulation(iterations: int = 10, device_counts: List[int] = None):
    """Run complete simulation suite"""
    if device_counts is None:
        device_counts = [100, 200, 300, 400, 500]
    
    policies = ["EADC", "GREEDY_ENERGY", "GREEDY_DEADLINE", "RANDOM", "EDGE_ONLY"]
    
    config = SimulationConfig()
    simulator = EnergyAwareSimulator(config)
    
    all_results = []
    
    print("="*70)
    print("Energy-Aware Task Offloading Simulation")
    print("="*70)
    print(f"Simulation time: {config.simulation_time/60:.0f} minutes")
    print(f"Warm-up period: {config.warm_up_period/60:.0f} minutes")
    print(f"Iterations per configuration: {iterations}")
    print(f"Device counts: {device_counts}")
    print(f"Policies: {policies}")
    print("="*70)
    
    for num_devices in device_counts:
        print(f"\nRunning simulations for {num_devices} devices...")
        
        for policy in policies:
            policy_results = []
            
            for i in range(iterations):
                result = simulator.run_simulation(policy, num_devices, i+1)
                policy_results.append(result)
            
            # Average results across iterations
            avg_result = SimulationResults(
                policy=policy,
                num_devices=num_devices,
                iteration=0  # Averaged
            )
            
            avg_result.total_tasks = int(np.mean([r.total_tasks for r in policy_results]))
            avg_result.completed_tasks = int(np.mean([r.completed_tasks for r in policy_results]))
            avg_result.failed_tasks = int(np.mean([r.failed_tasks for r in policy_results]))
            avg_result.avg_service_time = np.mean([r.avg_service_time for r in policy_results])
            avg_result.avg_energy_consumption = np.mean([r.avg_energy_consumption for r in policy_results])
            avg_result.deadline_satisfaction_rate = np.mean([r.deadline_satisfaction_rate for r in policy_results])
            avg_result.avg_edge_utilization = np.mean([r.avg_edge_utilization for r in policy_results])
            avg_result.local_executions = int(np.mean([r.local_executions for r in policy_results]))
            avg_result.edge_executions = int(np.mean([r.edge_executions for r in policy_results]))
            avg_result.cloud_executions = int(np.mean([r.cloud_executions for r in policy_results]))
            
            all_results.append(avg_result)
            
            print(f"  {policy}: Service={avg_result.avg_service_time:.3f}s, "
                  f"Energy={avg_result.avg_energy_consumption:.3f}J, "
                  f"Deadline={avg_result.deadline_satisfaction_rate*100:.1f}%")
    
    return all_results


def save_results(results: List[SimulationResults], output_dir: str):
    """Save results to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    results_data = []
    for r in results:
        results_data.append({
            'policy': r.policy,
            'num_devices': r.num_devices,
            'total_tasks': r.total_tasks,
            'completed_tasks': r.completed_tasks,
            'failed_tasks': r.failed_tasks,
            'avg_service_time': r.avg_service_time,
            'avg_energy_consumption': r.avg_energy_consumption,
            'deadline_satisfaction_rate': r.deadline_satisfaction_rate,
            'avg_edge_utilization': r.avg_edge_utilization,
            'local_executions': r.local_executions,
            'edge_executions': r.edge_executions,
            'cloud_executions': r.cloud_executions
        })
    
    with open(os.path.join(output_dir, 'simulation_results.json'), 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\nResults saved to {output_dir}/simulation_results.json")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Energy-Aware Task Offloading Simulation')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations')
    parser.add_argument('--output', type=str, default='../output', help='Output directory')
    
    args = parser.parse_args()
    
    results = run_full_simulation(iterations=args.iterations)
    save_results(results, args.output)
