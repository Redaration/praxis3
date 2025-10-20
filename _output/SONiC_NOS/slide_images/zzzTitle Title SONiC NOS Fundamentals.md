# Title: Title: SONiC NOS Fundamentals

*Generated on 2025-07-07*

## 1: What is SONiC NOS

### SONiC Overview

#### Defining SONiC

![Defining SONiC](./slide_Defining_SONiC.png)

![](zzzTitle%20Title%20SONiC%20NOS%20Fundamentals/slide_Verifying_Installation.png)

- Software for Open Networking in the Cloud.
- Open-source network operating system.
- Developed to meet cloud-scale networking demands.
- Supports a wide range of hardware.
- Enables network disaggregation.
- Fosters innovation through community collaboration.

#### Purpose and Goals

![Purpose and Goals](slide_images/slide_Purpose_and_Goals.png)

- To provide a flexible and scalable network OS.
- To enable faster innovation cycles.
- To reduce vendor lock-in.
- To support diverse hardware platforms.
- To simplify network management.
- To facilitate automation and programmability.

#### History and Contributions

![History and Contributions](slide_images/slide_History_and_Contributions.png)

- Originated from its use in large-scale data centers.
- Contributions from major cloud providers and vendors.
- Evolution driven by industry trends.
- Open-source nature encourages community development.
- Adoption across various service providers.
- Continuous improvement through active development.

#### Why SONiC?

![Why SONiC?](slide_images/slide_Why_SONiC?.png)

- Network Disaggregation
- Open Source
- Cloud Scale

## 2: SONiC Architecture

### SONiC Components

#### SONiC System Services (SWSS)

![SONiC System Services (SWSS)](slide_images/slide_SONiC_System_Services_(SWSS).png)

- Central orchestrator for network state.
- Manages configuration and operational data.
- Communicates with other SONiC services.
- Provides notifications on state changes.
- Handles policy enforcement.
- Core of SONiC's state management.

#### Synchronizer Daemon (Syncd)

![Synchronizer Daemon (Syncd)](slide_images/slide_Synchronizer_Daemon_(Syncd).png)

- Translates state from SWSS to SAI.
- Ensures consistency between software and hardware.
- Updates the forwarding plane.
- Receives commands from SWSS.
- Interacts with the ASIC Programming Interface.
- Manages hardware resource allocation.

#### SONiC Abstraction Interface (SAI)

![SONiC Abstraction Interface (SAI)](slide_images/slide_SONiC_Abstraction_Interface_(S.png)

- Standardized API for network silicon.
- Abstracts ASIC-specific details.
- Allows SONiC to run on diverse hardware.
- Defines objects for routing, switching, meters, etc.
- Vendor-neutral interface.
- Enables hardware independence.

#### Configuration Database (Config DB)

![Configuration Database (Config DB)](slide_images/slide_Configuration_Database_(Config.png)

- Centralized repository for network configuration.
- Stores desired network state.
- Written in Redis.
- Used by SWSS to drive configuration.
- Facilitates configuration rollback.
- Critical for state synchronization.

#### Other Key Components (e.g., FRR, gNMI, Orchagent)

![Other Key Components (e.g., FRR, gNMI, Orchagent)](slide_images/slide_Other_Key_Components_(e.g.,_FR.png)

- FRR (Free Range Routing) for routing protocols.
- gNMI for telemetry and configuration.
- Orchagent for application orchestration.
- Various daemons for specific functionalities.
- System services and utilities.
- Foundation for network operations.

### Architecture Overview

#### Microservices-based Design

![Microservices-based Design](slide_images/slide_Microservices-based_Design.png)

- SONiC utilizes a containerized microservices architecture.
- Each network function is a separate service.
- Benefits include modularity and fault isolation.
- Easier to update or replace individual services.
- Enhanced resilience and scalability.
- Promotes independent development.

#### Containerization (Docker)

![Containerization (Docker)](slide_images/slide_Containerization_(Docker).png)

- Services run as Docker containers.
- Provides isolation and portability.
- Simplifies deployment and management.
- Consistent execution environment.
- Facilitates resource management.
- Key for modularity.

#### Data Flow and State Management

![Data Flow and State Management](slide_images/slide_Data_Flow_and_State_Management.png)

- Configuration changes are written to Config DB.
- SWSS processes changes from Config DB.
- SWSS translates changes to SAI API calls.
- Syncd applies SAI calls to the hardware.
- Network state is maintained in SWSS.
- Feedback loop ensures consistency.

### Containerized Microservices Approach

#### Isolation and Dependencies

![Isolation and Dependencies](slide_images/slide_Isolation_and_Dependencies.png)

- Each microservice runs in its own container.
- Minimizes interdependencies between services.
- Prevents issues in one service affecting others.
- Allows for different language stacks.
- Simplifies scaling of specific functions.
- Enhances fault tolerance.

#### Service Orchestration

![Service Orchestration](slide_images/slide_Service_Orchestration.png)

- Container orchestration manages the lifecycle of services.
- Handles starting, stopping, and restarting containers.
- Monitors the health of services.
- Ensures desired state is maintained.
- Facilitates graceful upgrades.
- Key for stability.

#### Upgrades and Updates

![Upgrades and Updates](slide_images/slide_Upgrades_and_Updates.png)

- Individual services can be updated independently.
- Minimizes downtime during upgrades.
- Rollback to previous versions is possible.
- Reduces complexity of system-wide updates.
- Improves agility in adopting new features.
- Leverages container technology benefits.

### SONiC Communication Flows

#### Configuration Update Flow

![Configuration Update Flow](slide_images/slide_Configuration_Update_Flow.png)

- User or automation tool sends config to Config DB.
- SWSS detects the change in Config DB.
- SWSS updates its internal state and generates SAI commands.
- SWSS sends commands to Syncd.
- Syncd translates SAI commands into platform-specific calls.
- Hardware programming is updated.

#### State Notification Flow

![State Notification Flow](slide_images/slide_State_Notification_Flow.png)

- Hardware events trigger updates in the SAI.
- Syncd relays these hardware state changes.
- SWSS receives notifications and updates its state.
- Notifications can be pushed to other interested services.
- Consumers of state information are updated.
- Enables reactive behavior.

#### Inter-Service Communication

![Inter-Service Communication](slide_images/slide_Inter-Service_Communication.png)

- Services communicate via IPC or message queues.
- Pub/Sub model for state changes.
- Redis acts as a central messaging hub.
- REST API and gRPC for external interactions.
- Protocol daemons interact with SWSS.
- Ensures coordinated operation.

## 3: Deploying SONiC

### Hardware Considerations

#### ASIC Support

![ASIC Support](slide_images/slide_ASIC_Support.png)

- SONiC relies on specific ASIC support.
- Network Interface Cards (NICs) have ASICs.
- Supported ASICs determine SONiC compatibility.
- Broadcom, Mellanox, Intel are common vendors.
- SAI drivers are crucial for ASIC interaction.
- Verify platform compatibility matrix.

#### Platforms

![Platforms](slide_images/slide_Platforms.png)

- SONiC can be deployed on bare-metal switches.
- Also supported on virtual machines and emulators.
- Common vendors: Dell, Arista, Juniper (certain models).
- Reference platforms available for testing.
- Consider specific platform features and limitations.
- Ensure hardware meets performance requirements.

#### Resource Requirements

![Resource Requirements](slide_images/slide_Resource_Requirements.png)

- CPU, RAM, and storage needed.
- Varies based on port density and features.
- Use documentation for specific platform needs.
- Ensure sufficient resources for all microservices.
- Over-provisioning is often recommended.
- Impacts overall system stability.

### Installation Methods

#### ONIE (Open Network Install Environment)

![ONIE (Open Network Install Environment)](slide_images/slide_ONIE_(Open_Network_Install_Env.png)

- Standard bootloader for network devices.
- Allows installation of network operating systems.
- SONiC installer integrates with ONIE.
- Network-based or local installation.
- Provides a standardized installation process.
- Typically the preferred method for bare-metal.

#### USB Installation

![USB Installation](slide_images/slide_USB_Installation.png)

- Bootable USB drive with SONiC image.
- Useful for initial deployment or recovery.
- Create USB using tools like Rufus or dd.
- Boot the device from the USB.
- Follow on-screen prompts to install.
- Simple for smaller deployments.

#### PXE Boot Installation

![PXE Boot Installation](slide_images/slide_PXE_Boot_Installation.png)

- Network booting allows remote installation.
- Requires a DHCP and TFTP server.
- Image is downloaded over the network.
- Automates deployment across multiple devices.
- Efficient for large-scale rollouts.
- Needs careful network configuration.

#### Virtual Environments (e.g., KVM, VMware)

![Virtual Environments (e.g., KVM, VMware)](slide_images/slide_Virtual_Environments_(e.g.,_KV.png)

- Install SONiC as a virtual machine.
- Build it from source or use pre-built images.
- Suitable for testing and development.
- Enables simulation of network topologies.
- Verify functionality before physical deployment.
- Testbeds can be easily created.

### Initial Setup and Boot Process

#### First Boot

![First Boot](slide_images/slide_First_Boot.png)

- Device boots into ONIE.
- ONIE detects and loads the SONiC installer.
- Installer partitions the disk and installs SONiC system.
- A minimal set of services starts.
- Initial configuration prompts may appear.
- Basic network connectivity might be established.

#### Network Configuration Steps

![Network Configuration Steps](slide_images/slide_Network_Configuration_Steps.png)

- Assign an IP address to the management interface.
- Configure default gateway.
- Set DNS servers.
- Establish SSH access.
- Basic network connectivity is crucial.
- Ensure reachability for management.

#### Hostname and Credentials

![Hostname and Credentials](slide_images/slide_Hostname_and_Credentials.png)

- Set a unique hostname for the device.
- Configure administrative username and password.
- Secure the device from unauthorized access.
- Follow security best practices.
- Avoid default credentials.
- Plan for password rotation.

#### Verifying Installation

![Verifying Installation](slide_images/slide_Verifying_Installation.png)

- Check running services using `docker ps`.
- Verify network interfaces using `ip addr`.
- Test connectivity to management network.
- Access the SONiC CLI via SSH.
- Review system logs for errors.
- Ensure all critical components are operational.

## 4: Basic SONiC Configuration

### Command Line Interface (CLI) Basics

#### Accessing the CLI

![Accessing the CLI](slide_images/slide_Accessing_the_CLI.png)

- Connect via SSH to the management IP.
- Use console port for initial access if needed.
- Authenticate with provided credentials.
- Standard command prompt indicates successful login.
- Ensure network connectivity to the device.
- Use a secure terminal emulator.

#### Navigation and Structure

![Navigation and Structure](slide_images/slide_Navigation_and_Structure.png)

- Hierarchical command structure exists.
- Use `show` commands to view status.
- Use `config` to enter configuration mode.
- Context-specific commands are available.
- Tab completion aids command entry.
- `help` command provides assistance.

#### Common Commands

![Common Commands](slide_images/slide_Common_Commands.png)

- `show version`: Displays SONiC version and hardware info.
- `show interfaces`: Displays status of network interfaces.
- `show running-config`: Views the current operational configuration.
- `show log`: Displays system logs.
- `show bgp summary`: Shows BGP neighbor status.
- `sudo` command used for privileged operations.

#### Configuration Mode

![Configuration Mode](slide_images/slide_Configuration_Mode.png)

- Enter configuration mode with `config`.
- Changes are staged before committing.
- Exit configuration mode with `exit`.
- Use `commit` to apply changes.
- Use `discard` to revert changes.
- All configuration changes are managed by Config DB.

### Interface Configuration

#### Ethernet Interface Configuration

![Ethernet Interface Configuration](slide_images/slide_Ethernet_Interface_Configurati.png)

- `config interface ethernet <ifname> shutdown`: Shut down an interface.
- `config interface ethernet <ifname> startup`: Bring an interface up.
- `config interface ethernet <ifname> ip address <ip>/<prefix>`: Assign IP address.
- `config interface ethernet <ifname> description "<description>"`: Add a description.
- `config interface ethernet <ifname> alias <alias>`: Set an alias.
- Interface names like Ethernet0, Ethernet1, etc.

#### PortChannel (Link Aggregation) Configuration

![PortChannel (Link Aggregation) Configuration](slide_images/slide_PortChannel_(Link_Aggregation).png)

- `config portchannel <po_name> add <ifname>`: Add member to PortChannel.
- `config portchannel <po_name> del <ifname>`: Remove member from PortChannel.
- `config portchannel <po_name> ip address <ip>/<prefix>`: IP address for PortChannel.
- `config portchannel <po_name> load-balance <algorithm>`: Configure load balancing.
- `config portchannel <po_name> shutdown`: Shut down the PortChannel.
- PortChannel names typically `PortChannel0`, `PortChannel1`, etc.

#### Verifying Interface Status

- `show interfaces status`: Summary of interface states.
- `show interfaces <ifname>`: Detailed information for a specific interface.
- `show ip interface brief`: Shows IP addresses assigned to interfaces.
- `show portchannel summary`: Displays PortChannel configurations and status.
- Check for transmit/receive errors.
- Ensure oper status is up.

### VLANs and Layer 2 Switching

#### VLAN Creation and Configuration

- `config vlan add <vlan_id>`: Create a new VLAN.
- `config vlan <vlan_id> name <vlan_name>`: Assign a name to the VLAN.
- `config vlan <vlan_id> delete`: Delete a VLAN.
- VLANs are represented as FDB entries in SONiC.
- Default VLAN 1 is usually present.
- VLANs are managed via the Config DB.

#### Port VLAN Assignment (Access Ports)

- `config interface ethernet <ifname> switchport mode access`: Set port mode to access.
- `config interface ethernet <ifname> switchport access vlan <vlan_id>`: Assign VLAN to access port.
- Used for connecting end-user devices.
- Traffic is untagged on these ports.
- Specific VLAN membership is enforced.
- Ensure VLAN exists before assignment.

#### Trunk Port Configuration

- `config interface ethernet <ifname> switchport mode trunk`: Set port mode to trunk.
- `config interface ethernet <ifname> switchport trunk allowed vlan <vlan_list>`: Specify allowed VLANs.
- `config interface ethernet <ifname> switchport trunk native vlan <vlan_id>`: Set native VLAN.
- Used for inter-switch links.
- Carries traffic for multiple VLANs.
- VLAN tags are used for identification.

#### Verifying VLAN Configuration

- `show vlan brief`: Lists configured VLANs and associated ports.
- `show interfaces ethernet <ifname> switchport`: Shows switchport mode and VLAN settings.
- `show fdb`: Displays MAC address table.
- `show vlan`: Detailed VLAN information.
- Check port status within specified VLANs.
- Ensure trunk ports allow necessary VLAN traffic.

### IP Addressing and Static Routing

#### IP Addressing

- Assign IP addresses to interfaces (Layer 3).
- `config interface ethernet <ifname> ip address <ip>/<prefix>` command.
- Can be configured on physical interfaces or PortChannels.
- IPv4 and IPv6 are supported.
- Alias IPs can be added: `config interface ethernet <ifname> ip add alias <ip>/<prefix>`.
- Necessary for routing.

#### Static Route Configuration

- `config route add <destination_prefix> <next_hop_ip>`: Add a static route.
- `config route del <destination_prefix> <next_hop_ip>`: Delete a static route.
- Used for simple network topologies or specific path control.
- No dynamic negotiation required.
- Can specify interface for next-hop.
- Useful for default routes.

#### Default Route

- `config route add 0.0.0.0/0 <next_hop_ip>`: Configure default IPv4 route.
- `config route add ::/0 <next_hop_ipv6>`: Configure default IPv6 route.
- Directs traffic to destinations not in the routing table.
- Essential for reaching external networks.
- Usually points to a router or gateway.
- Crucial for internet connectivity.

#### Verifying IP and Routing Configuration

- `show ip route`: Displays the IP routing table.
- `show ipv6 route`: Displays the IPv6 routing table.
- `ping <destination_ip>`: Test reachability.
- `traceroute <destination_ip>`: Trace path to destination.
- Verify IP address assignments using `show ip interface brief`.
- Ensure static routes are correctly populated.

## 5: Advanced Networking with SONiC

### Dynamic Routing Protocols

#### BGP (Border Gateway Protocol)

- `config router bgp as <asn>`: Configure BGP Autonomous System.
- `config router bgp neighbor <neighbor_ip> remote-as <asn>`: Add BGP neighbor.
- `config router bgp neighbor <neighbor_ip> update-source <interface>`: Specify update source.
- `show ip bgp summary`: View BGP neighbor status.
- Used for inter-AS routing and internal routing in large networks.
- Requires careful configuration of AS paths and policies.

#### OSPF (Open Shortest Path First)

- `config router ospf router-id <id>`: Configure OSPF router ID.
- `config router ospf area <area_id> network <network>/<prefix>`: Advertise network into OSPF.
- `show ip ospf neighbor`: Display OSPF neighbor states.
- Link-state routing protocol for interior gateway functions.
- Hierarchical design with areas.
- Generally simpler to configure than BGP.

#### Enabling Protocols

- Need to enable FRR service if not already enabled.
- Configuration commands are managed via Config DB.
- Restarting relevant containers might be needed for changes to take effect.
- Ensure interfaces are up and configured with IP addresses for routing.
- Use `show running-config` to verify configured protocol settings.
- Consult specific SONiC version documentation for exact commands.

#### Verifying Dynamic Routing

- `show ip route <protocol>`: Filter routing table by protocol (e.g., `show ip route bgp`).
- `show <protocol> route`: Show routes learned by a specific protocol.
- `ping` and `traceroute` from L3 interfaces.
- Check routing process logs for errors.
- Ensure routes are correctly exchanged between neighbors.
- Validate next-hop reachability.

### EVPN and VXLAN Overlays

#### Understanding EVPN-VXLAN

- Ethernet VPN (EVPN) control plane for VXLAN.
- VXLAN tunnels encapsulate Layer 2 traffic over Layer 3.
- Provides multi-tenancy and network segmentation.
- EVPN uses BGP to distribute MAC and IP reachability.
- Offers scalable and flexible overlay solutions.
- Replaces traditional VLANs in large data centers.

#### VXLAN Configuration

- `config vxlan add <vxlan_id> <vni>`: Define a VXLAN VNI.
- `config vxlan interface <vxlan_id> <vni>`: Create logical VXLAN interface.
- `config vxlan interface <vxlan_id> src-ip <ip>`: Set source IP for tunnel.
- `config vxlan interface <vxlan_id> udp-port <port>`: Set UDP destination port.
- Tunnel endpoint IP addresses are learned via EVPN.
- VNIs map to L2 broadcast domains.

#### EVPN BGP Configuration

- Enable EVPN address family in BGP.
- `config router bgp activate <neighbor_ip> evpn`: Activate EVPN for a neighbor.
- Configure EVPN route types.
- Automatic MAC and IP advertisement.
- Learning remote MAC/IP via BGP EVPN.
- Crucial for MAC address mobility.

#### Attaching VLANs to VNIs

- `config vlan <vlan_id> vxlan <vni>`: Map a VLAN to a VXLAN VNI.
- Traffic within the VLAN is encapsulated in VXLAN.
- Ensures L2 connectivity across L3 network.
- Can extend L2 segments without physical adjacency.
- Requires careful planning of VNI allocation.
- Essential for overlay functionality.

#### Verifying EVPN-VXLAN

- `show vxlan vni`: List configured VNIs.
- `show bgp evpn summary`: Check EVPN BGP neighbor status.
- `show mac address-table`: Verify MAC addresses learned over EVPN.
- Use ping/traceroute between hosts in different subnets/VLANs.
- Check VXLAN tunnel endpoints.
- Ensure proper traffic forwarding.

### Quality of Service (QoS)

#### QoS Concepts

- Classification: Identifying traffic based on criteria.
- Marking: Setting priority labels (DSCP, CoS).
- Queuing: Prioritizing traffic into different queues.
- Scheduling: Determining the order of queue transmission.
- Policing/Shaping: Controlling traffic rates.
- Congestion management and prevention.

#### QoS Configuration in SONiC

- SONiC supports QoS through its configuration database.
- Configuration involves defining policies, match criteria, actions.
- Commands for setting DSCP values, trust modes.
- Configuration of queues and their properties.
- Dependent on underlying ASIC capabilities.
- Use `show qos` commands to verify.

#### Applying QoS Policies

- Apply classification and marking rules to interfaces.
- Bind queues and schedulers to specific interfaces or ports.
- Set rate limits for specific traffic flows.
- Prioritize real-time traffic like VoIP.
- Ensure fairness for different traffic types.
- Test impact of QoS policies on application performance.

#### Verifying QoS

- `show qos queue`: View queue status and statistics.
- `show qos policy`: Display configured QoS policies.
- Use traffic generators to test behavior.
- Monitor packet drops under congestion.
- Verify DSCP values on egress traffic.

#### QoS Use Cases

- Traffic prioritization for critical applications.
- Bandwidth control for specific users or services.
- Congestion management in data center fabrics.
- Service Level Agreement (SLA) enforcement.
- Differentiated services for different tenants.
- Improve user experience and application responsiveness.

### Access Control Lists (ACLs)

#### ACL Concepts

- Filtering network traffic based on defined rules.
- Rules specify criteria such as source/destination IP, port, protocol.
- Actions include permit, deny, or redirect.
- Applied to interfaces to control inbound or outbound traffic.
- Stateful vs. Stateless ACLs.
- Key for network security and segmentation.

#### ACL Configuration in SONiC

- `config acl add <acl_name> <acl_type>`: Create an ACL.
- `config acl add rule <acl_name> index <seq> <rule_spec>`: Add rules.
- `config acl interface ethernet <ifname> <in/out> <acl_name>`: Apply ACL to interface.
- Rule specifications include src-ip, dst-ip, proto, src-port, dst-port, action.
- Supports IPv4 and IPv6 ACLs.
- Refer to documentation for precise rule syntax.

#### ACL Types (L3/L4, MAC, Port)

- L3/L4 ACLs: Filter based on IP addresses, ports, protocols.
- MAC ACLs: Filter based on source/destination MAC addresses.
- Port ACLs: Filter based on interface names.
- Range ACLs for port or IP ranges.
- Combinations are often used.
- Choose the appropriate type for your needs.

#### Verifying ACLs

- `show acl table`: List all configured ACLs.
- `show acl table <acl_name>`: Show rules within a specific ACL.
- `show acl interface`: Verify ACLs applied to interfaces.
- Test connectivity to ensure rules function as expected.
- Examine packet counters for ACL rules.
- Ensure no unintended traffic is blocked.

## 6: SONiC Management and Monitoring

### Configuration Management

#### SONiC Configuration Database (Config DB)

- Centralized, distributed database for configuration.
- Stores desired state of the network.
- Implemented using Redis.
- State synchronization mechanism.
- Facilitates configuration backup and restore.
- All configuration entities are stored here.

#### Running Configuration vs. Config DB

- Running configuration reflects the current operational state.
- Config DB holds the intended configuration.
- SWSS reconciles Config DB with the actual hardware state.
- Changes made via CLI are applied to Config DB.
- `show running-config` shows configuration from applications.
- Commitment process ensures consistency.

#### Configuration Backup and Restore

- Export configuration: `sudo config save filename.json`.
- Import configuration: `sudo config load filename.json`.
- Store configuration backups securely.
- Use version control for configuration files.
- Automate backup processes.
- Essential for disaster recovery.

### Logging and Syslog

#### SONiC Logging Mechanism

- Logs from various microservices are consolidated.
- Standard syslog format.
- Logs accessible via CLI.
- Centralized logging collectors improve visibility.
- Debugging relies heavily on log analysis.
- Configurable log levels.

#### Viewing Logs

- `show log`: Displays recent log entries.
- `show log --tail`: Follow logs in real-time.
- `show log <service_name>`: View logs for a specific container.
- `/var/log/syslog` for main system logs.
- Logs for individual containers in `/path/to/container/logs`.
- Use `grep` for filtering.

#### Configuring Remote Syslog

- Edit `/etc/rsyslog.conf` or create a new file in `/etc/rsyslog.d/`.
- Add `*.* @<syslog_server_ip>:<port>` for UDP.
- Add `*.* @@<syslog_server_ip>:<port>` for TCP.
- Restart the rsyslog service.
- Ensure network connectivity to the syslog server.
- Centralizing logs provides better analysis.

### SNMP and Telemetry

#### SNMP Support

- SONiC supports SNMP for network management.
- SNMP agent provides access to MIBs.
- Configure SNMP community strings and traps.
- Use `show snmp` commands to verify.
- SNMPv1, v2c, and v3 are typically supported.
- Essential for integration with NMS platforms.

#### Telemetry Mechanisms (gNMI, NetFlow, sFlow)

- gNMI (gRPC Network Management Interface).
- NetFlow/sFlow

#### Configuring Telemetry

- Enable specific telemetry daemons or services.

#### Verifying Telemetry

- Check status of telemetry daemons.
- Verify data flow to collectors.
- Use collector's interface to analyze received data.
- Test specific telemetry subscriptions via gNMI clients.
- Ensure data accuracy and completeness.
- Monitor collector resource utilization.

### Software Upgrades and Downgrades

#### Upgrade Process

- Obtain the new SONiC image.
- Place image on device or network location.
- Use `sudo sonic-installer upgrade <image_path>` command.
- Installer handles partitioning and installation.
- Device reboots into the new version.
- Verify functionality after upgrade.

#### Pre-Upgrade Checks

- Backup current configuration.
- Check release notes for compatibility and known issues.
- Ensure sufficient disk space.
- Test the upgrade process in a lab environment first.
- Notify relevant stakeholders.
- Schedule during a maintenance window if possible.

#### Downgrade Process

- Similar to upgrade, use `sonic-installer downgrade`.
- Requires a previously installed stable version image.
- Rollback to a previous known good state.
- Use configuration backups to restore previous settings.
- Essential if an upgrade introduces critical issues.
- Test downgrade procedure as well.

#### Verifying Software Version

- `show version` command displays the active SONiC version.
- Check boot loader and kernel versions.
- Verify build information.
- Ensure all expected features are present.
- Cross-reference build number with documentation.

## 7: Automation and Programmability

### REST API and gRPC

#### SONiC Management APIs

- Exposes network configuration and operational data.
- REST API for common configuration tasks.
- gRPC for high-performance, streaming telemetry.
- Enables integration with automation frameworks.
- Requires enabling the respective APIs.
- Use tools like Postman or curl for REST.

#### Using REST API

- Authenticate and send HTTP requests (GET, POST, PUT, DELETE).
- Retrieve network state or push configuration changes.
- API endpoints for interfaces, routing, VLANs, etc.
- Data format is typically JSON.
- Automate repetitive configuration tasks.
- Useful for quick scripting.

#### Using gRPC

- Define service contracts using Protocol Buffers.
- Stream telemetry data efficiently.
- Client-server communication model.
- Libraries available for various programming languages.
- Ideal for real-time monitoring and complex control loops.
- Higher learning curve than REST.

### YANG Models

#### What is YANG?

- Data modeling language for network configuration and state.
- Defines the structure of configuration data.
- Standardized for network device configuration.
- Used by NETCONF, RESTCONF, and gNMI.
- Provides a vendor-neutral way of defining data.
- Enhances network programmability.

#### SONiC YANG Models

- SONiC adopts YANG for model-driven configuration.
- Models define SONiC's configuration hierarchy.
- Available models can be explored.
- Contributes to consistent configuration management.
- Facilitates interoperability with other NETCONF/YANG-compliant systems.
- Allows for validation of configuration data.

### Ansible Integration for Configuration Management

#### Ansible Overview

- Open-source automation tool for configuration management.
- Agentless architecture, uses SSH.
- Playbooks written in YAML.
- Manages infrastructure consistently.
- Large ecosystem of modules for various tasks.
- Ideal for network automation.

#### Connecting Ansible to SONiC

- Inventory file lists SONiC devices.
- Use `ansible_network_os: sonic` for SONiC connection.
- Specify connection method (CLI or NETCONF).
- Requires SSH access to SONiC devices.
- Ansible modules specific to SONiC.
- Ensure Python dependencies are met on the controller.

#### SONiC Ansible Modules

- Modules for configuring interfaces, VLANs, routing protocols.
- `sonic_config` module for general configuration.
- `sonic_interface`, `sonic_vlan`, `sonic_bgp` modules.
- Leverage the SONiC Config DB.
- Modules abstract the CLI commands.
- Refer to Ansible documentation for available modules.

#### Creating Playbooks

- Define tasks to configure SONiC devices.
- Use variables for flexibility.
- Implement idempotency.
- Manage configuration drift.
- Automate deployment of new devices.
- Version control playbooks for auditability.

### Python Scripting for SONiC

#### Python and Network Automation

- Python is a popular choice for network automation.
- Rich ecosystem of libraries (Netmiko, NAPALM, ncclient).
- Ability to interact with APIs (REST, gRPC).
- Write custom scripts for specific tasks.
- Automate complex workflows.
- Versatile and powerful for network management.

#### Interacting with SONiC via CLI

- Use `paramiko` or `netmiko` to connect via SSH.
- Execute CLI commands and parse output.
- Handle command execution and error checking.
- Automate tasks previously done manually via CLI.
- Suitable for simpler automation needs.
- Can be fragile if CLI output changes.

#### Interacting with SONiC via APIs

- Use libraries like `requests` for REST API.
- Use `grpcio` for gRPC communication.
- More robust and structured approach.
- Direct interaction with SONiC's management interfaces.
- Query operational data and push configurations.
- Recommended for reliable automation.

#### Libraries for SONiC Automation

- SONiC has native Python libraries and SDKs.
- Use `sonic-py-swsscommon` for SWSS interaction.
- `py-sonic-gold-tests` for testing.
- Creating custom applications and tools.
- Leverage existing Python ecosystems.
- Dive deep into SONiC's internal workings.

## 8: Troubleshooting SONiC

### Common Troubleshooting Commands

#### Interface Troubleshooting

- `show interfaces status`: Check if interfaces are up/down.
- `show interfaces | grep -i error`: Identify interface errors.
- `show interfaces counters`: View detailed packet counters.
- `ip link show`: Linux level interface status.
- `ethtool <interface>`: Advanced detailed interface information.
- Ensure physical connections are secure.

#### Routing Troubleshooting

- `show ip route`: Verify routing table entries.
- `show ip bgp summary`: Check BGP neighbor states.
- `show ip ospf neighbor`: Check OSPF neighbor states.
- `ping` and `traceroute` to test connectivity.
- `show route all`: Display all routes including VRF.
- Ensure routing protocol adjacencies are established.

#### Connectivity Troubleshooting

- `ping`: Test basic IP reachability.
- `traceroute`: Identify path and potential bottlenecks.
- `arp -an`: View ARP cache.
- `ip neigh`: Linux equivalent for ARP cache.
- Check firewall rules or ACLs.
- Verify MTU path discovery.

#### System Health

- `show system info`: Basic system overview.
- `show system resources`: CPU and memory usage.
- `docker ps`: List all running containers.
- `docker logs <container_name>`: Check specific container logs.
- Review system logs for critical errors.
- Monitor resource utilization.

### Log Analysis

#### Identifying Errors

- Look for keywords like "error", "fail", "warn", "critical".
- Correlate logs from different services.
- Timestamp analysis to identify sequences of events.
- Filter logs based on specific components.
- Understand normal log behavior to spot anomalies.
- Use `grep` extensively.

#### Analyzing Specific Issues

- Interface down: Check interface logs, logs related to SAI/SWSS.
- Routing protocol flapping: Examine BGP or OSPF logs for neighbor issues.
- Configuration errors: Check logs for SWSS or relevant config daemons.
- Performance issues: Monitor resource usage logs, buffer statistics.
- Check logs related to the specific service experiencing problems.
- Understand the context of log messages.

#### Log Rotation and Retention

- Configure log rotation policies to manage disk space.
- Understand log retention periods.
- Centralized logging helps in long-term analysis.
- Ensure sufficient log storage.
- Backup logs periodically.
- Avoid losing critical historical data.

### Debugging Network Issues

#### Systematic Approach

- Define the problem clearly.
- Isolate the scope of the issue (single host, segment, entire fabric).
- Verify basic connectivity and configuration.
- Check relevant logs and counters.
- Use diagnostic tools effectively.
- Test hypotheses and changes methodically.

#### Layered Troubleshooting

- Start from Layer 1 (physical links) upwards.
- Check Layer 2 (VLANs, MAC addresses, ARP).
- Verify Layer 3 (IP addressing, routing protocols).
- Examine Layer 4 (ports, TCP/UDP).
- Consider application-layer issues.
- Work your way up the OSI model.

#### Utilizing SONiC Specific Tools

- `swss-cli` for interacting with SWSS.
- Debugging tools within containers.
- `sai-cli` for SAI level debugging.
- Telemetry data for real-time insights.
- Use `show` commands extensively.
- Leverage community resources for common issues.

### Packet Capture and Analysis

#### Packet Capture Tools

- tcpdump: Command-line packet capture utility.
- Wireshark: Powerful graphical packet analyzer.
- SONiC has tcpdump available within containers or via host.
- Capture filters to reduce data volume.
- Capture on specific interfaces.
- Save captures to files for offline analysis.

#### Capturing Packets on SONiC

- Identify the correct interface to capture on.
- Execute `tcpdump -i <interface> -w <filename.pcap>`.
- Use capture filters: `tcpdump -i <interface> 'tcp port 80' -w http.pcap`.
- Access captured files via SCP or SFTP.
- Ensure proper permissions to run tcpdump.
- Consider traffic mirroring (SPAN) for deep analysis.

#### Analyzing Packet Captures

- Open `.pcap` files in Wireshark.
- Analyze packet flow, timing, and content.
- Filter traffic by IP, port, protocol, etc.
- Check for retransmissions, errors, latency.
- Validate protocol behavior.
- Understand how traffic is traversing the network.

#### SPAN and Mirroring

- Configure traffic mirroring on switch ports.
- Mirror specific ingress or egress traffic to a destination port.
- Analyze traffic without impacting the source device.
- Requires a port for monitoring traffic.
- Useful for capturing traffic without installing tools on the device.
- Check platform documentation for mirroring capabilities.

