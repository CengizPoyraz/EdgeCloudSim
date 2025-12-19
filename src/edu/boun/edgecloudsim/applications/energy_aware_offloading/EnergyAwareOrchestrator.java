package edu.boun.edgecloudsim.applications.energy_aware_offloading;

import java.util.List;

import org.cloudbus.cloudsim.Vm;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.core.SimEvent;

import edu.boun.edgecloudsim.core.SimManager;
import edu.boun.edgecloudsim.core.SimSettings;
import edu.boun.edgecloudsim.edge_orchestrator.EdgeOrchestrator;
import edu.boun.edgecloudsim.edge_client.Task;

/**
 * Energy-Aware Edge Orchestrator
 * Implements three offloading strategies
 */
public class EnergyAwareOrchestrator extends EdgeOrchestrator {
    
    private static final String BASELINE = "BASELINE";
    private static final String GREEDY = "GREEDY";
    private static final String ENERGY_AWARE = "ENERGY_AWARE";
    
    // Energy model parameters (Joules per instruction)
    private static final double LOCAL_ENERGY_PER_MI = 0.0001;
    private static final double EDGE_ENERGY_PER_MI = 0.00001;
    private static final double TRANSMISSION_ENERGY_PER_MB = 0.05;
    
    // Load thresholds
    private static final double HIGH_LOAD_THRESHOLD = 0.8;
    private static final double MEDIUM_LOAD_THRESHOLD = 0.5;
    
    private String policy;
    
    public EnergyAwareOrchestrator(String policy, String simScenario) {
        super(policy, simScenario);
        this.policy = policy;
    }
    
    @Override
    public void initialize() {
        // Initialization complete
    }
    
    @Override
    public int getDeviceToOffload(Task task) {
        // Apply strategy based on policy
        if (policy.equals(BASELINE)) {
            return baselineOffloading(task);
        } else if (policy.equals(GREEDY)) {
            return greedyOffloading(task);
        } else if (policy.equals(ENERGY_AWARE)) {
            return energyAwareOffloading(task);
        } else {
            return baselineOffloading(task);
        }
    }
    
    /**
     * BASELINE: Random 50-50 offloading
     */
    private int baselineOffloading(Task task) {
        if (Math.random() < 0.5) {
            return SimSettings.MOBILE_DATACENTER_ID;
        } else {
            return SimSettings.GENERIC_EDGE_DEVICE_ID;
        }
    }
    
    /**
     * GREEDY: Always offload to edge
     */
    private int greedyOffloading(Task task) {
        return SimSettings.GENERIC_EDGE_DEVICE_ID;
    }
    
    /**
     * ENERGY_AWARE: Intelligent offloading algorithm (OUR PROPOSAL)
     */
    private int energyAwareOffloading(Task task) {
        
        // Get task properties from Task object
        double taskLength = task.getCloudletLength();
        double inputSize = task.getCloudletFileSize();
        double outputSize = task.getCloudletOutputSize();
        // Use task's creation time as deadline constraint (10 second deadline from creation)
        double deadline = 10.0;
        
        // Calculate local execution cost
        double localEnergy = calculateLocalEnergy(taskLength);
        double localTime = estimateLocalExecutionTime(taskLength);
        
        // Calculate edge execution cost
        double edgeEnergy = calculateEdgeEnergy(taskLength, inputSize, outputSize);
        double edgeTime = estimateEdgeExecutionTime(taskLength, inputSize, outputSize);
        
        // Check deadline feasibility
        boolean localMeetsDeadline = (localTime <= deadline);
        boolean edgeMeetsDeadline = (edgeTime <= deadline);
        
        // Get edge server load
        double edgeLoad = getEdgeServerLoad();
        
        // Decision logic
        
        // Rule 1: If only one option meets deadline, choose it
        if (localMeetsDeadline && !edgeMeetsDeadline) {
            return SimSettings.MOBILE_DATACENTER_ID;
        }
        if (!localMeetsDeadline && edgeMeetsDeadline) {
            return SimSettings.GENERIC_EDGE_DEVICE_ID;
        }
        
        // Rule 2: If neither meets deadline, choose faster option
        if (!localMeetsDeadline && !edgeMeetsDeadline) {
            return (localTime < edgeTime) ? 
                SimSettings.MOBILE_DATACENTER_ID : 
                SimSettings.GENERIC_EDGE_DEVICE_ID;
        }
        
        // Rule 3: Both meet deadline - consider energy and load
        
        // If edge is heavily loaded, prefer local unless big energy savings
        if (edgeLoad > HIGH_LOAD_THRESHOLD) {
            if (edgeEnergy < localEnergy * 0.7) {
                return SimSettings.GENERIC_EDGE_DEVICE_ID;
            } else {
                return SimSettings.MOBILE_DATACENTER_ID;
            }
        }
        
        // If edge is moderately loaded
        if (edgeLoad > MEDIUM_LOAD_THRESHOLD) {
            if (edgeEnergy < localEnergy * 0.8) {
                return SimSettings.GENERIC_EDGE_DEVICE_ID;
            } else {
                return SimSettings.MOBILE_DATACENTER_ID;
            }
        }
        
        // Low load - choose most energy efficient
        return (edgeEnergy < localEnergy) ? 
            SimSettings.GENERIC_EDGE_DEVICE_ID : 
            SimSettings.MOBILE_DATACENTER_ID;
    }
    
    private double calculateLocalEnergy(double taskLength) {
        return taskLength * LOCAL_ENERGY_PER_MI;
    }
    
    private double calculateEdgeEnergy(double taskLength, double inputSize, double outputSize) {
        double processingEnergy = taskLength * EDGE_ENERGY_PER_MI;
        double transmissionEnergy = (inputSize + outputSize) * TRANSMISSION_ENERGY_PER_MB;
        return processingEnergy + transmissionEnergy;
    }
    
    private double estimateLocalExecutionTime(double taskLength) {
        double mobileMips = SimSettings.getInstance().getMipsForMobileVM();
        return taskLength / mobileMips;
    }
    
    private double estimateEdgeExecutionTime(double taskLength, double inputSize, double outputSize) {
        double edgeMips = SimSettings.getInstance().getMipsForMobileVM();
        double processingTime = taskLength / edgeMips;
        
        double wlanBandwidth = SimSettings.getInstance().getWlanBandwidth();
        double networkDelay = (inputSize + outputSize) / (wlanBandwidth * 1024.0 / 8.0);
        
        return processingTime + networkDelay;
    }
    
    private double getEdgeServerLoad() {
        try {
            SimManager simManager = SimManager.getInstance();
            if (simManager == null) {
                return 0.5; // Default to medium load
            }
            
            // Get list of VMs from edge server manager
            List<?> vmList = simManager.getEdgeServerManager().getVmList(0);
            
            if (vmList == null || vmList.isEmpty()) {
                return 0.0;
            }
            
            double totalUtilization = 0.0;
            int edgeVmCount = 0;
            
            for (Object vmObj : vmList) {
                if (vmObj instanceof Vm) {
                    Vm vm = (Vm) vmObj;
                    if (vm != null && vm.getHost() != null) {
                        double vmMips = vm.getMips();
                        
                        if (vmMips > 0) {
                            // Calculate utilization based on running cloudlets
                            double utilizationRatio = vm.getCloudletScheduler().getTotalUtilizationOfCpu(CloudSim.clock()) / vm.getNumberOfPes();
                            totalUtilization += utilizationRatio;
                            edgeVmCount++;
                        }
                    }
                }
            }
            
            return edgeVmCount > 0 ? totalUtilization / edgeVmCount : 0.0;
            
        } catch (Exception e) {
            return 0.5; // Default to medium load if error
        }
    }
    
    @Override
    public Vm getVmToOffload(Task task, int deviceId) {
        return null;
    }
    
    @Override
    public void processEvent(SimEvent ev) {
    }
    
    @Override
    public void shutdownEntity() {
    }
    
    @Override
    public void startEntity() {
    }
}