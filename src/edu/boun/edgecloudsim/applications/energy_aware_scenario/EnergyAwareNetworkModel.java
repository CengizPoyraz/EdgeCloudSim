package edu.boun.edgecloudsim.applications.energy_aware_scenario;

import org.cloudbus.cloudsim.core.CloudSim;

import edu.boun.edgecloudsim.core.SimManager;
import edu.boun.edgecloudsim.core.SimSettings;
import edu.boun.edgecloudsim.edge_client.Task;
import edu.boun.edgecloudsim.network.NetworkModel;
import edu.boun.edgecloudsim.utils.Location;
import edu.boun.edgecloudsim.utils.SimLogger;

public class EnergyAwareNetworkModel extends NetworkModel {
    
    private double wlanPoissonMean;
    private double wanPoissonMean;
    private double gsmPoissonMean;
    
    private double avgTaskInputSize;
    private double avgTaskOutputSize;
    
    public EnergyAwareNetworkModel(int _numberOfMobileDevices, String _simScenario) {
        super(_numberOfMobileDevices, _simScenario);
    }

    @Override
    public void initialize() {
        wlanPoissonMean = 0.5 / ((double)numberOfMobileDevices / 20.0);
        wanPoissonMean = 0.5 / ((double)numberOfMobileDevices / 20.0);
        gsmPoissonMean = 0.5 / ((double)numberOfMobileDevices / 20.0);
        
        avgTaskInputSize = 0;
        avgTaskOutputSize = 0;
        
        double[][] taskLookUp = SimSettings.getInstance().getTaskLookUpTable();
        for(int i = 0; i < taskLookUp.length; i++) {
            avgTaskInputSize += taskLookUp[i][5];
            avgTaskOutputSize += taskLookUp[i][6];
        }
        avgTaskInputSize = avgTaskInputSize / taskLookUp.length;
        avgTaskOutputSize = avgTaskOutputSize / taskLookUp.length;
    }

    @Override
    public double getUploadDelay(int sourceDeviceId, int destDeviceId, Task task) {
        double delay = 0;
        
        if(destDeviceId == SimSettings.CLOUD_DATACENTER_ID) {
            delay = getWanUploadDelay(sourceDeviceId, task);
        }
        else if(destDeviceId == SimSettings.GENERIC_EDGE_DEVICE_ID) {
            delay = getWlanUploadDelay(sourceDeviceId, task);
        }
        else if(destDeviceId == SimSettings.MOBILE_DATACENTER_ID) {
            delay = 0;
        }
        
        return delay;
    }

    @Override
    public double getDownloadDelay(int sourceDeviceId, int destDeviceId, Task task) {
        double delay = 0;
        
        if(sourceDeviceId == SimSettings.CLOUD_DATACENTER_ID) {
            delay = getWanDownloadDelay(destDeviceId, task);
        }
        else if(sourceDeviceId == SimSettings.GENERIC_EDGE_DEVICE_ID) {
            delay = getWlanDownloadDelay(destDeviceId, task);
        }
        else if(sourceDeviceId == SimSettings.MOBILE_DATACENTER_ID) {
            delay = 0;
        }
        
        return delay;
    }

    private double getWlanUploadDelay(int deviceId, Task task) {
        double dataSize = task.getCloudletFileSize();
        double wlanBw = SimSettings.getInstance().getWlanBandwidth();
        double delay = (dataSize * 8) / wlanBw;
        
        delay += exponentialRandom(wlanPoissonMean);
        
        return delay;
    }

    private double getWlanDownloadDelay(int deviceId, Task task) {
        double dataSize = task.getCloudletOutputSize();
        double wlanBw = SimSettings.getInstance().getWlanBandwidth();
        double delay = (dataSize * 8) / wlanBw;
        
        delay += exponentialRandom(wlanPoissonMean);
        
        return delay;
    }

    private double getWanUploadDelay(int deviceId, Task task) {
        double dataSize = task.getCloudletFileSize();
        double wanBw = SimSettings.getInstance().getWanBandwidth();
        
        if(wanBw == 0) {
            return Double.MAX_VALUE;
        }
        
        double delay = (dataSize * 8) / wanBw;
        delay += SimSettings.getInstance().getWanPropagationDelay();
        delay += exponentialRandom(wanPoissonMean);
        
        return delay;
    }

    private double getWanDownloadDelay(int deviceId, Task task) {
        double dataSize = task.getCloudletOutputSize();
        double wanBw = SimSettings.getInstance().getWanBandwidth();
        
        if(wanBw == 0) {
            return Double.MAX_VALUE;
        }
        
        double delay = (dataSize * 8) / wanBw;
        delay += SimSettings.getInstance().getWanPropagationDelay();
        delay += exponentialRandom(wanPoissonMean);
        
        return delay;
    }

    private double exponentialRandom(double mean) {
        return -mean * Math.log(1 - Math.random());
    }

    @Override
    public void uploadStarted(Location accessPointLocation, int destDeviceId) {
    }

    @Override
    public void uploadFinished(Location accessPointLocation, int destDeviceId) {
    }

    @Override
    public void downloadStarted(Location accessPointLocation, int sourceDeviceId) {
    }

    @Override
    public void downloadFinished(Location accessPointLocation, int sourceDeviceId) {
    }
}
