# Run the main Flask webserver in the background
echo "Starting webserver.py..."
python3 webserver.py &  

# Run the display server
echo "Starting display_server.py..."
python3 display_server.py
