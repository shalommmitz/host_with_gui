
This repository contains my procedure to create a reasonably safe VMware host.

You might find it useful for other scenarios, if you need the following traits:
  
   - A bare-bone installation
   - but with all the creature-comfort of a graphical desktop, sound, graphical network connection management, etc (not lots of etc)
   - Smaller attack surface

## Procedure

1. Hardware tip:   
   For a laptop secure storage, I like the 1T SSD 970pro, made by a well known Korean company.  
   This drive supports the OPAL2 encryption standard. Just make sure you actually turn the FDE (Full Disk Encryption) On.

2. Install Ubuntu 20.04 server:  
   I like to configure my own partitions, but this is just me.
   Also, I like the main partition (/home) to be xfs. YMMV.

3. Install Xubuntu core:  
   This will add Graphical desktop and related utilities, W/O any applications.  
   After the server is up, run:
   ```
   sudo apt update
   sudo apt install xubuntu-core^          # Notice the ^ at the end of the line  
   ```
   I do all my stuff on virtual machines.  
   So, Xubuntu core helps me NOT to do things on the host (which protects the host).  
   Twisted ? Yes. Defiantly.
   Most important: no browser :-)

4. Disable IPv6  
   At /etc/default/grub, replace the line:  
       `GRUB_CMDLINE_LINUX_DEFAULT=""`  
   with:  
       `GRUB_CMDLINE_LINUX_DEFAULT="ipv6.disable=1"`  
   and then run `update-grub`

5. Install Iptables  
   `sudo apt remove --purge ufw`  
   `sudo apt install iptables-persistent`  
   See appendix A for the rules file

6. Optional: disable CUPS 
   `systemctl disable cups.service`

7. Optional: autologin
   As root, create the file /etc/lightdm/lightdm.conf/70-autologin.conf
   with the contents:

   ```
   [SeatDefaults]
   autologin-user=YOUR-USER-NAME
   ```

8. Enable network manager (NM is not active by default on a server, which is the base we use)  

   First try the following:
   
      1. As root, cd to /etc/netplan
      2. Backup and remove all existing files in this folder
      3. Create the file `01-network-manager-all.yaml`, with the contents:
      
      ```
      # Let NetworkManager manage all devices on this system
      network:
          version: 2
          renderer: NetworkManager
      ```
      4. As root, run: `netplan generate` and `netplan apply`
        
         Note: This will eliminate any predefined network connections
         Note: Make sure you perform this step AFTER installing the Xubuntu-core sw (as this installs network-manager)`
   
   If the above did not work, try this:

   Source:
   []https://askubuntu.com/questions/71159/network-manager-says-device-not-managed

     1. sudo nano /etc/NetworkManager/NetworkManager.conf
        change the line `managed=false` to `managed=true`
     2. Backup and then edit `/etc/network/interfaces` to contain EXACTLY:  
       `auto lo`  
       `iface lo inet loopback`  
     3.  Surprisingly, Network Manager wont actually control wired connections w/o the below steps:  
         ```
         su
         cd /etc/NetworkManager/conf.d/
         mv 10-globally-managed-devices.conf orig_10-globally-managed-devices.conf
         touch /etc/NetworkManager/conf.d/10-globally-managed-devices.conf
         ```
     4. Restart Network Manager:   
        `sudo service network-manager restart`

## Author

**Shalom Mitz** - [shalommmitz](https://github.com/shalommmitz)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE ) file for details.

## Credits
Nothing in this repository is new or original.
I did not add references, but almost all the commands below have been googled - you can google them too.


## Appendix A: Iptables configuration files at /etc/iptables:

### The contents of /etc/iptables/rules.ip4: Block all incoming connections

```
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
#-A INPUT -m state --state NEW -m tcp -p TCP --dport 7777 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-port-unreachable
-A FORWARD -j REJECT --reject-with icmp-port-unreachable
COMMIT
```

### The contents of /etc/iptables/rules.ip6: Block everything
```
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -j REJECT
-A OUTPUT -j REJECT
-A FORWARD -j REJECT
COMMIT
```
