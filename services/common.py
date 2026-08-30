from dal import db
from flask_migrate import Migrate
import re
from urllib.parse import urlparse

class CommonService():
    # US Phone number regex: accepts formats like (123) 456-7890, 123-456-7890, etc.
    US_PHONE_REGEX = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
    
    @staticmethod
    def init_db(app):
        db.init_app(app)

    def migrate_db(app):
        return Migrate(app, db)
    
    @staticmethod
    def validate_phone(phone: str) -> tuple:
        """Validate phone number format.
        
        Returns (is_valid, error_message)
        """
        if not phone:  # Empty is OK (optional field)
            return True, None
        
        if not re.match(CommonService.US_PHONE_REGEX, phone):
            return False, "Phone number must be a valid US phone number (e.g., 123-456-7890 or (123) 456-7890)"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str, field_name: str = "URL") -> tuple:
        """Validate URL has a valid domain (FQDN).
        
        Returns (is_valid, error_message)
        """
        if not url:  # Empty is OK (optional field)
            return True, None
        
        try:
            result = urlparse(url)
            # Check if scheme exists and domain has at least one dot (valid TLD)
            if not result.scheme:
                return False, f"{field_name} must start with http:// or https://"
            if not result.netloc:
                return False, f"{field_name} must have a valid domain"
            if '.' not in result.netloc:
                return False, f"{field_name} must have a valid domain with a TLD (e.g., .com)"
            return True, None
        except Exception as e:
            return False, f"{field_name} is not a valid URL"
