FROM ubuntu:latest

LABEL authors=timeforaninja

# Enable Multiarch
RUN dpkg --add-architecture i386
# Install necessary tools and dependencies
RUN apt-get update && \
    apt-get install -y wine wine32 xorg xvfb x11-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
# TODO: remove when done debugging
RUN apt-get install -y curl
# cleanup after installs
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app
ENV WINEARCH="win32"

# Copy the required files into the container
COPY requirements.txt /app/
COPY install_python.sh /app/
COPY assets/python-3.12.8.exe /app/

# prep python inside wine
RUN ./install_python.sh

COPY pactest.py /app/
COPY winhttp.dll /app/
COPY example.pac /app/
COPY entrypoint.sh /app/
EXPOSE 8080

# Set Wine as the Windows interpreter and run the Python script
CMD ["./entrypoint.sh"]
#CMD ["xvfb-run", "wine", "python.exe", "pactest.py", "example.pac", "google.com"]
