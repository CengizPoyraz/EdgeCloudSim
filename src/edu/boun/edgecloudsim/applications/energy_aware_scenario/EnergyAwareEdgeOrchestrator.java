package edu.boun.edgecloudsim.applications.energy_aware_scenario;

import java.util.List;

import org.cloudbus.cloudsim.Host;
import org.cloudbus.cloudsim.UtilizationModelFull;
import org.cloudbus.cloudsim.Vm;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.core.SimEvent;

import edu.boun.edgecloudsim.cloud_server.CloudVM;
import edu.boun.edgecloudsim.core.SimManager;
import edu.boun.edgecloudsim.core.SimSettings;
import edu.boun.edgecloudsim.edge_orchestrator.EdgeOrchestrator;
import edu.boun.edgecloudsim.edge_server.EdgeVM;
import edu.boun.edgecloudsim.edge_client.CpuUtilizationModel_Custom;
import edu.boun.edgecloudsim.edge_client.Task;
import edu.boun.edgecloudsim.utils.SimLogger;

public class EnergyAwareEdgeOrchestrator extends EdgeOrchestrator {
    
    private int numberOfHost;
    
    private static final double MOBILE_POWER_IDLE = 0.5;
    private static final double MOBILE_POWER_ACTIVE = 2.5;
    private static final double MOBILE_POWER_TRANSMIT = 1.5;
    
    private static final double EDGE_MIPS = 10000;
    private static final double MOBILE_MIPS = 1000;
    
    private static final double ALPHA = 0.5;
    private static final double BETA = 0.5;
    
    public EnergyAwareEdgeOrchestrator(String _policy, String _simScenario) {
        super(_policy, _simScenario);
    }

    @Override
    public void initialize() {
        numberOfHost = SimSettings.getInstance().getNumOfEdgeHosts();
    }

    @Override
    public int getDeviceToOffload(Task task) {
        int result = SimSettings.GENERIC_EDGE_DEVICE_ID;
        
        if(policy.equals("RANDOM")) {
            result = getRandomDecision(task);
        }
        else if(policy.equals("GREEDY_ENERGY")) {
            result = getGreedyEnergyDecision(task);
        }
        else if(policy.equals("GREEDY_DEADLINE")) {
            result = getGreedyDeadlineDecision(task);
        }
        else if(policy.equals("EADC")) {
            result = getEADCDecision(task);
        }
        else if(policy.equals("LOCAL_ONLY")) {
            result = SimSettings.MOBILE_DATACENTER_ID;
        }
        else if(policy.equals("EDGE_ONLY")) {
            result = SimSettings.GENERIC_EDGE_DEVICE_ID;
        }
        else {
            SimLogger.printLine("Unknown policy: " + policy);
            System.exit(0);
        }
        
        return result;
    }
    
    private int getRandomDecision(Task task) {
        double random = Math.random();
        if(random < 0.33) {
            return SimSettings.MOBILE_DATACENTER_ID;
        } else if(random < 0.66) {
            return SimSettings.GENERIC_EDGE_DEVICE_ID;
        } else {
            return SimSettings.CLOUD_DATACENTER_ID;
        }
    }
    
    private int getGreedyEnergyDecision(Task task) {
        double taskLength = task.getCloudletLength();
        double dataSize = task.getCloudletFileSize() + task.getCloudletOutputSize();
        
        double localEnergy = calculateLocalEnergy(taskLength);
        double offloadEnergy = calculateOffloadEnergy(dataSize, taskLength);
        
        if(localEnergy <= offloadEnergy) {
            return SimSettings.MOBILE_DATACENTER_ID;
        } else {
            double edgeUtilization = SimManager.getInstance().getEdgeServerManager().getAvgUtilization();
            if(edgeUtilization < 80) {
                return SimSettings.GENERIC_EDGE_DEVICE_ID;
            } else {
                return SimSettings.CLOUD_DATACENTER_ID;
            }
        }
    }
    
    private int getGreedyDeadlineDecision(Task task) {
        double taskLength = task.getCloudletLength();
        int taskType = task.getTaskType();
        double maxDelay = SimSettings.getInstance().getTaskLookUpTable()[taskType][13];
        
        double localTime = taskLength / MOBILE_MIPS;
        double edgeTime = estimateEdgeExecutionTime(task);
        double cloudTime = estimateCloudExecutionTime(task);
        
        if(edgeTime <= maxDelay && edgeTime <= localTime && edgeTime <= cloudTime) {
            return SimSettings.GENERIC_EDGE_DEVICE_ID;
        } else if(localTime <= maxDelay && localTime <= cloudTime) {
            return SimSettings.MOBILE_DATACENTER_ID;
        } else if(cloudTime <= maxDelay) {
            return SimSettings.CLOUD_DATACENTER_ID;
        } else {
            return SimSettings.GENERIC_EDGE_DEVICE_ID;
        }
    }
    
    private int getEADCDecision(Task task) {
        double taskLength = task.getCloudletLength();
        double dataSize = task.getCloudletFileSize() + task.getCloudletOutputSize();
        int taskType = task.getTaskType();
        double maxDelay = SimSettings.getInstance().getTaskLookUpTable()[taskType][13];
        double delaySensitivity = SimSettings.getInstance().getTaskLookUpTable()[taskType][12];
        
        double localTime = taskLength / MOBILE_MIPS;
        double edgeTime = estimateEdgeExecutionTime(task);
        double cloudTime = estimateCloudExecutionTime(task);
        
        double localEnergy = calculateLocalEnergy(taskLength);
        double edgeEnergy = calculateOffloadEnergy(dataSize, taskLength);
        double cloudEnergy = calculateOffloadEnergy(dataSize * 1.5, taskLength);
        
        boolean localMeetsDeadline = localTime <= maxDelay;
        boolean edgeMeetsDeadline = edgeTime <= maxDelay;
        boolean cloudMeetsDeadline = cloudTime <= maxDelay;
        
        double adaptiveAlpha = ALPHA * (1 + delaySensitivity);
        double adaptiveBeta = BETA * (1 - delaySensitivity);
        
        double localScore = localMeetsDeadline ? 
            calculateScore(localTime, localEnergy, maxDelay, adaptiveAlpha, adaptiveBeta) : Double.MAX_VALUE;
        double edgeScore = edgeMeetsDeadline ? 
            calculateScore(edgeTime, edgeEnergy, maxDelay, adaptiveAlpha, adaptiveBeta) : Double.MAX_VALUE;
        double cloudScore = cloudMeetsDeadline ? 
            calculateScore(cloudTime, cloudEnergy, maxDelay, adaptiveAlpha, adaptiveBeta) : Double.MAX_VALUE;
        
        double edgeUtilization = SimManager.getInstance().getEdgeServerManager().getAvgUtilization();
        if(edgeUtilization > 85) {
            edgeScore *= (1 + (edgeUtilization - 85) / 100);
        }
        
        if(localScore <= edgeScore && localScore <= cloudScore && localMeetsDeadline) {
            return SimSettings.MOBILE_DATACENTER_ID;
        } else if(edgeScore <= cloudScore && edgeMeetsDeadline) {
            return SimSettings.GENERIC_EDGE_DEVICE_ID;
        } else if(cloudMeetsDeadline) {
            return SimSettings.CLOUD_DATACENTER_ID;
        } else {
            if(edgeTime <= localTime && edgeTime <= cloudTime) {
                return SimSettings.GENERIC_EDGE_DEVICE_ID;
            } else if(localTime <= cloudTime) {
                return SimSettings.MOBILE_DATACENTER_ID;
            } else {
                return SimSettings.CLOUD_DATACENTER_ID;
            }
        }
    }
    
    private double calculateScore(double time, double energy, double deadline, double alpha, double beta) {
        double normalizedTime = time / deadline;
        double maxEnergy = MOBILE_POWER_ACTIVE * 10;
        double normalizedEnergy = energy / maxEnergy;
        
        return alpha * normalizedTime + beta * normalizedEnergy;
    }
    
    private double calculateLocalEnergy(double taskLength) {
        double executionTime = taskLength / MOBILE_MIPS;
        return MOBILE_POWER_ACTIVE * executionTime;
    }
    
    private double calculateOffloadEnergy(double dataSize, double taskLength) {
        double transmissionTime = (dataSize * 8) / (SimSettings.getInstance().getWlanBandwidth() * 1000);
        double idleTime = taskLength / EDGE_MIPS;
        return MOBILE_POWER_TRANSMIT * transmissionTime + MOBILE_POWER_IDLE * idleTime;
    }
    
    private double estimateEdgeExecutionTime(Task task) {
        double taskLength = task.getCloudletLength();
        double dataSize = task.getCloudletFileSize() + task.getCloudletOutputSize();
        
        double transmissionDelay = (dataSize * 8) / (SimSettings.getInstance().getWlanBandwidth() * 1000);
        double processingTime = taskLength / EDGE_MIPS;
        double edgeUtilization = SimManager.getInstance().getEdgeServerManager().getAvgUtilization();
        double queuingDelay = (edgeUtilization / 100) * processingTime * 0.5;
        
        return transmissionDelay + processingTime + queuingDelay;
    }
    
    private double estimateCloudExecutionTime(Task task) {
        double taskLength = task.getCloudletLength();
        double dataSize = task.getCloudletFileSize() + task.getCloudletOutputSize();
        
        double wanDelay = SimSettings.getInstance().getWanPropagationDelay();
        double transmissionDelay = (dataSize * 8) / (SimSettings.getInstance().getWanBandwidth() * 1000) + wanDelay * 2;
        double processingTime = taskLength / (SimSettings.getInstance().getMipsForCloudVM());
        
        return transmissionDelay + processingTime;
    }

    @Override
    public Vm getVmToOffload(Task task, int deviceId) {
        Vm selectedVM = null;
        
        if(deviceId == SimSettings.CLOUD_DATACENTER_ID) {
            double selectedVmCapacity = 0;
            List<Host> list = SimManager.getInstance().getCloudServerManager().getDatacenter().getHostList();
            for (int hostIndex = 0; hostIndex < list.size(); hostIndex++) {
                List<CloudVM> vmArray = SimManager.getInstance().getCloudServerManager().getVmList(hostIndex);
                for(int vmIndex = 0; vmIndex < vmArray.size(); vmIndex++) {
                    double requiredCapacity = ((CpuUtilizationModel_Custom)task.getUtilizationModelCpu()).predictUtilization(vmArray.get(vmIndex).getVmType());
                    double targetVmCapacity = (double)100 - vmArray.get(vmIndex).getCloudletScheduler().getTotalUtilizationOfCpu(CloudSim.clock());
                    if(requiredCapacity <= targetVmCapacity && targetVmCapacity > selectedVmCapacity) {
                        selectedVM = vmArray.get(vmIndex);
                        selectedVmCapacity = targetVmCapacity;
                    }
                }
            }
        }
        else if(deviceId == SimSettings.GENERIC_EDGE_DEVICE_ID) {
            double selectedVmCapacity = 0;
            for(int hostIndex = 0; hostIndex < numberOfHost; hostIndex++) {
                List<EdgeVM> vmArray = SimManager.getInstance().getEdgeServerManager().getVmList(hostIndex);
                for(int vmIndex = 0; vmIndex < vmArray.size(); vmIndex++) {
                    double requiredCapacity = ((CpuUtilizationModel_Custom)task.getUtilizationModelCpu()).predictUtilization(vmArray.get(vmIndex).getVmType());
                    double targetVmCapacity = (double)100 - vmArray.get(vmIndex).getCloudletScheduler().getTotalUtilizationOfCpu(CloudSim.clock());
                    if(requiredCapacity <= targetVmCapacity && targetVmCapacity > selectedVmCapacity) {
                        selectedVM = vmArray.get(vmIndex);
                        selectedVmCapacity = targetVmCapacity;
                    }
                }
            }
        }
        
        return selectedVM;
    }

    @Override
    public void processEvent(SimEvent arg0) {
    }

    @Override
    public void shutdownEntity() {
    }

    @Override
    public void startEntity() {
    }
}
