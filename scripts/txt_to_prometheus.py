import sys
import os
import re
from datetime import datetime

def convert_ping_report_to_prom(input_path, output_path):
    with open(input_path) as f:
        content = f.read()

    #parse headers
    source_router_match = re.search(r"Source Router: (.+?) \(", content)
    source_router = source_router_match.group(1).strip() if source_router_match else "unknown"

    source_ip_match = re.search(r"Source Router: .+?\((.+?)\)", content)
    source_ip = source_ip_match.group(1).strip() if source_ip_match else "unknown"

    loopback_ip_match = re.search(r"Loopback IP: (.+?)\s", content, re.MULTILINE)
    loopback_ip = loopback_ip_match.group(1).strip() if loopback_ip_match else "unknown"

    #parse connectivity results
    metrics = []
    target_pattern = re.compile(
            r"Target: (.+?)\n"
            r"Status: (SUCCESS|FAILED)\n"
            r"Packets: (\d+) sent / (\d+) received\n"
            r"Loss: (\d+)%\n"
            r"Latency \(ms\): min=([\d.]+) avg=([\d.]+) max=([\d.]+)",
            re.DOTALL)


    for match in target_pattern.finditer(content):
        target = match.group(1).strip()
        status = 0 if match.group(2) == "SUCCESS" else 1
        packets_tx = int(match.group(3))
        packets_rx = int(match.group(4))
        packet_loss = float(match.group(5))
        rtt_min = float(match.group(6))
        rtt_avg = float(match.group(7))
        rtt_max = float(match.group(8))
        
        metrics.append({
            "target": target,
            "status": status,
            "packets_tx": packets_tx,
            "packets_rx": packets_rx,
            "packet_loss": packet_loss,
            "rtt_min": rtt_min,
            "rtt_avg": rtt_avg,
            "rtt_max": rtt_max
        })
    
    # Parse summary with improved regex
    summary_match = re.search(
        r"#summary\nSuccessful: (\d+) / (\d+)\nFailed: (\d+)", 
        content, re.IGNORECASE
    )
    successful = int(summary_match.group(1)) if summary_match else 0
    total = int(summary_match.group(2)) if summary_match else 0
    failed = int(summary_match.group(3)) if summary_match else 0
    
    # Write Prometheus metrics
    with open(output_path, "w") as f:
        # Write metadata
        f.write("# HELP ping_metadata Router metadata\n")
        f.write("# TYPE ping_metadata gauge\n")
        f.write(f'ping_metadata{{router="{source_router}", ip="{source_ip}", loopback="{loopback_ip}"}} 1\n\n')
        
        # Write ping metrics
        f.write("# HELP ping_status Ping status (0=success, 1=failure)\n")
        f.write("# TYPE ping_status gauge\n")
        f.write("# HELP ping_packet_loss Packet loss percentage\n")
        f.write("# TYPE ping_packet_loss gauge\n")
        f.write("# HELP ping_rtt_min Minimum round-trip time (ms)\n")
        f.write("# TYPE ping_rtt_min gauge\n")
        f.write("# HELP ping_rtt_avg Average round-trip time (ms)\n")
        f.write("# TYPE ping_rtt_avg gauge\n")
        f.write("# HELP ping_rtt_max Maximum round-trip time (ms)\n")
        f.write("# TYPE ping_rtt_max gauge\n")
        f.write("# HELP ping_packets_tx Packets transmitted\n")
        f.write("# TYPE ping_packets_tx counter\n")
        f.write("# HELP ping_packets_rx Packets received\n")
        f.write("# TYPE ping_packets_rx counter\n\n")
        
        for metric in metrics:
            labels = f'source="{source_router}", target="{metric["target"]}"'
            f.write(f'ping_status{{{labels}}} {metric["status"]}\n')
            f.write(f'ping_packet_loss{{{labels}}} {metric["packet_loss"]}\n')
            f.write(f'ping_rtt_min{{{labels}}} {metric["rtt_min"]}\n')
            f.write(f'ping_rtt_avg{{{labels}}} {metric["rtt_avg"]}\n')
            f.write(f'ping_rtt_max{{{labels}}} {metric["rtt_max"]}\n')
            f.write(f'ping_packets_tx{{{labels}}} {metric["packets_tx"]}\n')
            f.write(f'ping_packets_rx{{{labels}}} {metric["packets_rx"]}\n\n')
        
        # Write summary metrics
        f.write("# HELP ping_successful_total Successful ping targets\n")
        f.write("# TYPE ping_successful_total gauge\n")
        f.write("# HELP ping_failed_total Failed ping targets\n")
        f.write("# TYPE ping_failed_total gauge\n")
        f.write("# HELP ping_targets_total Total ping targets\n")
        f.write("# TYPE ping_targets_total gauge\n\n")
        
        f.write(f'ping_successful_total{{source="{source_router}"}} {successful}\n')
        f.write(f'ping_failed_total{{source="{source_router}"}} {failed}\n')
        f.write(f'ping_targets_total{{source="{source_router}"}} {total}\n')

def main():
    
    base_dir = "/home/sam/Prometheus/router_metrics"
    input_dir = os.path.join(base_dir, "txt_files")
    output_dir = "/var/lib/node_exporter/textfile_collector/"

    #create output directory 
    os.makedirs(output_dir, exist_ok=True)

    # Process each .txt file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            txt_path = os.path.join(input_dir, filename)

            # Create output filename with .prom extension
            base_name = os.path.splitext(filename)[0]
            prom_filename = base_name + ".prom"
            prom_path = os.path.join(output_dir, prom_filename)

            print(f"Processing {txt_path} -> {prom_path}")
            try:
                convert_ping_report_to_prom(txt_path, prom_path)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                traceback.print_exc()

if __name__ == "__main__":
    main()
