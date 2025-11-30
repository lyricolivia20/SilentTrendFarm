---
title: "PC Build & Repair - Common Hardware Headaches Solved"
description: "Building a PC is 90% triumph and 10% sheer panic. Here's how to troubleshoot the most common hardware issues."
pubDate: 2024-11-25
heroImage: /images/pc-build.jpg
tags:
  - "hardware"
  - "pc-build"
  - "troubleshooting"
  - "repair"
category: "it-tech"
---

Building a PC is 90% triumph and 10% sheer panic. For that 10% when a new build refuses to post or a component fails, here are the first things I check.

## Problem: CPU Fan Error on Boot

This error message on startup typically means the motherboard isn't detecting a signal from the CPU fan, a safety measure to prevent overheating.

**To fix it:**

1. **Check the connection**: Open the case and ensure the fan's cable is securely plugged into the correct motherboard header, almost always labeled `CPU_FAN`.

2. **Visual confirmation**: Power on the PC with the case open to visually confirm the fan is spinning. If it isn't, the fan itself may be faulty.

3. **BIOS settings**: If the fan is working, check your BIOS settings; some motherboards have fan monitoring that is too sensitive and may need adjustment. Look for "CPU Fan Speed Low Limit" and set it to "Ignore" or a lower RPM threshold.

## Problem: New GPU Needs Power, But PSU Lacks Connectors

You've installed a new graphics card, but it requires a 6-pin or 8-pin PCIe power connector that your power supply unit (PSU) doesn't have. This usually happens with older or lower-wattage PSUs.

**Solutions:**

- **Best long-term solution**: Upgrade your PSU to one with adequate wattage and the correct connectors.

- **Temporary workaround**: You can use a Molex-to-PCIe adapter, but this is **not recommended for long-term use** as it can put a strain on your PSU and may not provide stable power. High-end GPUs should never rely on adapters.

## Problem: External Hard Drive Not Found or Gives Errors

When you plug in an external drive and it doesn't appear or gives frequent errors, it could be anything from a faulty cable to a power issue.

**Troubleshoot in this order:**

1. **Check physical connections**: Try a different USB port and a different cable. USB cables fail more often than you'd think.

2. **Power issues**: If the drive has a separate power adapter, ensure it's plugged in and working. If it's USB-powered, connect it directly to the computer instead of through a hub, which may not provide enough power.

3. **Direct connection**: Always connect directly during troubleshooting to rule out hubs or extension cables as the problem.

4. **Check Disk Management** (Windows): The drive might be connected but not assigned a drive letter. Open Disk Management and look for unallocated or offline disks.

## General Troubleshooting Philosophy

Whether it's a software glitch or a hardware headache, the key to solving most tech problems is a calm and systematic approach. By isolating variables and testing potential solutions one by one, you can turn frustration into accomplishment.

**The golden rule**: Change one thing at a time, test, then move on. Changing multiple variables at once makes it impossible to know what actually fixed the problem.
