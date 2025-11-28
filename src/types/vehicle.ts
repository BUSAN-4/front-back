export type VehicleType = 'private' | 'taxi' | 'rental';

export interface Vehicle {
  id: string;
  userId: string;
  licensePlate: string;
  vehicleType: VehicleType;
  model?: string;
  year?: number;
  createdAt: string;
}

export interface TripRecord {
  id: string;
  vehicleId: string;
  startTime: string;
  endTime: string;
  distance: number;
  duration: number;
  safetyScore: number;
  drowsinessCount: number;
  suddenAccelerationCount: number;
  location?: string;
}

export interface SafetyScore {
  overall: number;
  drowsiness: number;
  acceleration: number;
  posture: number;
}

