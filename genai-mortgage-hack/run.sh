#!/bin/bash

echo "🏠 Mortgage Eligibility Engine Launcher"
echo "========================================"
echo ""
echo "Choose which server to run:"
echo "1) Flask app (recommended) - Port 8080"
echo "2) Simple HTTP server - Port 8081"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Starting Flask app on port 8080..."
        echo "Access at: http://localhost:8080"
        python3 app.py
        ;;
    2)
        echo ""
        echo "Starting Simple HTTP server on port 8081..."
        echo "Access at: http://localhost:8081"
        python3 server.py
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
