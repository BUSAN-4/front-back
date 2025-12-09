import { useVehicleStore } from '../store/vehicleStore';

export const useVehicle = () => {
  const {
    vehicles,
    selectedVehicle,
    tripRecords,
    isLoading,
    fetchVehicles,
    registerVehicle,
    updateVehicle,
    deleteVehicle,
    selectVehicle,
    fetchTripRecords,
  } = useVehicleStore();

  return {
    vehicles,
    selectedVehicle,
    tripRecords,
    isLoading,
    fetchVehicles,
    registerVehicle,
    updateVehicle,
    deleteVehicle,
    selectVehicle,
    fetchTripRecords,
  };
};




