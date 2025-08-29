import pandas as pd
import json
import re
from typing import Dict, List, Tuple, Set
import sys

class PIIDetectorRedactor:
    def _init_(self):
        # Patterns for standalone PII
        self.phone_pattern = re.compile(r'\b\d{10}\b')
        self.aadhar_pattern = re.compile(r'\b\d{12}\b')
        self.passport_pattern = re.compile(r'\b[A-Z]{1}\d{7}\b')
        self.upi_pattern = re.compile(r'\b[\w.-]+@[\w.-]+\b')
        
        # Combinatorial PII fields
        self.combinatorial_pii_fields = {'name', 'email', 'address', 'device_id', 'ip_address'}
        
    def detect_pii(self, data: Dict) -> Tuple[bool, Dict]:
        """
        Detect PII in a JSON object and return both detection result and redacted data
        """
        standalone_pii_found = False
        combinatorial_pii_count = 0
        redacted_data = data.copy()
        
        # Check for standalone PII
        for key, value in data.items():
            if isinstance(value, str):
                # Phone number detection
                if key == 'phone' and self.phone_pattern.match(value):
                    standalone_pii_found = True
                    redacted_data[key] = self.redact_phone(value)
                
                # Aadhar detection
                elif key == 'aadhar' and self.aadhar_pattern.match(value):
                    standalone_pii_found = True
                    redacted_data[key] = self.redact_aadhar(value)
                
                # Passport detection
                elif key == 'passport' and self.passport_pattern.match(value):
                    standalone_pii_found = True
                    redacted_data[key] = self.redact_passport(value)
                
                # UPI ID detection
                elif key == 'upi_id' and self.upi_pattern.match(value):
                    standalone_pii_found = True
                    redacted_data[key] = self.redact_upi(value)
                
                # Count combinatorial PII fields
                if key in self.combinatorial_pii_fields:
                    combinatorial_pii_count += 1
        
        # Check for combinatorial PII (at least 2 combinatorial fields)
        combinatorial_pii_found = combinatorial_pii_count >= 2
        
        # Final PII determination
        is_pii = standalone_pii_found or combinatorial_pii_found
        
        # If combinatorial PII is found, redact those fields
        if combinatorial_pii_found:
            for key in self.combinatorial_pii_fields:
                if key in redacted_data:
                    if key == 'name':
                        redacted_data[key] = self.redact_name(redacted_data[key])
                    elif key == 'email':
                        redacted_data[key] = self.redact_email(redacted_data[key])
                    elif key == 'address':
                        redacted_data[key] = self.redact_address(redacted_data[key])
                    elif key == 'device_id':
                        redacted_data[key] = self.redact_device_id(redacted_data[key])
                    elif key == 'ip_address':
                        redacted_data[key] = self.redact_ip_address(redacted_data[key])
        
        return is_pii, redacted_data
    
    def redact_phone(self, phone: str) -> str:
        """Redact phone number while preserving format"""
        return phone[:2] + 'X' * 6 + phone[8:]
    
    def redact_aadhar(self, aadhar: str) -> str:
        """Redact Aadhar number while preserving format"""
        return aadhar[:4] + 'X' * 4 + aadhar[8:]
    
    def redact_passport(self, passport: str) -> str:
        """Redact passport number while preserving format"""
        return passport[0] + 'X' * 6 + passport[7] if len(passport) > 7 else 'X' * 8
    
    def redact_upi(self, upi: str) -> str:
        """Redact UPI ID while preserving format"""
        parts = upi.split('@')
        if len(parts) == 2:
            username = parts[0]
            if len(username) > 2:
                redacted_username = username[:2] + 'X' * (len(username) - 2)
            else:
                redacted_username = 'X' * len(username)
            return redacted_username + '@' + parts[1]
        return 'X' * len(upi)
    
    def redact_name(self, name: str) -> str:
        """Redact name while preserving format"""
        parts = name.split()
        if len(parts) >= 2:
            # Full name with at least first and last name
            redacted_parts = []
            for part in parts:
                if len(part) > 1:
                    redacted_parts.append(part[0] + 'X' * (len(part) - 1))
                else:
                    redacted_parts.append('X')
            return ' '.join(redacted_parts)
        else:
            # Single name part, don't redact as it's not PII alone
            return name
    
    def redact_email(self, email: str) -> str:
        """Redact email while preserving format"""
        parts = email.split('@')
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            if len(username) > 2:
                redacted_username = username[:2] + 'X' * (len(username) - 2)
            else:
                redacted_username = 'X' * len(username)
            return redacted_username + '@' + domain
        return 'X' * len(email)
    
    def redact_address(self, address: str) -> str:
        """Redact address while preserving format"""
        # Simple approach: redact numbers and sensitive parts
        words = address.split()
        redacted_words = []
        for word in words:
            if word.isdigit() and len(word) >= 4:  # Likely a house number or pin code
                redacted_words.append('X' * len(word))
            else:
                redacted_words.append(word)
        return ' '.join(redacted_words)
    
    def redact_device_id(self, device_id: str) -> str:
        """Redact device ID while preserving format"""
        if len(device_id) > 4:
            return device_id[:2] + 'X' * (len(device_id) - 4) + device_id[-2:]
        return 'X' * len(device_id)
    
    def redact_ip_address(self, ip_address: str) -> str:
        """Redact IP address while preserving format"""
        parts = ip_address.split('.')
        if len(parts) == 4:
            return parts[0] + '.' + parts[1] + '.XXX.XXX'
        return 'XXX.XXX.XXX.XXX'

def process_csv(input_file: str, output_file: str):
    """Process the CSV file and generate output with PII detection and redaction"""
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Initialize the PII detector/redactor
    detector = PIIDetectorRedactor()
    
    # Prepare lists for output
    redacted_jsons = []
    is_pii_list = []
    
    # Process each row
    for index, row in df.iterrows():
        try:
            # Parse the JSON data
            data_json = json.loads(row['data_json'].replace("'", '"'))
            
            # Detect PII and get redacted data
            is_pii, redacted_data = detector.detect_pii(data_json)
            
            # Store results
            redacted_jsons.append(json.dumps(redacted_data))
            is_pii_list.append(is_pii)
            
        except json.JSONDecodeError:
            # In case of JSON parsing error, keep original and mark as non-PII
            redacted_jsons.append(row['data_json'])
            is_pii_list.append(False)
    
    # Create output DataFrame
    output_df = pd.DataFrame({
        'record_id': df['record_id'],
        'redacted_data_json': redacted_jsons,
        'is_pii': is_pii_list
    })
    
    # Save to output file
    output_df.to_csv(output_file, index=False)
    
    print(f"Processing complete. Output saved to {output_file}")

if _name_ == "_main_":
    if len(sys.argv) != 2:
        print("Usage: python detector_john_doe.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = "redacted_output_john_doe.csv"
    
    process_csv(input_file, output_file)
