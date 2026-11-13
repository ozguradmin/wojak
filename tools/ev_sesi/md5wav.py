#!/usr/bin/env python3
"""md5 of the sample data of a wav (ignores the header)"""
import sys, hashlib, soundfile as sf, numpy as np
for p in sys.argv[1:]:
    y, sr = sf.read(p, dtype="int32")
    print(hashlib.md5(np.ascontiguousarray(y).tobytes()).hexdigest(), sr, y.shape, p)
