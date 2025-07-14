import sys
import os
import re

def convert_ping_report_to_prom(input_path, output_path):
    with open(input_path) as f:
        lines = f.readlines()

    source_router = None
    source_ip = None
    metrics = []

    #parse headers for source router and loopback IP
    for line in lines:
        if line.startswith("Source Router:"):
            match = re.search(r"Source Router: (\S+)", line)
            if match:
                source_router = match.group(1)
        elif line.startswith("Loopback IP:"):
            match = re.search(r"Loopback IP: ([0-9\.]+)", line)
            if match:
                source_ip = match.group(1)
        if source_router and source_ip:
            break

    pattern_target = re.compile(r"Target: ([0-9\.]+)")
    pattern_loss = re.compile(r"Loss: (\d+)%")
    pattern_avg_latency = re.compile(r"Latency \(ms\): .*avg=(\d+)")

    current_target = None
    packet_loss = None
    avg_latency = None

    for line in lines:
        target_match = pattern_target.search(line)
        if target_match:
            if current_target is not None:
                metrics.append((current_target, packet_loss, avg_latency))
            packet_loss = None
            avg_latency = None
        loss_match = pattern_loss.search(line)
        if loss_match:
            packet_loss = int(loss_match.group(1))
        latency_match = pattern_avg_latency.search(line)
        if latency_match:
            avg_latency = int(latency_match.group(1))

    if current_target is not None:
        metrics.append((current_target, packet_loss, avg_latency))

    with open(output_path, "w") as f:
        f.write(f"# Generated from {input_path}\n")
        f.write("# HELP ping_packet_loss Packet Loss percentage from source to target\n")
        f.write("# TYPE ping_packet_loss gauge\n")
        f.write("# HELP ping_latency_avg_ms Average latency in ms from source to target\n")
        f.write("# TYPE ping_latency_avg_ms gauge\n\n")
        for target, loss, latency in metrics:
            f.write(f'ping_packet_loss{{source="{source_router}", target="{target}"}} {loss}\n')
            f.write(f'ping_latency_avg_ms{{source="{source_router}", target="{target}"}} {latency}\n')

def main():
     folder = "/home/sam/Prometheus/router_metrics"
     for filename in os.listdir(folder):
         if filename.endswith(".txt"):
             txt_path = os.path.join(folder, filename)
             prom_filename = filename.rsplit(',',1)[0] + ".prom"
             prom_path = os.path.join(folder, prom_filename)
             print(f"Processing {txt_path} -> {prom_path}")
             convert_ping_report_to_prom(txt_path, prom_path)
             os.remove(txt_path)
             print(f"Deleted {txt_path}")


if __name__ == "__main__":
    main()
