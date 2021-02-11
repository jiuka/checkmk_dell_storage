# Checkmk extension for Dell Storage REST API

![build](https://github.com/jiuka/checkmk_dell_storage/workflows/build/badge.svg)
![flake8](https://github.com/jiuka/checkmk_dell_storage/workflows/Lint/badge.svg)
![pytest](https://github.com/jiuka/checkmk_dell_storage/workflows/pytest/badge.svg)

## Description

Check Dell Storage Managed by the Dell Storage Manager with the Storage REST API. This Special Agent uses `piggyback` to return informations for different parts of the system.

### Piggyback structure

 * A node per StorageCenter
   * List of StorageCenter Alerts
   * State of the Storage Center
   * State of the Controllers
   * State of the Enclosures
   * State of the Volumes (w/ metrics for latency, throughput, iops and usage)
 * A node per Controllers
   * State of the Controller
   * State of the Controller Ports (w/ metrics for latency, throughput ans iops)
   * State of the Controller Fans
   * State of the Controller PSUs
   * State of the Controller Temperatures
 * A node per Enclosures
   * State of the Enclosure
   * State of the Enclosure Fans
   * State of the Enclosure Disks (w/ metrics for latency, throughput, iops and usage)
   * State of the Controller PSUs
   * State of the Enclosure Temperatures

## Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

## Directories

The following directories in this repo are getting mapped into the Checkmk site.

* `agents`, `checkman`, `checks`, `doc`, `inventory`, `notifications`, `pnp-templates`, `web` are mapped into `local/share/check_mk/`
* `agent_based` is mapped to `local/lib/check_mk/base/plugins/agent_based`
* `nagios_plugins` is mapped to `local/lib/nagios/plugins`

## Continuous integration
### Local

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.

### Github Workflow

The provided Github Workflows run `pytest` and `flake8` in the same checkmk docker conatiner as vscode.