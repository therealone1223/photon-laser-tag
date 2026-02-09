#!/bin/bash

echo "Updating package list..."
sudo apt update

echo "Installing required dependencies..."
sudo apt install -y python3 python3-psycopg2 postgresq1

echo "Installation complete"
