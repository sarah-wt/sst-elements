import sst
from mhlib import componentlist

# Define the simulation components
cpu0 = sst.Component("core0", "memHierarchy.standardCPU")
iface0 = cpu0.setSubComponent("memory", "memHierarchy.standardInterface")
cpu0.addParams({
    "memFreq" : 1,
    "memSize" : "1MiB",
    "verbose" : 0,
    "clock" : "2GHz",
    "rngseed" : 1,
    "maxOutstanding" : 32,
    "opCount" : 5000,
    "reqsPerIssue" : 4,
    "write_freq" : 40, # 40% writes
    "read_freq" : 60,  # 60% reads
})
c0_l1cache = sst.Component("l1cache0.msi", "memHierarchy.Cache")
c0_l1cache.addParams({
      "access_latency_cycles" : "5",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "4",
      "cache_line_size" : "64",
      "cache_size" : "4 KB",
      "L1" : "1",
      "debug" : "0"
})
cpu1 = sst.Component("core1", "memHierarchy.standardCPU")
iface1 = cpu1.setSubComponent("memory", "memHierarchy.standardInterface")
cpu1.addParams({
    "memFreq" : 1,
    "memSize" : "1MiB",
    "verbose" : 0,
    "clock" : "2GHz",
    "rngseed" : 2,
    "maxOutstanding" : 32,
    "opCount" : 5000,
    "reqsPerIssue" : 4,
    "write_freq" : 40, # 40% writes
    "read_freq" : 60,  # 60% reads
})
c1_l1cache = sst.Component("l1cache1.msi", "memHierarchy.Cache")
c1_l1cache.addParams({
      "access_latency_cycles" : "5",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "4",
      "cache_line_size" : "64",
      "cache_size" : "4 KB",
      "L1" : "1",
      "debug" : "0"
})
n0_bus = sst.Component("n0.bus", "memHierarchy.Bus")
n0_bus.addParams({
      "bus_frequency" : "2 Ghz"
})
n0_l2cache = sst.Component("l2cache0.msi.inclus", "memHierarchy.Cache")
n0_l2cache.addParams({
      "access_latency_cycles" : "20",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "8",
      "cache_line_size" : "64",
      "cache_size" : "32 KB",
      "debug" : "0"
})
cpu2 = sst.Component("core2", "memHierarchy.standardCPU")
iface2 = cpu2.setSubComponent("memory", "memHierarchy.standardInterface")
cpu2.addParams({
    "memFreq" : 1,
    "memSize" : "1MiB",
    "verbose" : 0,
    "clock" : "2GHz",
    "rngseed" : 2,
    "maxOutstanding" : 32,
    "opCount" : 5000,
    "reqsPerIssue" : 4,
    "write_freq" : 40, # 40% writes
    "read_freq" : 60,  # 60% reads
})
c2_l1cache = sst.Component("l1cache2.msi", "memHierarchy.Cache")
c2_l1cache.addParams({
      "access_latency_cycles" : "5",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "4",
      "cache_line_size" : "64",
      "cache_size" : "4 KB",
      "L1" : "1",
      "debug" : "0"
})
cpu3 = sst.Component("core3", "memHierarchy.standardCPU")
iface3 = cpu3.setSubComponent("memory", "memHierarchy.standardInterface")
cpu3.addParams({
    "memFreq" : 1,
    "memSize" : "1MiB",
    "verbose" : 0,
    "clock" : "2GHz",
    "rngseed" : 3,
    "maxOutstanding" : 32,
    "opCount" : 5000,
    "reqsPerIssue" : 4,
    "write_freq" : 40, # 40% writes
    "read_freq" : 60,  # 60% reads
})
c3_l1cache = sst.Component("l1cache3.msi", "memHierarchy.Cache")
c3_l1cache.addParams({
      "access_latency_cycles" : "5",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "4",
      "cache_line_size" : "64",
      "cache_size" : "4 KB",
      "L1" : "1",
      "debug" : "0"
})
n1_bus = sst.Component("n1.bus", "memHierarchy.Bus")
n1_bus.addParams({
      "bus_frequency" : "2 Ghz"
})
n1_l2cache = sst.Component("l2cache1.msi.inclus", "memHierarchy.Cache")
n1_l2cache.addParams({
      "access_latency_cycles" : "20",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "8",
      "cache_line_size" : "64",
      "cache_size" : "32 KB",
      "debug" : "0"
})
n2_bus = sst.Component("n2.bus", "memHierarchy.Bus")
n2_bus.addParams({
      "bus_frequency" : "2 Ghz"
})
l3cache = sst.Component("l3cache.msi.inclus", "memHierarchy.Cache")
l3cache.addParams({
      "access_latency_cycles" : "100",
      "cache_frequency" : "2 Ghz",
      "replacement_policy" : "lru",
      "coherence_protocol" : "MSI",
      "associativity" : "16",
      "cache_line_size" : "64",
      "cache_size" : "64 KB",
      "debug" : "0",
})
l3tol2 = l3cache.setSubComponent("cpulink", "memHierarchy.MemLink")
l3NIC = l3cache.setSubComponent("memlink", "memHierarchy.MemNIC")
l3NIC.addParams({
    "group" : 1,
    "network_bw" : "25GB/s",
})
network = sst.Component("network", "merlin.hr_router")
network.addParams({
      "xbar_bw" : "1GB/s",
      "link_bw" : "1GB/s",
      "input_buf_size" : "1KB",
      "num_ports" : "2",
      "flit_size" : "72B",
      "output_buf_size" : "1KB",
      "id" : "0",
      "topology" : "merlin.singlerouter"
})
network.setSubComponent("topology","merlin.singlerouter")
dirctrl = sst.Component("directory.msi", "memHierarchy.DirectoryController")
dirctrl.addParams({
    "coherence_protocol" : "MSI",
    "debug" : "0",
    "entry_cache_size" : "32768",
    "addr_range_end" : "0x1F000000",
    "addr_range_start" : "0x0"
})
dirtoM = dirctrl.setSubComponent("memlink", "memHierarchy.MemLink")
dirNIC = dirctrl.setSubComponent("cpulink", "memHierarchy.MemNIC")
dirNIC.addParams({
    "group" : 2,
    "network_bw" : "25GB/s",
})
memctrl = sst.Component("memory", "memHierarchy.MemController")
memctrl.addParams({
    "debug" : "0",
    "clock" : "1GHz",
    "request_width" : "64",
    "addr_range_end" : 512*1024*1024-1,
})
memory = memctrl.setSubComponent("backend", "memHierarchy.vaultsim")
memory.addParams({
    "access_time" : "2 ns",   # Phy latency
    "mem_size" : "512MiB",
})
logic_layer = sst.Component("logic_layer", "vaultsim.logicLayer")
logic_layer.addParams({
    "clock" : "1GHz",
    "bwlimit" : "32",
    "vaults" : "8",
    "terminal" : 1,
    "llID" : 0,
    "LL_MASK" : 0
})

vault0 = sst.Component("vault_0", "vaultsim.vaultsim")
vault0.addParams({
    "clock" : "500MHz",
    "VaultID" : 0,
    "numVaults2" : 3
})

vault1 = sst.Component("vault_1", "vaultsim.vaultsim")
vault1.addParams({
    "clock" : "500MHz",
    "VaultID" : 1,
    "numVaults2" : 3
})

vault2 = sst.Component("vault_2", "vaultsim.vaultsim")
vault2.addParams({
    "clock" : "500MHz",
    "VaultID" : 2,
    "numVaults2" : 3
})

vault3 = sst.Component("vault_3", "vaultsim.vaultsim")
vault3.addParams({
    "clock" : "500MHz",
    "VaultID" : 3,
    "numVaults2" : 3
})

vault4 = sst.Component("vault_4", "vaultsim.vaultsim")
vault4.addParams({
    "clock" : "500MHz",
    "VaultID" : 4,
    "numVaults2" : 3
})

vault5 = sst.Component("vault_5", "vaultsim.vaultsim")
vault5.addParams({
    "clock" : "500MHz",
    "VaultID" : 5,
    "numVaults2" : 3
})

vault6 = sst.Component("vault_6", "vaultsim.vaultsim")
vault6.addParams({
    "clock" : "500MHz",
    "VaultID" : 6,
    "numVaults2" : 3
})

vault7 = sst.Component("vault_7", "vaultsim.vaultsim")
vault7.addParams({
    "clock" : "500MHz",
    "VaultID" : 7,
    "numVaults2" : 3
})

# Enable statistics
sst.setStatisticLoadLevel(7)
sst.setStatisticOutput("sst.statOutputConsole")
for a in componentlist:
    sst.enableAllStatisticsForComponentType(a)


# Define the simulation links
link_c0_l1cache = sst.Link("link_c0_l1cache")
link_c0_l1cache.connect( (iface0, "port", "1000ps"), (c0_l1cache, "high_network_0", "1000ps") )
link_c0L1cache_bus = sst.Link("link_c0L1cache_bus")
link_c0L1cache_bus.connect( (c0_l1cache, "low_network_0", "10000ps"), (n0_bus, "high_network_0", "10000ps") )
link_c1_l1cache = sst.Link("link_c1_l1cache")
link_c1_l1cache.connect( (iface1, "port", "1000ps"), (c1_l1cache, "high_network_0", "1000ps") )
link_c1L1cache_bus = sst.Link("link_c1L1cache_bus")
link_c1L1cache_bus.connect( (c1_l1cache, "low_network_0", "10000ps"), (n0_bus, "high_network_1", "10000ps") )
link_bus_n0L2cache = sst.Link("link_bus_n0L2cache")
link_bus_n0L2cache.connect( (n0_bus, "low_network_0", "10000ps"), (n0_l2cache, "high_network_0", "10000ps") )
link_n0L2cache_bus = sst.Link("link_n0L2cache_bus")
link_n0L2cache_bus.connect( (n0_l2cache, "low_network_0", "10000ps"), (n2_bus, "high_network_0", "10000ps") )
link_c2_l1cache = sst.Link("link_c2_l1cache")
link_c2_l1cache.connect( (iface2, "port", "1000ps"), (c2_l1cache, "high_network_0", "1000ps") )
link_c2L1cache_bus = sst.Link("link_c2L1cache_bus")
link_c2L1cache_bus.connect( (c2_l1cache, "low_network_0", "10000ps"), (n1_bus, "high_network_0", "10000ps") )
link_c3_l1cache = sst.Link("link_c3_l1cache")
link_c3_l1cache.connect( (iface3, "port", "1000ps"), (c3_l1cache, "high_network_0", "1000ps") )
link_c3L1cache_bus = sst.Link("link_c3L1cache_bus")
link_c3L1cache_bus.connect( (c3_l1cache, "low_network_0", "10000ps"), (n1_bus, "high_network_1", "10000ps") )
link_bus_n1L2cache = sst.Link("link_bus_n1L2cache")
link_bus_n1L2cache.connect( (n1_bus, "low_network_0", "10000ps"), (n1_l2cache, "high_network_0", "10000ps") )
link_n1L2cache_bus = sst.Link("link_n1L2cache_bus")
link_n1L2cache_bus.connect( (n1_l2cache, "low_network_0", "10000ps"), (n2_bus, "high_network_1", "10000ps") )
link_bus_l3cache = sst.Link("link_bus_l3cache")
link_bus_l3cache.connect( (n2_bus, "low_network_0", "10000ps"), (l3tol2, "port", "10000ps") )
link_cache_net_0 = sst.Link("link_cache_net_0")
link_cache_net_0.connect( (l3NIC, "port", "10000ps"), (network, "port1", "2000ps") )
link_dir_net_0 = sst.Link("link_dir_net_0")
link_dir_net_0.connect( (network, "port0", "2000ps"), (dirNIC, "port", "2000ps") )
link_dir_mem_link = sst.Link("link_dir_mem_link")
link_dir_mem_link.connect( (dirtoM, "port", "10000ps"), (memctrl, "direct_link", "10000ps") )
link_dir_cube_link = sst.Link("link_dir_cube_link")
link_dir_cube_link.connect( (memory, "cube_link", "2ns"), (logic_layer, "toCPU", "2ns") )
link_logic_v0 = sst.Link("link_logic_v0")
link_logic_v0.connect( (logic_layer, "bus_0", "500ps"), (vault0, "bus", "500ps") )
link_logic_v1 = sst.Link("link_logic_v1")
link_logic_v1.connect( (logic_layer, "bus_1", "500ps"), (vault1, "bus", "500ps") )
link_logic_v2 = sst.Link("link_logic_v2")
link_logic_v2.connect( (logic_layer, "bus_2", "500ps"), (vault2, "bus", "500ps") )
link_logic_v3 = sst.Link("link_logic_v3")
link_logic_v3.connect( (logic_layer, "bus_3", "500ps"), (vault3, "bus", "500ps") )
link_logic_v4 = sst.Link("link_logic_v4")
link_logic_v4.connect( (logic_layer, "bus_4", "500ps"), (vault4, "bus", "500ps") )
link_logic_v5 = sst.Link("link_logic_v5")
link_logic_v5.connect( (logic_layer, "bus_5", "500ps"), (vault5, "bus", "500ps") )
link_logic_v6 = sst.Link("link_logic_v6")
link_logic_v6.connect( (logic_layer, "bus_6", "500ps"), (vault6, "bus", "500ps") )
link_logic_v7 = sst.Link("link_logic_v7")
link_logic_v7.connect( (logic_layer, "bus_7", "500ps"), (vault7, "bus", "500ps") )
