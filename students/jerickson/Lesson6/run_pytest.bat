rem Set the working directory to where this file is located, then run the pytest command
SET mypath=%~dp0
cd %mypath:~0,-1%

pytest --cov=mailroom test_mailroom.py