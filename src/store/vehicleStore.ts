import { create } from 'zustand';
import type { Vehicle, TripRecord } from '../types/vehicle';

interface VehicleState {
  vehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  tripRecords: TripRecord[];
  isLoading: boolean;
  fetchVehicles: () => Promise<void>;
  registerVehicle: (data: Omit<Vehicle, 'id' | 'userId' | 'createdAt'>) => Promise<void>;
  updateVehicle: (id: string, data: Partial<Vehicle>) => Promise<void>;
  deleteVehicle: (id: string) => Promise<void>;
  selectVehicle: (vehicle: Vehicle | null) => void;
  fetchTripRecords: (vehicleId: string) => Promise<void>;
}

const mockVehicles: Vehicle[] = [
  {
    id: '1',
    userId: '1',
    licensePlate: '12가3456',
    vehicleType: 'private',
    model: '소나타',
    year: 2020,
    createdAt: new Date().toISOString(),
  },
];

const mockTripRecords: Record<string, TripRecord[]> = {
  '1': [
    {
      id: '1',
      vehicleId: '1',
      startTime: new Date(Date.now() - 86400000).toISOString(),
      endTime: new Date(Date.now() - 86400000 + 3600000).toISOString(),
      distance: 45.5,
      duration: 3600,
      safetyScore: 85.5,
      drowsinessCount: 2,
      suddenAccelerationCount: 1,
      location: '부산시 해운대구',
    },
    {
      id: '2',
      vehicleId: '1',
      startTime: new Date(Date.now() - 172800000).toISOString(),
      endTime: new Date(Date.now() - 172800000 + 7200000).toISOString(),
      distance: 120.3,
      duration: 7200,
      safetyScore: 92.0,
      drowsinessCount: 0,
      suddenAccelerationCount: 0,
      location: '부산시 남구',
    },
  ],
};

export const useVehicleStore = create<VehicleState>((set) => ({
  vehicles: [],
  selectedVehicle: null,
  tripRecords: [],
  isLoading: false,

  fetchVehicles: async () => {
    set({ isLoading: true });
    await new Promise((resolve) => setTimeout(resolve, 500));
    set({ vehicles: mockVehicles, isLoading: false });
  },

  registerVehicle: async (data) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const newVehicle: Vehicle = {
      ...data,
      id: Date.now().toString(),
      userId: '1',
      createdAt: new Date().toISOString(),
    };
    set((state) => ({ vehicles: [...state.vehicles, newVehicle] }));
  },

  updateVehicle: async (id, data) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    set((state) => {
      const updated = state.vehicles.find((v) => v.id === id);
      if (!updated) return state;
      const newVehicle = { ...updated, ...data };
      return {
        vehicles: state.vehicles.map((v) => (v.id === id ? newVehicle : v)),
        selectedVehicle: state.selectedVehicle?.id === id ? newVehicle : state.selectedVehicle,
      };
    });
  },

  deleteVehicle: async (id) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    set((state) => ({
      vehicles: state.vehicles.filter((v) => v.id !== id),
      selectedVehicle: state.selectedVehicle?.id === id ? null : state.selectedVehicle,
    }));
  },

  selectVehicle: (vehicle) => {
    set({ selectedVehicle: vehicle });
  },

  fetchTripRecords: async (vehicleId) => {
    set({ isLoading: true });
    await new Promise((resolve) => setTimeout(resolve, 500));
    const records = mockTripRecords[vehicleId] || [];
    set({ tripRecords: records, isLoading: false });
  },
}));

