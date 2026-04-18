from pyaccsharedmemory import accSharedMemory

asm = accSharedMemory()

def read_telemetry():
    return asm.read_shared_memory()

def close_telemetry():
    asm.close()
