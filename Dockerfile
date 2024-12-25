FROM ubuntu:latest

LABEL authors=timeforaninja

# Enable Multiarch
RUN dpkg --add-architecture i386
# Install necessary tools and dependencies
RUN apt-get update
RUN apt-get install -y wine wine32
RUN apt-get install -y xorg xvfb x11-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
# cleanup after installs, to reduce docker size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app
# winhttp requires x32 architecture, so configure wine accordingly
ENV WINEARCH="win32"

# Copy the required files for python into the container
COPY requirements.txt /app/
COPY install_python.sh /app/
COPY assets/python-3.12.8.exe /app/

# prep python inside wine
RUN ./install_python.sh

# Copy the required files for execution into the container
COPY pactest.py /app/
COPY winhttp.dll /app/
COPY example.pac /app/
COPY entrypoint.sh /app/

# Run the entrypoint which starts the python server using wine
EXPOSE 8080
CMD ["./entrypoint.sh"]
