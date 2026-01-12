
export type Language = 'en' | 'ar' | 'ur' | 'hi' | 'ne';

export interface Location {
  latitude: number;
  longitude: number;
  timestamp: number;
  address?: string;
}

export interface Checkpoint {
  timestamp: number;
  location: Location;
  passengers: number;
}

export interface Trip {
  id: string;
  driverId: string;
  driverName: string;
  vehicleNumber: string;
  startPassengers: number;
  endPassengers?: number;
  startTime: number;
  endTime?: number;
  startLocation: Location;
  endLocation?: Location;
  checkpoints: Checkpoint[];
  status: 'active' | 'completed';
  distanceKm: number;
}

export interface Driver {
  id: string;
  name: string;
  points: number;
  totalTrips: number;
  status?: 'active' | 'suspended';
}

export interface Vehicle {
  number: string;
  type: string;
  capacity: number;
}

export interface AdminLog {
  id: string;
  action: 'ADD' | 'UPDATE' | 'DELETE' | 'COMPLETE' | 'POINTS_ADJUST';
  entityType: 'DRIVER' | 'VEHICLE' | 'TRIP';
  entityId: string;
  details: string;
  timestamp: number;
}

export interface AppState {
  drivers: Driver[];
  vehicles: Vehicle[];
  trips: Trip[];
  logs: AdminLog[];
}
