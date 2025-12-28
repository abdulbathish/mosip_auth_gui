# MOSIP IDA Authentication Testing Tool

Reference implementation of a lightweight GUI application for MOSIP IDA authentication operations.

## Installation

### Windows
1. Navigate to `installation/windows/`
2. Double-click `install.bat`
3. After installation, double-click `run.bat` to start

### Mac
1. Navigate to `installation/mac/`
2. Run: `chmod +x install.sh run.sh`
3. Run: `./install.sh`
4. Run: `./run.sh` to start

### Linux
1. Navigate to `installation/linux/`
2. Run: `chmod +x install.sh run.sh`
3. Run: `./install.sh`
4. Run: `./run.sh` to start

## Configuration

### Certificate Files

Place certificate files in the `config/` directory:

- `config/IDA_FIR.pem` - Encryption certificate (PEM format)
- `config/partner1.p12` - Signing and decryption certificate (P12 format)

### Config File

Edit `config/config.toml` with your settings:

#### MOSIP Server Settings
```toml
[mosip_auth_server]
ida_auth_domain_uri = 'https://your-mosip-server.com'
ida_auth_url = 'https://your-mosip-server.com/idauthentication/v1'
```

#### Partner Credentials
```toml
[mosip_auth]
partner_apikey = "YOUR_API_KEY"
partner_misp_lk = "YOUR_MISP_LK"
partner_id = "YOUR_PARTNER_ID"
```

#### Certificate Passwords
```toml
[crypto_encrypt]
decrypt_p12_file_password = "YOUR_PASSWORD"

[crypto_signature]
sign_p12_file_password = 'YOUR_PASSWORD'
```

### GUI Dropdown Configuration

Configure dropdown values in `config/config.toml` under `[gui]` section:

```toml
[gui]
# ID Types dropdown
id_types = ["UIN", "VID"]

# Gender dropdown options
gender_options = ["Male", "Female", "Other"]

# Language dropdown options
languages = ["eng", "ara", "fra"]
```

Modify these arrays to add or remove options. The first item in each list is the default value.

## Usage

1. Start the application using the run script for your OS
2. Select authentication type (KYC Auth is implemented)
3. Enter UIN or VID and select ID type
4. Check boxes for demographic fields to include
5. Fill in values for checked fields
6. Click Submit
7. View results in the Results tab

## Features

- KYC Authentication with checkbox-based field selection
- Dynamic response display (all fields from JSON)
- Photo display with placeholder fallback
- Configurable dropdown values via config file
- Self-contained (all config and certificates in project directory)

## Requirements

- Python 3.10 or higher
- tkinter (included with Python)
- Internet connection for dependency installation

## Project Structure

```
mosip_auth_gui/
├── README.md
├── config/
│   ├── config.toml
│   ├── config.toml.example
│   ├── IDA_FIR.pem
│   └── partner1.p12
├── installation/
│   ├── windows/
│   ├── mac/
│   └── linux/
├── gui/
├── utils/
└── main.py
```

## Notes

- This is a reference implementation
- Only KYC authentication is fully implemented
- OTP and Demographic auth forms are placeholders
- All configuration is in the `config/` directory
- Certificate files must be placed in `config/` directory
