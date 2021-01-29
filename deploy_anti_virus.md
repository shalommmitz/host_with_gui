Reference: []https://www.techrepublic.com/article/how-to-install-and-use-clamav-on-ubuntu-server-20-04/

## Target

We want to be able to periodically scan the virtual machine hard disks.
This is attractive, because, when we do the scan, the VM is not working and some of the hiding mechanisms of the malware are not active.

## Procedure Highlights

   - Install and update the threat database of clamav
   - Setup cron job to regularly suspend the VMs (if running), mount their HD and scan
