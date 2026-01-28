print("Hello from python")
import sys
print(sys.executable)
try:
    import app.core.database
    print("Database module imported")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
