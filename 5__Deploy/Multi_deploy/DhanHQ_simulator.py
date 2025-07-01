import asyncio
import ast
from collections import deque
import time
import threading
import pickle
import struct
from pathlib import Path
from config import MYPATHS

class SharedTickDataManager:
    """Modified to feed files one by one with notifications"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.data_file = None  # Will be set from main notebook
        self.tick_data = deque()
        self.current_index = 0
        self.total_ticks = 0
        self.is_loaded = False
        self._data_end_printed = False
        self._access_lock = threading.Lock()
        
        # NEW: File-by-file processing
        self.file_list = []
        self.current_file_index = 0
        self.current_file_name = ""
        self.current_file_loaded = False
        self.file_start_callback = None
        
        self._initialized = True
    
    def set_simulation_data_path(self, data_path):
        """Set simulation data path from main notebook"""
        self.data_file = data_path
    
    def set_file_start_callback(self, callback):
        """Set callback function to notify when new file starts"""
        self.file_start_callback = callback
    
    def _discover_files(self, path_input):
        """Same as original - discover and validate simulation files"""
        path = Path(path_input)
        
        if path.is_file():
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            return [str(path)]
        
        elif path.is_dir():
            txt_files = sorted(list(path.glob("*.txt")))
            bin_files = sorted(list(path.glob("*.bin")))
            
            if len(txt_files) + len(bin_files) == 0:
                raise FileNotFoundError(f"No .txt or .bin files found in: {path}")
            
            if len(txt_files) > 0 and len(bin_files) > 0:
                raise ValueError(f"Both .txt and .bin files found in {path}. Please use only one format.")
            
            if txt_files:
                return [str(f) for f in txt_files]
            else:
                return [str(f) for f in bin_files]
        
        else:
            base_path = Path(path_input)
            parent_dir = base_path.parent
            name_without_ext = base_path.stem
            
            txt_file = parent_dir / f"{name_without_ext}.txt"
            bin_file = parent_dir / f"{name_without_ext}.bin"
            
            txt_exists = txt_file.exists()
            bin_exists = bin_file.exists()
            
            if not txt_exists and not bin_exists:
                raise FileNotFoundError(f"Neither {txt_file} nor {bin_file} found")
            
            if txt_exists and bin_exists:
                raise ValueError(f"Both {txt_file} and {bin_file} exist. Please use only one format.")
            
            return [str(txt_file if txt_exists else bin_file)]
    
    def _load_txt_file(self, file_path):
        """Load data from .txt file"""
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    tick_dict = ast.literal_eval(line)
                    self.tick_data.append(tick_dict)
                        
                except (ValueError, SyntaxError) as e:
                    print(f"⚠️ Skipping malformed line {line_num}: {e}")
                    continue
    
    def _load_bin_file(self, file_path):
        """Load data from .bin file"""
        try:
            with open(file_path, 'rb') as file:
                while True:
                    length_data = file.read(4)
                    if len(length_data) != 4:
                        break
                    
                    data_length = struct.unpack('I', length_data)[0]
                    pickled_data = file.read(data_length)
                    
                    if len(pickled_data) != data_length:
                        raise ValueError(f"Binary file corrupted: Expected {data_length} bytes, got {len(pickled_data)}")
                    
                    tick_dict = pickle.loads(pickled_data)
                    self.tick_data.append(tick_dict)
                        
        except pickle.PickleError as e:
            raise ValueError(f"Binary file corrupted: Pickle error - {e}")
        except struct.error as e:
            raise ValueError(f"Binary file corrupted: Structure error - {e}")
        except Exception as e:
            raise ValueError(f"Binary file corrupted: {e}")
    
    def _load_current_file(self):
        """Load current file data"""
        if self.current_file_index >= len(self.file_list):
            return False
        
        current_file_path = self.file_list[self.current_file_index]
        self.current_file_name = Path(current_file_path).name
        
        # Clear previous file data
        self.tick_data.clear()
        self.current_index = 0
        
        # Notify callback about new file start
        if self.file_start_callback:
            try:
                self.file_start_callback(self.current_file_name)
            except Exception as e:
                print(f"⚠️ Callback error: {e}")
                
        try:
            # Load based on file extension
            if current_file_path.lower().endswith('.txt'):
                self._load_txt_file(current_file_path)
            elif current_file_path.lower().endswith('.bin'):
                self._load_bin_file(current_file_path)
            else:
                raise ValueError(f"Unsupported file format: {current_file_path}")
            
            self.total_ticks = len(self.tick_data)
            self.current_file_loaded = True
            
            print(f"✅ from {self.current_file_name}, {self.total_ticks} ticks loaded")
            return True
            
        except Exception as e:
            print(f"❌ Error loading file {self.current_file_name}: {e}")
            raise  # Re-raise error as per requirement #10
    
    def load_tick_data(self, data_path=None, target_security_ids=None):
        """Initialize file discovery - don't load data yet"""
        if self.is_loaded:
            print("📂 Data manager already initialized, skipping...")
            return
        
        # Use provided path or fallback to default if not set
        if data_path:
            file_path_input = data_path
        elif self.data_file:
            file_path_input = self.data_file
        else:
            # Fallback to default if nothing is set
            from config import MYPATHS
            file_path_input = MYPATHS['Raw_data_bin']
                    
        try:
            # Discover all files but don't load yet
            self.file_list = self._discover_files(file_path_input)
            print(f"📂 Discovered {len(self.file_list)} file's from {file_path_input}")
            
            # Load first file
            if self.file_list:
                self._load_current_file()
            
            self.is_loaded = True
            
        except Exception as e:
            print(f"❌ Error discovering files: {e}")
            raise
    
    def get_next_tick(self):
        """Get next tick - load next file when current file ends"""
        with self._access_lock:
            # Check if current file is exhausted
            if self.current_index >= self.total_ticks:
                # Try to load next file
                self.current_file_index += 1
                
                if self.current_file_index >= len(self.file_list):
                    # All files processed
                    if not self._data_end_printed:
                        self._data_end_printed = True
                    return None
                
                # Load next file
                if not self._load_current_file():
                    return None
            
            # Get next tick from current file
            if self.current_index < self.total_ticks:
                tick_data = self.tick_data[self.current_index]
                self.current_index += 1
                return tick_data
            
            return None
    
    def get_stats(self):
        """Get statistics including file progress"""
        file_progress = (self.current_index / self.total_ticks) * 100 if self.total_ticks > 0 else 0
        overall_progress = ((self.current_file_index * 100) + file_progress) / len(self.file_list) if self.file_list else 0
        
        return {
            'total_files': len(self.file_list),
            'current_file_index': self.current_file_index + 1,  # 1-based
            'current_file_name': self.current_file_name,
            'current_file_ticks': self.total_ticks,
            'current_file_progress': file_progress,
            'overall_progress': overall_progress,
            'ticks_fed_current_file': self.current_index,
            'remaining_ticks_current_file': self.total_ticks - self.current_index,
            'is_loaded': self.is_loaded
        }


class MarketFeed:
    """Drop-in replacement for DhanHQ MarketFeed - feeds stored tick data one file at a time"""
    
    # Constants to match original DhanHQ
    NSE = 1
    NSE_FNO = 2
    NSE_CURR = 3
    BSE = 4
    MCX = 5
    BSE_CURR = 7
    BSE_FNO = 8
    
    Ticker = 15
    Quote = 17
    Depth = 19
    Full = 21
    
    def __init__(self, dhan_context, instruments, version='v2'):
        """Initialize simulator with stored data"""
        self.dhan_context = dhan_context
        self.instruments = instruments
        self.version = version
        
        # Extract security_ids from instruments for filtering
        self.target_security_ids = set()
        for instrument in instruments:
            if len(instrument) >= 2:
                self.target_security_ids.add(int(instrument[1]))
        
        # Get shared data manager
        self.data_manager = SharedTickDataManager()
        self.is_connected = False
            
    def set_file_start_callback(self, callback):
        """Set callback for file start notifications"""
        self.data_manager.set_file_start_callback(callback)
    
    async def connect(self):
        """Simulate connection - discover files"""
        print("🔌 Connecting to simulator...")
        
        # Discover files and load first one
        self.data_manager.load_tick_data()
        self.is_connected = True
        print("✅ Simulator connected!")
    
    async def get_instrument_data(self):
        """Return next tick data from current file"""
        if not self.is_connected:
            raise Exception("Simulator not connected. Call connect() first.")
        
        # Get next tick from shared manager
        tick_data = self.data_manager.get_next_tick()
        
        if tick_data is None:
            # Sleep to prevent excessive CPU usage when data ends
            await asyncio.sleep(1)
            return None
        
        # Return tick without filtering
        return tick_data
    
    async def disconnect(self):
        """Simulate disconnection"""
        print("🔌 Disconnecting simulator...")
        self.is_connected = False
        print("✅ Simulator disconnected")
    
    def get_stats(self):
        """Get simulator statistics"""
        stats = self.data_manager.get_stats()
        stats['instance_instruments'] = len(self.target_security_ids)
        return stats