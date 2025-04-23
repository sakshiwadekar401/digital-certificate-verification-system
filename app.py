import os
import requests
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
import web3_utils
import hashlib
from datetime import datetime  # Needed for date parsing

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
PINATA_JWT = os.getenv('PINATA_JWT')

uploaded_data = {
    'sha256_hash': None,
    'ipfs_hash': None,
    'ipfs_url': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_certificate', methods=['POST'])
def register_certificate():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if 'certificate' not in request.files:
        flash('No file part')
        return redirect(url_for('admin_dashboard'))

    file = request.files['certificate']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin_dashboard'))

    student_name = request.form.get('student_name')
    course_name = request.form.get('course_name')

    try:
        # Convert issue date from YYYY-MM-DD to Unix timestamp
        issue_date_str = request.form.get('issue_date')
        issue_date = int(datetime.strptime(issue_date_str, "%Y-%m-%d").timestamp())

        # Save file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Calculate SHA-256 hash
        with open(filename, 'rb') as f:
            file_bytes = f.read()
            sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        # Upload to IPFS
        ipfs_hash = None
        ipfs_url = None
        if PINATA_JWT:
            with open(filename, 'rb') as f:
                response = requests.post(
                    url="https://api.pinata.cloud/pinning/pinFileToIPFS",
                    files={"file": (file.filename, f)},
                    headers={"Authorization": f"Bearer {PINATA_JWT}"}
                )

            if response.status_code == 200:
                ipfs_hash = response.json().get('IpfsHash')
                ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
            else:
                flash(f"Failed to upload to IPFS: {response.json().get('error', 'Unknown error')}")

        # Save hash and IPFS info
        uploaded_data['sha256_hash'] = sha256_hash
        uploaded_data['ipfs_hash'] = ipfs_hash
        uploaded_data['ipfs_url'] = ipfs_url

        # Print data for debugging
        print("Student Name:", student_name)
        print("Course Name:", course_name)
        print("Issue Date:", issue_date)
        print("SHA-256 Hash:", sha256_hash)

        # Register on blockchain
        tx_receipt = web3_utils.register_certificate(student_name, course_name, issue_date, sha256_hash)

        if tx_receipt:
            flash(f"Certificate registered successfully! Tx Hash: {tx_receipt.transactionHash.hex()}")
        else:
            flash("Error registering certificate on blockchain.")

    except Exception as e:
        flash(f"Error: {str(e)}")

    return redirect(url_for('admin_dashboard'))

@app.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    if 'certificate' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['certificate']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        with open(filename, 'rb') as f:
            file_bytes = f.read()
            uploaded_sha256_hex = hashlib.sha256(file_bytes).hexdigest()

        stored_certificate_data = web3_utils.get_certificate_data(uploaded_sha256_hex)

        if stored_certificate_data[0]:
            stored_sha256_hex = stored_certificate_data[3]
            if uploaded_sha256_hex == stored_sha256_hex:
                return jsonify({'message': 'Certificate Verified', 'hash': uploaded_sha256_hex})
            else:
                return jsonify({'message': 'Certificate Not Verified'}), 400
        else:
            return jsonify({'message': 'Certificate Not Found on Blockchain'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid login credentials')

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if uploaded_data.get('sha256_hash'):
        cert_data = web3_utils.get_certificate_data(uploaded_data['sha256_hash'])
    else:
        cert_data = None

    events = web3_utils.get_certificate_registered_events()
    debugEvents = web3_utils.get_debug_events()

    return render_template(
        'admin_dashboard.html',
        sha256_hash=uploaded_data.get('sha256_hash'),
        ipfs_hash=uploaded_data.get('ipfs_hash'),
        ipfs_url=uploaded_data.get('ipfs_url'),
        cert_data=cert_data,
        events=events,
        debugEvents=debugEvents,
    )

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
