from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, IPvAnyAddress


class DeviceBase(BaseModel):
    name: str
    ip_address: IPvAnyAddress
    type: str = Field(default="unknown", description="device category")
    snmp_profile: Optional[dict] = Field(default=None, description="SNMP credentials and version info")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[IPvAnyAddress] = None
    type: Optional[str] = None
    snmp_profile: Optional[dict] = None


class Device(DeviceBase):
    id: UUID = Field(default_factory=uuid4)


class LayoutDevice(BaseModel):
    device_id: UUID
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class LayoutBase(BaseModel):
    name: str
    background: str = Field(default="osm", description="uploaded image path or 'osm'")
    devices: List[LayoutDevice] = Field(default_factory=list)


class LayoutCreate(LayoutBase):
    pass


class LayoutUpdate(BaseModel):
    name: Optional[str] = None
    background: Optional[str] = None
    devices: Optional[List[LayoutDevice]] = None


class Layout(LayoutBase):
    id: UUID = Field(default_factory=uuid4)


class LinkBase(BaseModel):
    source_device_id: UUID
    target_device_id: UUID
    source_ifindex: Optional[int] = Field(default=None, ge=0)
    target_ifindex: Optional[int] = Field(default=None, ge=0)
    label: Optional[str] = None


class LinkCreate(LinkBase):
    pass


class LinkUpdate(BaseModel):
    source_ifindex: Optional[int] = Field(default=None, ge=0)
    target_ifindex: Optional[int] = Field(default=None, ge=0)
    label: Optional[str] = None


class Link(LinkBase):
    id: UUID = Field(default_factory=uuid4)


class CheckResult(BaseModel):
    status: str = Field(description="ok, warn, crit, or down")
    latency_ms: Optional[float] = Field(default=None, description="round trip time in milliseconds")
    message: Optional[str] = None
    checked_at: datetime


class CheckBase(BaseModel):
    device_id: UUID
    target: str = Field(description="host or IP to poll")
    type: str = Field(default="icmp", description="icmp or other check type")
    interval_s: int = Field(default=60, ge=1, description="polling cadence in seconds")
    timeout_ms: int = Field(default=1000, ge=100, le=10000, description="timeout for the check")
    params: Optional[dict] = Field(default=None, description="extra parameters for the check type")


class CheckCreate(CheckBase):
    pass


class CheckUpdate(BaseModel):
    target: Optional[str] = None
    type: Optional[str] = None
    interval_s: Optional[int] = Field(default=None, ge=1)
    timeout_ms: Optional[int] = Field(default=None, ge=100, le=10000)
    params: Optional[dict] = None


class Check(CheckBase):
    id: UUID = Field(default_factory=uuid4)
    last_result: Optional[CheckResult] = Field(default=None, description="latest poll outcome")
