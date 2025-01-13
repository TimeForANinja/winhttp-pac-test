FROM ubuntu:latest

LABEL authors=timeforaninja

# Enable Multiarch, since winhttp requires x32 architecture
RUN dpkg --add-architecture i386
# tune wine (enable 32bit mode & enforce wine directory)
ENV WINEARCH="win32"
ENV WINEPREFIX=/pac-test/.wine/

# Install necessary (generic) tools and dependencies
RUN apt-get update
RUN apt-get install -y curl sudo python3 python3-pip python3-venv
# Dependencies for winhttp - wine 32bit and xvfb as fake display
RUN apt-get install -y wine32 winetricks \
    xorg xvfb x11-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
# Dependencies for v8 - nodejs
RUN curl -sL https://deb.nodesource.com/setup_22.x | sudo -E bash -
RUN apt-get install -y nodejs

# cleanup after installs; reduces docker size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /pac-test

# Copy the required files for installation(s) into the container
COPY engines/ /pac-test/engines/
COPY app /pac-test/app/

# prep v8 - install nodejs dependencies
RUN cd /pac-test/engines/v8 && npm install
# prep eslint - install nodejs dependencies
RUN cd /pac-test/engines/eslint && npm install
# prep winhttp - install python
# yes, the sleep at the end is essential...
RUN xvfb-run wine engines/winhttp/python-3.12.8.exe /quiet PrependPath=1 InstallAllUsers=1 && sleep 10
# overwrite wine dll's with windows native
# some features (e.g. convert_addr) are part of the wine reverse engineered dll but not of the og windows dll
RUN winetricks winhttp wininet
# prep core server - install python dependencies
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    python3 -m pip install --break-system-packages -r /pac-test/app/requirements.txt

# Define health check using the script
COPY healthcheck.sh /pac-test/healthcheck.sh
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 CMD /pac-test/healthcheck.sh

# Copy missing runtime files
COPY entrypoint.sh /pac-test/

# Run the entrypoint which starts the python server using wine
EXPOSE 8080
CMD ["./entrypoint.sh"]
