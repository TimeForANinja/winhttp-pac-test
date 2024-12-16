FROM ubuntu:latest

# Enable Multiarch
RUN dpkg --add-architecture i386
# Install necessary tools and dependencies
RUN apt-get update && \
    apt-get install -y python3:i386 python3-dev:i386 python3-pip wine32 xvfb
# cleanup after installs
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the required files into the container
# Assuming you have these files in the same directory as the Dockerfile
COPY pactest.py /app/
COPY winhttp.dll /app/
COPY requirements.txt /app/
COPY example.pac /app/
COPY assets/python-3.12.8.exe /app/

RUN pip3 install --break-system-packages pyinstaller -r requirements.txt

# Generate the Python executable using PyInstaller
RUN pyinstaller --onefile pactest.py --distpath /app/dist

# prep wine
RUN xvfb-run wine msiexec /i python-3.12.8.exe /L*v log.txt
RUN xvfb-run wine python.exe Scripts/pip.exe install -r requirements.txt

# Set Wine as the Windows interpreter and run the Python script
CMD ["wine", "python.exe", "pactest.py", "example.pac", "google.com"]
