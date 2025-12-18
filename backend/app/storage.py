from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from . import schemas


class InMemoryStore:
    def __init__(self) -> None:
        self.devices: Dict[UUID, schemas.Device] = {}
        self.layouts: Dict[UUID, schemas.Layout] = {}
        self.links: Dict[UUID, schemas.Link] = {}
        self.checks: Dict[UUID, schemas.Check] = {}

    # Devices
    def list_devices(self) -> List[schemas.Device]:
        return list(self.devices.values())

    def create_device(self, payload: schemas.DeviceCreate) -> schemas.Device:
        device = schemas.Device(**payload.model_dump())
        self.devices[device.id] = device
        return device

    def get_device(self, device_id: UUID) -> schemas.Device:
        return self.devices[device_id]

    def update_device(self, device_id: UUID, payload: schemas.DeviceUpdate) -> schemas.Device:
        device = self.devices[device_id]
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(device, field, value)
        self.devices[device_id] = device
        return device

    def delete_device(self, device_id: UUID) -> None:
        self.devices.pop(device_id, None)

    # Layouts
    def list_layouts(self) -> List[schemas.Layout]:
        return list(self.layouts.values())

    def create_layout(self, payload: schemas.LayoutCreate) -> schemas.Layout:
        layout = schemas.Layout(**payload.model_dump())
        self.layouts[layout.id] = layout
        return layout

    def get_layout(self, layout_id: UUID) -> schemas.Layout:
        return self.layouts[layout_id]

    def update_layout(self, layout_id: UUID, payload: schemas.LayoutUpdate) -> schemas.Layout:
        layout = self.layouts[layout_id]
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(layout, field, value)
        self.layouts[layout_id] = layout
        return layout

    def delete_layout(self, layout_id: UUID) -> None:
        self.layouts.pop(layout_id, None)

    # Links
    def list_links(self) -> List[schemas.Link]:
        return list(self.links.values())

    def create_link(self, payload: schemas.LinkCreate) -> schemas.Link:
        link = schemas.Link(**payload.model_dump())
        self.links[link.id] = link
        return link

    def get_link(self, link_id: UUID) -> schemas.Link:
        return self.links[link_id]

    def update_link(self, link_id: UUID, payload: schemas.LinkUpdate) -> schemas.Link:
        link = self.links[link_id]
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(link, field, value)
        self.links[link_id] = link
        return link

    def delete_link(self, link_id: UUID) -> None:
        self.links.pop(link_id, None)

    # Checks
    def list_checks(self) -> List[schemas.Check]:
        return list(self.checks.values())

    def create_check(self, payload: schemas.CheckCreate) -> schemas.Check:
        check = schemas.Check(**payload.model_dump())
        self.checks[check.id] = check
        return check

    def get_check(self, check_id: UUID) -> schemas.Check:
        return self.checks[check_id]

    def update_check(self, check_id: UUID, payload: schemas.CheckUpdate) -> schemas.Check:
        check = self.checks[check_id]
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(check, field, value)
        self.checks[check_id] = check
        return check

    def delete_check(self, check_id: UUID) -> None:
        self.checks.pop(check_id, None)

    def record_check_result(self, check_id: UUID, result: schemas.CheckResult) -> schemas.Check:
        check = self.checks[check_id]
        check.last_result = result
        self.checks[check_id] = check
        return check
