import socket

nb = 1  # 0- HIT-"139.162.222.115", 1 - open HiveMQ - broker.hivemq.com
brokers = [str(socket.gethostbyname('vmm1.saaintertrade.com')), str(socket.gethostbyname('broker.hivemq.com'))]
ports = ['80', '1883']
usernames = ['MATZI', '']  # should be modified for HIT
passwords = ['MATZI', '']  # should be modified for HIT

broker_ip = brokers[nb]
broker_port = ports[nb]
port = ports[nb]
username = usernames[nb]
password = passwords[nb]

mzs = ['matzi/', '']

sub_topics = [mzs[nb] + '#', '#']
pub_topics = [mzs[nb] + 'test', 'test']

sub_topic = sub_topics[nb]
pub_topic = pub_topics[nb]

# Common
conn_time = 0  # 0 stands for endless loop
topic_prefix = 'pr/home/WQM'
manag_time = 10  # sec
topic_alarm = topic_prefix + "alarm"

# SENSORS:
device_id = '1r2v9r5g84g'  # get it on the device sticker on purchase

# 1. Turbidity
base_turbidity = 0.4  # in NTU unit (Total Suspended Solids - TSS)
turbidity_max = 1.0  # in NTU unit (Total Suspended Solids - TSS)

# 2. pH safe range
ph_value_max = 9.5
ph_value_min = 6.5
base_ph_value = 4.5  # should be 7

# 3. Water hardness
base_hardness_value = 110  # in milligram per litter (of CaCO3)
hardness_max = 180
