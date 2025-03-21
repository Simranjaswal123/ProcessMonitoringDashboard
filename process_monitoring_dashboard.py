import psutil
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time


# Module 1: Data Collection
# Module 1: Data Collection
def get_process_data():
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'num_threads', 'io_counters']):
            io_counters = proc.info['io_counters']
            read_bytes = io_counters.read_bytes if io_counters else 0
            write_bytes = io_counters.write_bytes if io_counters else 0

            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'state': proc.info['status'],
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_info'].rss / 1024 / 1024,  # Convert bytes to MB
                'threads': proc.info['num_threads'],
                'io_read': read_bytes / (1024 * 1024),  # Convert bytes to MB
                'io_write': write_bytes / (1024 * 1024)  # Convert bytes to MB
            })
    except Exception as e:
        print(f"Error fetching process data: {e}")
    return processes



# Module 2: GUI Functions
def update_table():
    """Update the process table with current data."""
    # Clear existing table
    for row in tree.get_children():
        tree.delete(row)

    # Fetch and insert new data
    processes = get_process_data()
    for proc in processes:
        tree.insert('', 'end', values=(
            proc['pid'],
            proc['name'],
            proc['state'],
            f"{proc['cpu']:.1f}%",
            f"{proc['memory']:.1f} MB"
        ))

    # Schedule next update (every 5 seconds)
    root.after(5000, update_table)


def terminate_process():
    """Terminate the selected process."""
    selected = tree.selection()
    if selected:
        pid = int(tree.item(selected[0])['values'][0])
        try:
            process = psutil.Process(pid)
            process.terminate()
            update_table()  # Refresh table after termination
        except psutil.NoSuchProcess:
            print(f"Process {pid} no longer exists.")
        except Exception as e:
            print(f"Error terminating process {pid}: {e}")


# Module 3: Data Visualization
def update_cpu_graph():
    """Update the CPU usage graph."""
    global cpu_history
    cpu_history.append(psutil.cpu_percent(interval=1))
    if len(cpu_history) > 20:  # Limit history to 20 points
        cpu_history.pop(0)

    # Clear and redraw plot
    ax.clear()
    ax.plot(cpu_history, color='blue')
    ax.set_title("CPU Usage Over Time (%)")
    ax.set_ylim(0, 100)  # CPU% range
    canvas.draw()

    # Schedule next update
    root.after(1000, update_cpu_graph)  # Update every 1 second


# Main Application Setup
root = tk.Tk()
root.title("Real-Time Process Monitoring Dashboard")
root.geometry("800x600")

# Process Table (Module 2: GUI)
tree = ttk.Treeview(root, columns=('PID', 'Name', 'State', 'CPU%', 'Memory (MB)'), show='headings')
tree.heading('PID', text='PID')
tree.heading('Name', text='Process Name')
tree.heading('State', text='State')
tree.heading('CPU%', text='CPU Usage')
tree.heading('Memory (MB)', text='Memory Usage')
tree.column('PID', width=80)
tree.column('Name', width=200)
tree.column('State', width=100)
tree.column('CPU%', width=100)
tree.column('Memory (MB)', width=100)
tree.pack(pady=10, fill='x')

# Buttons (Module 2: GUI)
button_frame = tk.Frame(root)
button_frame.pack(pady=5)
tk.Button(button_frame, text="Refresh Now", command=update_table).pack(side='left', padx=5)
tk.Button(button_frame, text="Terminate Process", command=terminate_process).pack(side='left', padx=5)

# CPU Graph (Module 3: Visualization)
cpu_history = []
fig, ax = plt.subplots(figsize=(7, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

# Start Updates
update_table()  # Initial table update
update_cpu_graph()  # Initial graph update

# Run the application
root.mainloop()
