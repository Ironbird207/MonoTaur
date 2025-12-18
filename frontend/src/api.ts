const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

export interface Device {
  id: string;
  name: string;
  ip_address: string;
  type: string;
  snmp_profile?: Record<string, unknown> | null;
}

export interface LayoutDevice {
  device_id: string;
  x: number;
  y: number;
}

export interface Layout {
  id: string;
  name: string;
  background: string;
  devices: LayoutDevice[];
}

export interface Link {
  id: string;
  source_device_id: string;
  target_device_id: string;
  source_ifindex?: number | null;
  target_ifindex?: number | null;
  label?: string | null;
}

export interface DeviceCreate {
  name: string;
  ip_address: string;
  type?: string;
  snmp_profile?: Record<string, unknown> | null;
}

export interface LayoutCreate {
  name: string;
  background: string;
  devices: LayoutDevice[];
}

export interface LayoutUpdate {
  name?: string;
  background?: string;
  devices?: LayoutDevice[];
}

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getDevices: () => request<Device[]>('/devices'),
  getLayouts: () => request<Layout[]>('/layouts'),
  getLinks: () => request<Link[]>('/links'),
  createDevice: async (payload: DeviceCreate) => {
    const res = await fetch(`${API_BASE}/devices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    return (await res.json()) as Device;
  },
  createLayout: async (payload: LayoutCreate) => {
    const res = await fetch(`${API_BASE}/layouts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    return (await res.json()) as Layout;
  },
  updateLayout: async (layoutId: string, payload: LayoutUpdate) => {
    const res = await fetch(`${API_BASE}/layouts/${layoutId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    return (await res.json()) as Layout;
  },
};
