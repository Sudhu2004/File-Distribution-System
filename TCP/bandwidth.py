import psutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Configuration
WINDOW_SIZE = 60  # Number of data points to show

# Initialize deques to hold data
cpu_data = deque(maxlen=WINDOW_SIZE)
memory_data = deque(maxlen=WINDOW_SIZE)
network_data_sent = deque(maxlen=WINDOW_SIZE)
network_data_received = deque(maxlen=WINDOW_SIZE)
times = deque(maxlen=WINDOW_SIZE)

# Set up the figure and axes
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
plt.subplots_adjust(hspace=0.4)

# Initialize lines
line_cpu, = ax1.plot([], [], label='CPU Usage (%)')
line_memory, = ax2.plot([], [], label='Memory Usage (%)')
line_network_sent, = ax3.plot([], [], label='Network Sent (MBps)')
line_network_received, = ax3.plot([], [], label='Network Received (MBps)')

# Set up plot limits and labels
ax1.set_xlim(0, WINDOW_SIZE)
ax1.set_ylim(0, 100)
ax1.set_ylabel('CPU Usage (%)')
ax1.legend(loc='upper right')

ax2.set_xlim(0, WINDOW_SIZE)
ax2.set_ylim(0, 100)
ax2.set_ylabel('Memory Usage (%)')
ax2.legend(loc='upper right')

ax3.set_xlim(0, WINDOW_SIZE)
ax3.set_ylim(0, 5)  # Adjust based on expected network bandwidth
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Network (MBps)')
ax3.legend(loc='upper right')

# Previous net I/O data for bandwidth calculation
prev_sent = psutil.net_io_counters().bytes_sent
prev_recv = psutil.net_io_counters().bytes_recv

def update_plot(frame):
    global prev_sent, prev_recv

    # Append current time
    times.append(len(times))
    
    # CPU usage
    cpu_percent = psutil.cpu_percent()
    cpu_data.append(cpu_percent)
    
    # Memory usage
    memory_percent = psutil.virtual_memory().percent
    memory_data.append(memory_percent)
    
    # Network usage
    net_io = psutil.net_io_counters()
    sent_bandwidth = (net_io.bytes_sent - prev_sent) / 1024 / 1024  # MBps
    received_bandwidth = (net_io.bytes_recv - prev_recv) / 1024 / 1024  # MBps
    prev_sent = net_io.bytes_sent
    prev_recv = net_io.bytes_recv
    
    network_data_sent.append(sent_bandwidth)
    network_data_received.append(received_bandwidth)
    
    # Update lines
    line_cpu.set_data(times, cpu_data)
    line_memory.set_data(times, memory_data)
    line_network_sent.set_data(times, network_data_sent)
    line_network_received.set_data(times, network_data_received)
    
    # Adjust limits
    ax1.set_xlim(max(0, len(times) - WINDOW_SIZE), len(times))
    ax2.set_xlim(max(0, len(times) - WINDOW_SIZE), len(times))
    ax3.set_xlim(max(0, len(times) - WINDOW_SIZE), len(times))
    
    return line_cpu, line_memory, line_network_sent, line_network_received

ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=1000)

plt.show()
