from core.workflows.main_commands import pipeline_from_upload

pipeline_from_upload("mydoc.pdf")


# import sys
# import os
# import importlib

# print("PYTHON:", sys.executable)
# print("CWD:", os.getcwd())
# print("PATHS:\n", "\n".join(sys.path))

# try:
#     module = importlib.import_module("core.storage.upload_local")
#     print("Module loaded from:", module.__file__)
#     print("upload_file exists:", hasattr(module, "upload_file"))
# except Exception as e:
#     import traceback
#     traceback.print_exc()
