#!/usr/bin/python
# Copyright: Lee Garrett
# GNU Affero General Public License v3.0+ (see https://www.gnu.org/licenses/agpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = r"""
---
module: fwupdmgr
short_description: Update firmware via fwupdmgr
description:
  - Optionally refreshes the fwupd metadata, then installs all pending
    firmware updates reported by C(fwupdmgr get-updates).
  - Never reboots. Updates staged for the next boot (e.g. UEFI capsules) are
    applied once the caller reboots the host.
author: Lee Garrett
options:
  refresh:
    description:
      - Run C(fwupdmgr refresh) before looking for updates.
      - Skipped in check mode.
    type: bool
    default: true
  force_refresh:
    description:
      - Pass C(--force) to C(fwupdmgr refresh), downloading metadata even if
        it is considered recent.
    type: bool
    default: false
  update:
    description:
      - Install pending updates. If V(false), only report them.
    type: bool
    default: true
  devices:
    description:
      - Device IDs or GUIDs to update. Empty means all devices.
    type: list
    elements: str
    default: []
  filter:
    description:
      - Device flag filter passed as C(--filter), e.g. V(internal,~needs-reboot).
    type: str
  security_fix:
    description:
      - Allow fwupdmgr to fix host security attributes after updating.
    type: bool
    default: false
  check_reboot:
    description:
      - Run C(fwupdmgr check-reboot-needed) at the end and return
        RV(reboot_required).
    type: bool
    default: true
attributes:
  check_mode:
    support: full
    details: Reports pending updates against the cached metadata.
requirements:
  - fwupd
"""

EXAMPLES = r"""
- name: Update all firmware
  become: true
  leegarrett.system.fwupdmgr:

- name: Report pending updates without refreshing or installing
  become: true
  leegarrett.system.fwupdmgr:
    refresh: false
    update: false
  register: _fwupd

- name: Update internal devices only
  become: true
  leegarrett.system.fwupdmgr:
    filter: internal
"""

RETURN = r"""
refreshed:
  description: Whether new metadata was downloaded.
  returned: always
  type: bool
updates:
  description: Devices with a pending update, before updating.
  returned: always
  type: list
  elements: dict
  contains:
    device_id:
      description: fwupd device ID.
      type: str
    name:
      description: Device name.
      type: str
    version:
      description: Installed firmware version.
      type: str
    update_version:
      description: Version that is (or would be) installed.
      type: str
updated:
  description:
    - Devices that were updated, in the same format as RV(updates).
    - In check mode, the devices that would be updated.
    - On failure, the devices updated before the failing one.
  returned: always
  type: list
  elements: dict
no_updates:
  description: Updatable devices without a pending update.
  returned: always
  type: list
  elements: dict
  contains:
    device_id:
      description: fwupd device ID.
      type: str
    name:
      description: Device name.
      type: str
    version:
      description: Installed firmware version.
      type: str
reboot_required:
  description: Whether any device needs a reboot or shutdown to finish an update.
  returned: when O(check_reboot=true)
  type: bool
"""

import json

from ansible.module_utils.basic import AnsibleModule

# fwupdmgr rc 2: successful, but nothing to do
RC_OK = (0, 2)
COMMON_FLAGS = ["--no-remote-check", "--no-unreported-check"]


def run(module, argv, **result):
    rc, out, err = module.run_command(argv)
    if rc not in RC_OK:
        module.fail_json(msg="%s failed" % " ".join(argv), rc=rc, stdout=out, stderr=err, **result)
    return rc, out


def get_json_devices(module, argv):
    rc, out = run(module, argv)
    if rc == 2 or not out.strip():
        return []
    try:
        devices = json.loads(out).get("Devices", [])
    except ValueError as e:
        module.fail_json(msg="cannot parse %s output: %s" % (" ".join(argv), e), stdout=out)

    wanted = module.params["devices"]
    if not wanted:
        return devices
    return [d for d in devices if any(i in wanted for i in [d.get("DeviceId")] + (d.get("Guid") or []))]


def device_entry(dev):
    return {"device_id": dev.get("DeviceId"), "name": dev.get("Name"), "version": dev.get("Version")}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            refresh=dict(type="bool", default=True),
            force_refresh=dict(type="bool", default=False),
            update=dict(type="bool", default=True),
            devices=dict(type="list", elements="str", default=[]),
            filter=dict(type="str"),
            security_fix=dict(type="bool", default=False),
            check_reboot=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
    )
    p = module.params
    binary = module.get_bin_path("fwupdmgr", required=True)
    filter_args = ["--filter", p["filter"]] if p["filter"] else []
    query_args = ["--json", "--no-metadata-check"] + COMMON_FLAGS + filter_args

    refreshed = False
    if p["refresh"] and not module.check_mode:
        argv = [binary, "refresh"] + COMMON_FLAGS
        if p["force_refresh"]:
            argv.append("--force")
        rc, _ = run(module, argv)
        refreshed = rc == 0

    updates = [
        dict(device_entry(d), update_version=d["Releases"][0].get("Version"))
        for d in get_json_devices(module, [binary, "get-updates"] + query_args)
        if d.get("Releases")
    ]
    pending = set(u["device_id"] for u in updates)
    no_updates = [
        device_entry(d)
        for d in get_json_devices(module, [binary, "get-devices"] + query_args)
        if "updatable" in (d.get("Flags") or []) and d.get("DeviceId") not in pending
    ]
    result = dict(refreshed=refreshed, updates=updates, no_updates=no_updates, updated=[])

    if p["update"] and updates:
        if module.check_mode:
            result["updated"] = updates
        else:
            argv = [binary, "update", "--assume-yes", "--no-reboot-check"] + COMMON_FLAGS + filter_args
            if not p["security_fix"]:
                argv.append("--no-security-fix")
            if p["devices"]:
                for u in updates:
                    run(module, argv + [u["device_id"]], **result)
                    result["updated"].append(u)
            else:
                run(module, argv, **result)
                result["updated"] = updates

    if p["check_reboot"]:
        rc, _ = run(module, [binary, "check-reboot-needed", "--json"], **result)
        result["reboot_required"] = rc == 0

    module.exit_json(changed=refreshed or bool(result["updated"]), **result)


if __name__ == "__main__":
    main()
