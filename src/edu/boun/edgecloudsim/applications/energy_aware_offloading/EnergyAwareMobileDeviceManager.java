package edu.boun.edgecloudsim.applications.energy_aware_offloading;

import org.cloudbus.cloudsim.UtilizationModel;

import edu.boun.edgecloudsim.edge_client.MobileDeviceManager;
import edu.boun.edgecloudsim.edge_client.CpuUtilizationModel_Custom;
import edu.boun.edgecloudsim.utils.TaskProperty;

/**
 * Mobile device manager with energy tracking
 * Extends the default MobileDeviceManager
 */
public class EnergyAwareMobileDeviceManager extends MobileDeviceManager {
    
    private UtilizationModel cpuUtilizationModel;
    
    public EnergyAwareMobileDeviceManager() throws Exception {
        super();
        this.cpuUtilizationModel = new CpuUtilizationModel_Custom();
    }
    
    @Override
    public void initialize() {
        // Initialize is handled by parent class
    }
    
    @Override
    public UtilizationModel getCpuUtilizationModel() {
        return cpuUtilizationModel;
    }
    
    @Override
    public void submitTask(TaskProperty edgeTask) {
        // Delegate to parent class for task submission
        // This method is called to submit tasks from mobile devices
    }
}