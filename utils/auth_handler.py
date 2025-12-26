"""Authentication handler for MOSIP operations."""
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dynaconf import Dynaconf
from mosip_auth_sdk import MOSIPAuthenticator
from mosip_auth_sdk.models import DemographicsModel


class AuthHandler:
    """Handles all MOSIP authentication operations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the authentication handler.
        
        Args:
            config_path: Path to config.toml file. If None, uses config/config.toml in project directory.
        """
        # Get the project root directory (mosip_auth_gui)
        project_root = Path(__file__).parent.parent
        config_dir = project_root / "config"
        
        if config_path is None:
            # Use config from local config directory
            config_path = str(config_dir / "config.toml")
        
        # Change to config directory so certificate paths in config work correctly
        # (certificates are in the config/ directory)
        original_cwd = os.getcwd()
        try:
            os.chdir(config_dir)
            self.config = Dynaconf(
                settings_files=[str(Path(config_path).name)],  # Just filename since we're in config dir
                environments=False,
            )
            self.authenticator = MOSIPAuthenticator(config=self.config)
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
    
    def perform_kyc(
        self,
        individual_id: str,
        id_type: str,
        demographics_data: DemographicsModel,
        consent: bool = True
    ) -> Dict[str, Any]:
        """
        Perform KYC authentication.
        
        Args:
            individual_id: UIN or VID
            id_type: "UIN" or "VID"
            demographics_data: DemographicsModel instance
            consent: Whether consent has been obtained
            
        Returns:
            Dictionary with 'success', 'data', and 'error' keys
        """
        try:
            # Change to config directory for certificate access
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            original_cwd = os.getcwd()
            try:
                os.chdir(config_dir)
                response = self.authenticator.kyc(
                    individual_id=individual_id,
                    individual_id_type=id_type,
                    demographic_data=demographics_data,
                    consent=consent,
                )
            finally:
                os.chdir(original_cwd)
            
            # Check response status
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'data': None
                }
            
            # Parse response
            if not response.text.strip():
                return {
                    'success': False,
                    'error': 'Empty response received from server',
                    'data': None
                }
            
            response_body = response.json()
            errors = response_body.get("errors") or []
            
            if errors:
                error_messages = []
                for error in errors:
                    error_code = error.get("errorCode", "UNKNOWN")
                    error_msg = error.get("errorMessage", "Unknown error")
                    error_messages.append(f"{error_code}: {error_msg}")
                
                return {
                    'success': False,
                    'error': '\n'.join(error_messages),
                    'data': None
                }
            
            # Decrypt response
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            original_cwd = os.getcwd()
            try:
                os.chdir(config_dir)
                decrypted_response = self.authenticator.decrypt_response(response_body)
            finally:
                os.chdir(original_cwd)
            
            return {
                'success': True,
                'data': decrypted_response,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error during KYC authentication: {str(e)}",
                'data': None
            }
    
    def perform_auth(
        self,
        individual_id: str,
        id_type: str,
        demographics_data: DemographicsModel,
        consent: bool = True
    ) -> Dict[str, Any]:
        """
        Perform demographic authentication.
        
        Args:
            individual_id: UIN or VID
            id_type: "UIN" or "VID"
            demographics_data: DemographicsModel instance
            consent: Whether consent has been obtained
            
        Returns:
            Dictionary with 'success', 'data', 'error', 'authStatus', and 'authToken' keys
        """
        try:
            # Change to config directory for certificate access
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            original_cwd = os.getcwd()
            try:
                os.chdir(config_dir)
                response = self.authenticator.auth(
                    individual_id=individual_id,
                    individual_id_type=id_type,
                    demographic_data=demographics_data,
                    consent=consent,
                )
            finally:
                os.chdir(original_cwd)
            
            # Check response status
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'data': None,
                    'authStatus': False,
                    'authToken': None
                }
            
            # Parse response
            if not response.text.strip():
                return {
                    'success': False,
                    'error': 'Empty response received from server',
                    'data': None,
                    'authStatus': False,
                    'authToken': None
                }
            
            response_body = response.json()
            errors = response_body.get("errors") or []
            
            if errors:
                error_messages = []
                for error in errors:
                    error_code = error.get("errorCode", "UNKNOWN")
                    error_msg = error.get("errorMessage", "Unknown error")
                    error_messages.append(f"{error_code}: {error_msg}")
                
                return {
                    'success': False,
                    'error': '\n'.join(error_messages),
                    'data': response_body,
                    'authStatus': False,
                    'authToken': None
                }
            
            # Extract auth status and token from response
            response_data = response_body.get("response", {})
            auth_status = response_data.get("authStatus", False)
            auth_token = response_data.get("authToken", None)
            
            return {
                'success': True,
                'data': response_body,
                'error': None,
                'authStatus': auth_status,
                'authToken': auth_token
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error during demographic authentication: {str(e)}",
                'data': None,
                'authStatus': False,
                'authToken': None
            }
    
    def generate_otp(
        self,
        individual_id: str,
        id_type: str,
        email: bool = False,
        phone: bool = False
    ) -> Dict[str, Any]:
        """
        Generate OTP.
        
        Args:
            individual_id: UIN or VID
            id_type: "UIN" or "VID"
            email: Send OTP via email
            phone: Send OTP via phone
            
        Returns:
            Dictionary with 'success', 'data', 'error', 'txn_id', 'masked_email', 'masked_mobile' keys
        """
        try:
            # Change to config directory for certificate access
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            original_cwd = os.getcwd()
            try:
                os.chdir(config_dir)
                response = self.authenticator.genotp(
                    individual_id=individual_id,
                    individual_id_type=id_type,
                    email=email,
                    phone=phone,
                )
            finally:
                os.chdir(original_cwd)
            
            # Check response status
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'data': None,
                    'txn_id': None,
                    'masked_email': None,
                    'masked_mobile': None
                }
            
            # Parse response
            if not response.text.strip():
                return {
                    'success': False,
                    'error': 'Empty response received from server',
                    'data': None,
                    'txn_id': None,
                    'masked_email': None,
                    'masked_mobile': None
                }
            
            response_body = response.json()
            errors = response_body.get("errors") or []
            
            if errors:
                error_messages = []
                for error in errors:
                    error_code = error.get("errorCode", "UNKNOWN")
                    error_msg = error.get("errorMessage", "Unknown error")
                    error_messages.append(f"{error_code}: {error_msg}")
                
                return {
                    'success': False,
                    'error': '\n'.join(error_messages),
                    'data': response_body,
                    'txn_id': None,
                    'masked_email': None,
                    'masked_mobile': None
                }
            
            # Extract response data
            response_data = response_body.get("response", {})
            txn_id = response_body.get("transactionID")
            masked_email = response_data.get("maskedEmail")
            masked_mobile = response_data.get("maskedMobile")
            
            return {
                'success': True,
                'data': response_body,
                'error': None,
                'txn_id': txn_id,
                'masked_email': masked_email,
                'masked_mobile': masked_mobile
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error during OTP generation: {str(e)}",
                'data': None,
                'txn_id': None,
                'masked_email': None,
                'masked_mobile': None
            }
    
    def verify_otp(
        self,
        individual_id: str,
        id_type: str,
        otp_value: str,
        txn_id: str,
        consent: bool = True
    ) -> Dict[str, Any]:
        """
        Verify OTP using KYC endpoint.
        
        Args:
            individual_id: UIN or VID
            id_type: "UIN" or "VID"
            otp_value: The OTP value to verify
            txn_id: Transaction ID from generate OTP response
            consent: Whether consent has been obtained
            
        Returns:
            Dictionary with 'success', 'data', and 'error' keys
        """
        try:
            # Change to config directory for certificate access
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            original_cwd = os.getcwd()
            try:
                os.chdir(config_dir)
                response = self.authenticator.kyc(
                    individual_id=individual_id,
                    individual_id_type=id_type,
                    otp_value=otp_value,
                    consent=consent,
                    txn_id=txn_id
                )
            finally:
                os.chdir(original_cwd)
            
            # Check response status
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'data': None
                }
            
            # Parse response
            if not response.text.strip():
                return {
                    'success': False,
                    'error': 'Empty response received from server',
                    'data': None
                }
            
            response_body = response.json()
            errors = response_body.get("errors") or []
            
            if errors:
                error_messages = []
                for error in errors:
                    error_code = error.get("errorCode", "UNKNOWN")
                    error_msg = error.get("errorMessage", "Unknown error")
                    error_messages.append(f"{error_code}: {error_msg}")
                
                return {
                    'success': False,
                    'error': '\n'.join(error_messages),
                    'data': None
                }
            
            # Decrypt response
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"
            original_cwd = os.getcwd()
            try:
                os.chdir(config_dir)
                decrypted_response = self.authenticator.decrypt_response(response_body)
            finally:
                os.chdir(original_cwd)
            
            return {
                'success': True,
                'data': decrypted_response,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error during OTP verification: {str(e)}",
                'data': None
            }
    
    def perform_otp_auth(
        self,
        individual_id: str,
        id_type: str,
        otp_value: str
    ) -> Dict[str, Any]:
        """
        Perform OTP authentication (deprecated - use verify_otp instead).
        
        Args:
            individual_id: UIN or VID
            id_type: "UIN" or "VID"
            otp_value: The OTP value
            
        Returns:
            Dictionary with error message indicating not implemented
        """
        return {
            'success': False,
            'error': 'Use generate_otp and verify_otp methods instead',
            'data': None
        }
