"""系统资源监控脚本

在压测期间持续采集 CPU、内存、磁盘 I/O 指标，保存到 CSV。

用法:
    python tests/load/monitor.py --duration 600 --output results/system_metrics.csv

或在压测脚本中后台启动:
    Start-Process -NoNewWindow python tests/load/monitor.py -ArgumentList "--duration 600"
"""

import argparse
import csv
import os
import time

import psutil


def collect_metrics(duration: int, output_path: str, interval: float = 2.0):
    """采集系统指标

    Args:
        duration: 采集时长（秒）
        output_path: CSV 输出路径
        interval: 采样间隔（秒）
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    process = psutil.Process()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "cpu_percent_total",
            "cpu_percent_process",
            "mem_percent_total",
            "mem_used_gb",
            "mem_process_mb",
            "disk_read_mb_s",
            "disk_write_mb_s",
            "net_sent_mb_s",
            "net_recv_mb_s",
            "open_files",
            "thread_count",
        ])

        start = time.time()
        prev_disk_io = psutil.disk_io_counters()
        prev_net_io = psutil.net_io_counters()
        prev_time = start

        while time.time() - start < duration:
            now = time.time()
            elapsed = now - prev_time
            prev_time = now

            # CPU
            cpu_total = psutil.cpu_percent(interval=0.1)
            cpu_process = process.cpu_percent(interval=0)

            # Memory
            mem = psutil.virtual_memory()
            mem_process = process.memory_info()

            # Disk IO
            disk_io = psutil.disk_io_counters()
            disk_read_rate = (disk_io.read_bytes - prev_disk_io.read_bytes) / (1024 * 1024) / elapsed if elapsed > 0 else 0
            disk_write_rate = (disk_io.write_bytes - prev_disk_io.write_bytes) / (1024 * 1024) / elapsed if elapsed > 0 else 0
            prev_disk_io = disk_io

            # Network IO
            net_io = psutil.net_io_counters()
            net_sent_rate = (net_io.bytes_sent - prev_net_io.bytes_sent) / (1024 * 1024) / elapsed if elapsed > 0 else 0
            net_recv_rate = (net_io.bytes_recv - prev_net_io.bytes_recv) / (1024 * 1024) / elapsed if elapsed > 0 else 0
            prev_net_io = net_io

            # File handles & threads
            try:
                open_files = len(process.open_files())
            except (psutil.AccessDenied, Exception):
                open_files = -1
            thread_count = process.num_threads()

            writer.writerow([
                round(now - start, 1),
                cpu_total,
                cpu_process,
                mem.percent,
                round(mem.used / (1024 ** 3), 2),
                round(mem_process.rss / (1024 * 1024), 1),
                round(disk_read_rate, 2),
                round(disk_write_rate, 2),
                round(net_sent_rate, 2),
                round(net_recv_rate, 2),
                open_files,
                thread_count,
            ])

            # 打印实时状态
            print(f"\r[{now - start:5.0f}s] CPU: {cpu_total:5.1f}% | "
                  f"Mem: {mem.percent:5.1f}% ({mem_process.rss / 1024 / 1024:.0f}MB) | "
                  f"Threads: {thread_count}",
                  end="", flush=True)

            time.sleep(max(0, interval - (time.time() - now)))

    print(f"\n✅ 系统指标已保存至: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="系统资源监控")
    parser.add_argument("--duration", type=int, default=600, help="采集时长（秒）")
    parser.add_argument("--output", type=str, default="results/system_metrics.csv", help="输出路径")
    parser.add_argument("--interval", type=float, default=2.0, help="采样间隔（秒）")
    args = parser.parse_args()

    print(f"📊 系统监控启动: 时长={args.duration}s, 间隔={args.interval}s")
    print(f"   输出: {args.output}")
    collect_metrics(args.duration, args.output, args.interval)
