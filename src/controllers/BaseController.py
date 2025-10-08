from helpers.config import get_settings, Settings
import os
import random
import string

class BaseController:
    """
    Base controller class that can be extended by other controllers.
    This class can contain common methods or properties that all controllers might need.
    """
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files")
        
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )
        

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k = length))

    def get_database_path(self, db_name: str):
        database_path = os.path.join(self.database_dir, db_name)
        
        if not os.path.exists(database_path):
            os.makedirs(database_path)
            
        return database_path
    