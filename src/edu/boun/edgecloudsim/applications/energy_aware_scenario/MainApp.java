package edu.boun.edgecloudsim.applications.energy_aware_scenario;

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

public class MainApp {

    public static void main(String[] args) {
        Log.disable();
        
        SimLogger.enablePrintLog();
        
        int iterationNumber = 1;
        String configFile = "";
        String outputFolder = "";
        String edgeDevicesFile = "";
        String applicationsFile = "";
        
        if(args.length == 5) {
            configFile = args[0];
            edgeDevicesFile = args[1];
            applicationsFile = args[2];
            outputFolder = args[3];
            iterationNumber = Integer.parseInt(args[4]);
        }
        else if(args.length == 1) {
            configFile = args[0] + "/config/default_config.properties";
            edgeDevicesFile = args[0] + "/config/edge_devices.xml";
            applicationsFile = args[0] + "/config/applications.xml";
            outputFolder = args[0] + "/output";
            iterationNumber = 1;
        }
        else {
            SimLogger.printLine("Simulation arguments are not valid! Using defaults.");
            configFile = "scripts/energy_aware/config/default_config.properties";
            edgeDevicesFile = "scripts/energy_aware/config/edge_devices.xml";
            applicationsFile = "scripts/energy_aware/config/applications.xml";
            outputFolder = "scripts/energy_aware/output";
        }
        
        SimSettings SS = SimSettings.getInstance();
        if(SS.initialize(configFile, edgeDevicesFile, applicationsFile) == false) {
            SimLogger.printLine("Cannot initialize simulation settings!");
            System.exit(0);
        }
        
        if(SS.getFileLoggingEnabled()) {
            SimLogger.enableFileLog();
            SimUtils.cleanOutputFolder(outputFolder);
        }
        
        DateFormat df = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
        Date SimulationStartDate = Calendar.getInstance().getTime();
        String now = df.format(SimulationStartDate);
        SimLogger.printLine("Simulation started at " + now);
        SimLogger.printLine("----------------------------------------------------------------------");
        
        for(int j = SS.getMinNumOfMobileDev(); j <= SS.getMaxNumOfMobileDev(); j += SS.getMobileDevCounterSize()) {
            for(int k = 0; k < SS.getSimulationScenarios().length; k++) {
                for(int i = 0; i < SS.getOrchestratorPolicies().length; i++) {
                    
                    String simScenario = SS.getSimulationScenarios()[k];
                    String orchestratorPolicy = SS.getOrchestratorPolicies()[i];
                    Date ScenarioStartDate = Calendar.getInstance().getTime();
                    now = df.format(ScenarioStartDate);
                    
                    SimLogger.printLine("Scenario started at " + now);
                    SimLogger.printLine("Scenario: " + simScenario + " - Policy: " + orchestratorPolicy + " - #iteration: " + iterationNumber);
                    SimLogger.printLine("Duration: " + SS.getSimulationTime()/60 + " min (warm-up: " + SS.getWarmUpPeriod()/60 + " min)");
                    SimLogger.printLine("# of mobile devices: " + j);
                    SimLogger.getInstance().simStarted(outputFolder, "SIMRESULT_" + simScenario + "_" + orchestratorPolicy + "_" + j + "DEVICES");
                    
                    try {
                        int num_user = 2;
                        Calendar calendar = Calendar.getInstance();
                        boolean trace_flag = false;
                        
                        CloudSim.init(num_user, calendar, trace_flag, 0.01);
                        
                        ScenarioFactory sampleFactory = new EnergyAwareScenarioFactory(j, SS.getSimulationTime(),
                                orchestratorPolicy, simScenario);
                        
                        SimManager manager = new SimManager(sampleFactory, j, simScenario, orchestratorPolicy);
                        manager.startSimulation();
                    }
                    catch(Exception e) {
                        SimLogger.printLine("The simulation has been terminated due to an unexpected error");
                        e.printStackTrace();
                        System.exit(0);
                    }
                    
                    Date ScenarioEndDate = Calendar.getInstance().getTime();
                    now = df.format(ScenarioEndDate);
                    SimLogger.printLine("Scenario finished at " + now + ". It took " + SimUtils.getTimeDifference(ScenarioStartDate, ScenarioEndDate));
                    SimLogger.printLine("----------------------------------------------------------------------");
                }
            }
        }
        
        Date SimulationEndDate = Calendar.getInstance().getTime();
        now = df.format(SimulationEndDate);
        SimLogger.printLine("Simulation finished at " + now + ". It took " + SimUtils.getTimeDifference(SimulationStartDate, SimulationEndDate));
    }
}
