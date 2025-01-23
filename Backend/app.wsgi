import sys
import os
sys.path.insert(0, '/var/www/SecureHub/Backend')
os.chdir('/var/www/SecureHub/Backend')
from app import app as application
