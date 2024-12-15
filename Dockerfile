# Use a lightweight Linux base image like Ubuntu
FROM ubuntu:latest

# Metadata
LABEL authors="tkuts"

# Enable Multiarch
RUN dpkg --add-architecture i386
# Install necessary tools and dependencies
RUN apt-get update && \
    apt-get install -y wine:i386 libwine:i386 unzip libsm6:i386
# Install Xvfb and other necessary tools
RUN apt-get install -y xvfb x11-utils x11vnc
RUN apt-get install -y winetricks
# Clean up after installation
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the required files into the container
# Assuming you have these files in the same directory as the Dockerfile
COPY pactest.py /app/
COPY winhttp.dll /app/
COPY example.pac /app/
COPY entrypoint.sh /app/
COPY assets/python-3.12.4-embed-win32.zip /app/

RUN winetricks -q win10
#RUN Xvfb :0 -screen 0 1024x768x16 & DISPLAY=:0.0 winetricks vcrun2015

# Extract the Python embedded package inside the container
RUN unzip python-3.12.4-embed-win32.zip -d python && rm python-3.12.4-embed-win32.zip

#RUN Xvfb :0 -screen 0 1024x768x16 & DISPLAY=:0.0 wine pip /app/python/python.exe -m pip install -r requirements.txt

# Set Wine as the Windows interpreter and run the Python script
CMD ["sh", "./entrypoint.sh"]
