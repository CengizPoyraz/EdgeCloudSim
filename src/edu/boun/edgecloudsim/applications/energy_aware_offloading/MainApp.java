package edu.boun.edgecloudsim.applications.energy_aware_offloading;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import org.cloudbus.cloudsim.Log;
import org.cloudbus.cloudsim.core.CloudSim;

import edu.boun.edgecloudsim.core.ScenarioFactory;
import edu.boun.edgecloudsim.core.SimManager;
import edu.boun.edgecloudsim.core.SimSettings;
import edu.boun.edgecloudsim.utils.SimLogger;
import edu.boun.edgecloudsim.utils.SimUtils;

/**
 * Energy-Aware Task Offloading with Deadline Constraints
 * Main simulation entry point
 */
public class MainApp {
    
    public static void main(String[] args) {
        
        // Disable CloudSim logs
        Log.disable();
        
        // Enable EdgeCloudSim logs
        SimLogger.enablePrintLog();
        
        int iterationNumber = 1;
        String configFile = "";
        String outputFolder = "";
        String edgeDevicesFile = "";
        String applicationsFile = "";
        
        // Parse command line arguments
        if (args.length == 5) {
            configFile = args[0];
            edgeDevicesFile = args[1];
            applicationsFile = args[2];
            outputFolder = args[3];
            iterationNumber = Integer.parseInt(args[4]);
        } else {
            SimLogger.printLine("Simulation setting file, output folder and iteration number are not provided! Using default ones...");
            
            // Default paths - relative to EdgeCloudSim root directory
            configFile = "scripts/energy_aware_offloading/config/config.properties";
            edgeDevicesFile = "scripts/energy_aware_offloading/config/edge_devices.xml";
            applicationsFile = "scripts/energy_aware_offloading/config/applications.xml";
            outputFolder = "sim_results/ite" + iterationNumber;
        }
        
        // Initialize simulation settings FIRST
        SimSettings SS = SimSettings.getInstance();
        if (SS.initialize(configFile, edgeDevicesFile, applicationsFile) == false) {
            SimLogger.printLine("Cannot initialize simulation settings!");
            SimLogger.printLine("Please check:");
            SimLogger.printLine("  1. Config file exists: " + configFile);
            SimLogger.printLine("  2. Edge devices file exists: " + edgeDevicesFile);
            SimLogger.printLine("  3. Applications file exists: " + applicationsFile);
            System.exit(1);
        }
        
        // Enable file logging if configured
        if (SS.getFileLoggingEnabled()) {
            SimLogger.enableFileLog();
            SimUtils.cleanOutputFolder(outputFolder);
        }
        
        DateFormat df = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
        Date SimulationStartDate = Calendar.getInstance().getTime();
        String now = df.format(SimulationStartDate);
        
        SimLogger.printLine("========================================");
        SimLogger.printLine("ENERGY-AWARE TASK OFFLOADING SIMULATION");
        SimLogger.printLine("========================================");
        SimLogger.printLine("Simulation started at " + now);
        SimLogger.printLine("Iteration number: " + iterationNumber);
        SimLogger.printLine("Config file: " + configFile);
        SimLogger.printLine("Orchestrator policies:");
        
        String[] orchestratorPolicies = SS.getOrchestratorPolicies();
        for (String policy : orchestratorPolicies) {
            SimLogger.printLine("  - " + policy);
        }
        
        SimLogger.printLine("Warm-up period: " + SS.getWarmUpPeriod() + " seconds");
        SimLogger.printLine("Simulation time: " + SS.getSimulationTime() + " seconds");
        SimLogger.printLine("========================================\n");
        
        // Run simulations for each orchestrator policy
        for (int j = 0; j < orchestratorPolicies.length; j++) {
            
            String orchestratorPolicy = orchestratorPolicies[j];
            
            Date ScenarioStartDate = Calendar.getInstance().getTime();
            now = df.format(ScenarioStartDate);
            
            SimLogger.printLine("----------------------------------------------------------------------");
            SimLogger.printLine("Scenario started at " + now);
            SimLogger.printLine("Scenario: " + orchestratorPolicy + " - Iteration: " + iterationNumber);
            SimLogger.printLine("----------------------------------------------------------------------");
            
            // Run simulation for different number of mobile devices
            for (int k = SS.getMinNumOfMobileDev(); k <= SS.getMaxNumOfMobileDev(); k += SS.getMobileDevCounterSize()) {
                
                try {
                    // Initialize CloudSim
                    int num_user = 2;
                    Calendar calendar = Calendar.getInstance();
                    boolean trace_flag = false;
                    
                    CloudSim.init(num_user, calendar, trace_flag, 0.01);
                    
                    // Create scenario factory
                    String simScenario = orchestratorPolicy + "_" + k + "DEVICES";
                    ScenarioFactory scenarioFactory = new EnergyAwareScenarioFactory(
                        j,
                        SS.getSimulationTime(),
                        orchestratorPolicy,
                        simScenario
                    );
                    
                    // Set number of mobile devices
                    scenarioFactory.setNumOfMobileDevice(k);
                    
                    // Create simulation manager
                    SimManager manager = new SimManager(
                        scenarioFactory,
                        k,  // number of mobile devices
                        simScenario,
                        orchestratorPolicy
                    );
                    
                    // Initialize SimLogger for this scenario
                    String outputPath = outputFolder;// + "/" + simScenario;
                    SimLogger.getInstance().simStarted(outputPath, simScenario);
                    
                    SimLogger.printLine("Starting simulation with " + k + " mobile devices...");
                    
                    // Start simulation
                    manager.startSimulation();
                    
                    // Stop logging
                    SimLogger.getInstance().simStopped();
                    
                    SimLogger.printLine("Simulation with " + k + " devices completed successfully.");
                    
                } catch (Exception e) {
                    SimLogger.printLine("The simulation has been terminated due to an unexpected error");
                    SimLogger.printLine("Error: " + e.getMessage());
                    e.printStackTrace();
                    System.exit(1);
                }
            }
            
            Date ScenarioEndDate = Calendar.getInstance().getTime();
            now = df.format(ScenarioEndDate);
            SimLogger.printLine("Scenario finished at " + now + ". It took " + 
                SimUtils.getTimeDifference(ScenarioStartDate, ScenarioEndDate));
            SimLogger.printLine("----------------------------------------------------------------------\n");
        }
        
        Date SimulationEndDate = Calendar.getInstance().getTime();
        now = df.format(SimulationEndDate);
        
        SimLogger.printLine("========================================");
        SimLogger.printLine("ALL SIMULATIONS COMPLETED SUCCESSFULLY!");
        SimLogger.printLine("========================================");
        SimLogger.printLine("Simulation finished at " + now);
        SimLogger.printLine("Total time: " + SimUtils.getTimeDifference(SimulationStartDate, SimulationEndDate));
        SimLogger.printLine("\nResults saved to: " + outputFolder);
    }
}