FROM python:3.10-alpine

# Create Working Directory
WORKDIR /app

RUN python3 -m pip install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY tplinkrouter tplinkrouter/

# Set entrypoint
ENTRYPOINT [ "python", "-m", "tplinkrouter.main" ]
