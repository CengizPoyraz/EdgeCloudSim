package edu.boun.edgecloudsim.applications.energy_aware_offloading;

import java.util.ArrayList;

import org.apache.commons.math3.distribution.ExponentialDistribution;

import edu.boun.edgecloudsim.core.SimSettings;
import edu.boun.edgecloudsim.task_generator.LoadGeneratorModel;
import edu.boun.edgecloudsim.utils.SimLogger;
import edu.boun.edgecloudsim.utils.TaskProperty;

/**
 * Load generator for energy-aware offloading simulation
 * Generates tasks with different application profiles based on Poisson distribution
 */
public class EnergyAwareLoadGenerator extends LoadGeneratorModel {
    
    public EnergyAwareLoadGenerator(int numberOfMobileDevices, double simulationTime, String simScenario) {
        super(numberOfMobileDevices, simulationTime, simScenario);
    }
    
    @Override
    public void initializeModel() {
        // Initialize the task list
        taskList = new ArrayList<TaskProperty>();
        
        // Get simulation settings
        SimSettings SS = SimSettings.getInstance();
        
        // Generate tasks for each mobile device
        for(int i = 0; i < numberOfMobileDevices; i++) {
            
            // Determine which application type this device will use
            int taskType = getTaskTypeOfDevice(i);
            
            // Get application-specific properties from task lookup table
            double[][] lookupTable = SS.getTaskLookUpTable();
            
            double poissonMean = lookupTable[taskType][8]; // poisson_interarrival
            double activePeriod = lookupTable[taskType][5]; // active_period
            double idlePeriod = lookupTable[taskType][6]; // idle_period
            
            // Create exponential distribution for task inter-arrival times
            ExponentialDistribution rng = new ExponentialDistribution(poissonMean);
            
            double taskStartTime = SS.getWarmUpPeriod(); // Start after warm-up period
            double currentTime = taskStartTime;
            
            // Generate tasks for this device during the simulation period
            while(currentTime < simulationTime) {
                
                // Active period - generate tasks
                double activeEndTime = Math.min(currentTime + activePeriod, simulationTime);
                
                while(currentTime < activeEndTime) {
                    
                    // Create a new task
                    TaskProperty task = new TaskProperty(
                        i,                     // mobile device ID
                        taskType,              // task type
                        currentTime,           // submission time
                        0,                 // pessimistic flag
                        0                      // vm type (will be decided by orchestrator)
                    );
                    
                    // Add task to the list
                    taskList.add(task);
                    
                    // Calculate next task arrival time using exponential distribution
                    double interval = rng.sample();
                    currentTime += interval;
                }
                
                // Idle period - no tasks generated
                currentTime += idlePeriod;
            }
        }
        
        // Sort tasks by submission time
        taskList.sort((task1, task2) -> {
            double time1 = task1.getStartTime();
            double time2 = task2.getStartTime();
            return Double.compare(time1, time2);
        });
        
        // Log task generation statistics
        SimLogger.printLine("Task generation completed:");
        SimLogger.printLine("  Total tasks: " + taskList.size());
        SimLogger.printLine("  Mobile devices: " + numberOfMobileDevices);
        SimLogger.printLine("  Simulation time: " + simulationTime + " seconds");
    }
    
    @Override
    public int getTaskTypeOfDevice(int deviceId) {
        // Distribute devices across application types
        // This ensures a mix of computation-intensive, network-intensive, and balanced tasks
        SimSettings SS = SimSettings.getInstance();
        
        double[][] lookupTable = SS.getTaskLookUpTable();
        int numOfAppTypes = lookupTable.length;
        
        if (numOfAppTypes > 0) {
            return deviceId % numOfAppTypes;
        }
        
        return 0;
    }
}