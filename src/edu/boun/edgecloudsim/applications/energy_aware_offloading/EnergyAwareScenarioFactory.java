package edu.boun.edgecloudsim.applications.energy_aware_offloading;

import edu.boun.edgecloudsim.core.ScenarioFactory;
import edu.boun.edgecloudsim.edge_client.MobileDeviceManager;
import edu.boun.edgecloudsim.edge_client.mobile_processing_unit.MobileServerManager;
import edu.boun.edgecloudsim.edge_client.mobile_processing_unit.DefaultMobileServerManager;
import edu.boun.edgecloudsim.edge_orchestrator.EdgeOrchestrator;
import edu.boun.edgecloudsim.edge_server.EdgeServerManager;
import edu.boun.edgecloudsim.edge_server.DefaultEdgeServerManager;
import edu.boun.edgecloudsim.cloud_server.CloudServerManager;
import edu.boun.edgecloudsim.cloud_server.DefaultCloudServerManager;
import edu.boun.edgecloudsim.network.NetworkModel;
import edu.boun.edgecloudsim.network.MM1Queue;
import edu.boun.edgecloudsim.task_generator.LoadGeneratorModel;
import edu.boun.edgecloudsim.task_generator.IdleActiveLoadGenerator;
import edu.boun.edgecloudsim.mobility.MobilityModel;
import edu.boun.edgecloudsim.mobility.NomadicMobility;

/**
 * Factory class for energy-aware offloading simulation
 * Creates all necessary components for the simulation
 */
public class EnergyAwareScenarioFactory implements ScenarioFactory {
    
    private int numOfMobileDevice;
    private double simulationTime;
    private String orchestratorPolicy;
    private String simScenario;
    
    /**
     * Constructor
     * @param policyIndex - Index of the orchestrator policy
     * @param simulationTime - Duration of simulation
     * @param orchestratorPolicy - Name of orchestrator policy
     * @param simScenario - Scenario identifier
     */
    public EnergyAwareScenarioFactory(int policyIndex, double simulationTime, 
                                      String orchestratorPolicy, String simScenario) {
        this.simulationTime = simulationTime;
        this.orchestratorPolicy = orchestratorPolicy;
        this.simScenario = simScenario;
        this.numOfMobileDevice = 0; // Will be set later
    }
    
    @Override
    public LoadGeneratorModel getLoadGeneratorModel() {
        // Use the default IdleActiveLoadGenerator which generates tasks
        // based on applications.xml with Poisson distribution
        return new IdleActiveLoadGenerator(numOfMobileDevice, simulationTime, simScenario);
    }
    
    @Override
    public EdgeOrchestrator getEdgeOrchestrator() {
        return new EnergyAwareOrchestrator(orchestratorPolicy, simScenario);
    }
    
    @Override
    public MobilityModel getMobilityModel() {
        return new NomadicMobility(numOfMobileDevice, simulationTime);
    }
    
    @Override
    public NetworkModel getNetworkModel() {
        return new MM1Queue(numOfMobileDevice, simScenario);
    }
    
    @Override
    public EdgeServerManager getEdgeServerManager() {
        return new DefaultEdgeServerManager();
    }
    
    @Override
    public CloudServerManager getCloudServerManager() {
        // Return default cloud server manager (even though we're not using cloud)
        return new DefaultCloudServerManager();
    }
    
    @Override
    public MobileServerManager getMobileServerManager() {
        // Return default mobile server manager
        // Use DefaultMobileServerManager instead of abstract MobileServerManager
        return new DefaultMobileServerManager();
    }
    
    @Override
    public MobileDeviceManager getMobileDeviceManager() throws Exception {
        return new EnergyAwareMobileDeviceManager();
    }
    
    // Getter and setter methods (not @Override since they might not be in interface)
    public int getNumOfMobileDevice() {
        return numOfMobileDevice;
    }
    
    public void setNumOfMobileDevice(int numOfMobileDevice) {
        this.numOfMobileDevice = numOfMobileDevice;
    }
    
    public double getSimulationTime() {
        return simulationTime;
    }
    
    public void setSimulationTime(double simulationTime) {
        this.simulationTime = simulationTime;
    }
    
    public String getSimulationScenario() {
        return simScenario;
    }
}