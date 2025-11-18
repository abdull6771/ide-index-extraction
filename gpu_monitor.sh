#!/bin/bash

# GPU Monitor Script
# Run this to monitor extraction progress

echo "=================================================="
echo "IDE Index Extraction Monitor"
echo "=================================================="
echo ""

# Function to show system stats
show_stats() {
    echo "📊 System Resources:"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
    echo "RAM: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
    if command -v nvidia-smi &> /dev/null; then
        echo "GPU: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)%"
        echo "GPU RAM: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits)"
    fi
    echo ""
}

# Function to show progress
show_progress() {
    echo "📁 Data Status:"
    if [ -d "data" ]; then
        pdf_count=$(find data -name "*.pdf" -type f | wc -l)
        echo "PDF files: $pdf_count"
    fi

    if [ -d "database" ]; then
        db_files=$(find database -name "*.db" -type f | wc -l)
        echo "Database files: $db_files"
    fi

    if [ -d "outputs" ]; then
        output_files=$(find outputs -type f | wc -l)
        echo "Output files: $output_files"
    fi
    echo ""

    # Show recent logs if they exist
    if [ -f "extraction.log" ]; then
        echo "📝 Recent Log Entries:"
        tail -5 extraction.log 2>/dev/null || echo "No recent logs"
        echo ""
    fi
}

# Function to show running processes
show_processes() {
    echo "⚙️  Running Processes:"
    ps aux | grep -E "(python|extraction)" | grep -v grep || echo "No extraction processes running"
    echo ""
}

# Main monitoring loop
if [ "$1" = "once" ]; then
    show_stats
    show_progress
    show_processes
    exit 0
fi

# Continuous monitoring
echo "Monitoring every 30 seconds... (Ctrl+C to stop)"
echo ""

while true; do
    clear
    echo "=================================================="
    echo "IDE Index Extraction Monitor - $(date)"
    echo "=================================================="
    echo ""
    show_stats
    show_progress
    show_processes
    sleep 30
done