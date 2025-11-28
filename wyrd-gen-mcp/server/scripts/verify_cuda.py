#!/usr/bin/env python3
import torch
import sys

def check_cuda():
    print("Python version:", sys.version)
    print("PyTorch version:", torch.__version__)
    
    if torch.cuda.is_available():
        print("\n✅ CUDA is available!")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Device count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"\nDevice {i}: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"  Total Memory: {props.total_memory / 1024**3:.2f} GB")
            print(f"  Major/Minor: {props.major}.{props.minor}")
            
        try:
            x = torch.rand(5, 3).cuda()
            print("\n✅ Tensor creation on GPU successful")
        except Exception as e:
            print(f"\n❌ Tensor creation on GPU failed: {e}")
            
    else:
        print("\n❌ CUDA is NOT available.")
        print("Please check your NVIDIA drivers and PyTorch installation.")

if __name__ == "__main__":
    check_cuda()
