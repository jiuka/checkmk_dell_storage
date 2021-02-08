# Checkmk extension for Dell Storage REST API

![build](https://github.com/jiuka/checkmk_dell_storage/workflows/build/badge.svg)
![flake8](https://github.com/jiuka/checkmk_dell_storage/workflows/Lint/badge.svg?branch=master)

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