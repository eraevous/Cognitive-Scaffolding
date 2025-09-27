Refactored FrameStore.inject_memory to avoid redundant load_frame calls.
Each frame_id now triggers a single disk read, reducing I/O overhead.
Added regression test verifying load_frame call count and output string.
