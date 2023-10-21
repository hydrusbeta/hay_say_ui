# This is a Dockerfile for Synth App, which is not associated with Hay Say as of the time of this writing.
# Synth App is a UI for the text-to-speech architecture "Tacotron".

# Use Nvidia Cuda container base, sync the timezone to GMT, and install necessary package dependencies.
# Cuda 11.8 is used instead of 12 for backwards compatibility. Cuda 11.8 supports compute capability
# 3.5 through 9.0
FROM nvidia/cuda:11.8.0-base-ubuntu20.04
ENV TZ=Etc/GMT
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
	apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    python3.9-venv \
    wget

# Install the official Mega command line, to download the zip file
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    wget https://mega.nz/linux/repo/Debian_11/amd64/megacmd-Debian_11_amd64.deb && \
    apt install -y libc-ares2 libpcrecpp0v5 && \
    dpkg -i megacmd-Debian_11_amd64.deb

# Switch to a limited user
RUN useradd --create-home --shell /bin/bash luna
USER luna

# Install the application and configure it to listen on all addresses (0.0.0.0) instead of only loopback (127.0.0.1)
# Also download the base hifigan models ahead of time for quicker first startup.
RUN mkdir /home/luna/synthapp
WORKDIR /home/luna/synthapp
RUN mega-get https://mega.nz/folder/Zu8HmQhY#mCot1ZTzF64Z2Z4TlXgeig /home/luna/synthapp/ && \
	unzip ./Builds/pony_synth_app_r1d.zip && \
	rm -rf Builds/ && \
	chmod u+x run_linux bin/linux_install_packages bin/micromamba-linux-64 bin/run_webapp && \
	sed -i 's/127.0.0.1/0.0.0.0/' config.py && \
    export CONDA_ALWAYS_YES="true" && \
    ./bin/micromamba-linux-64 create -f bin/f.yaml && \
    mkdir -p models_base/sr/ models_base/hfg/ && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=14fOprFAIlCQkVRxsfInhEPG0n-xN4QOa' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=14fOprFAIlCQkVRxsfInhEPG0n-xN4QOa" -O models_base/sr/Superres_Twilight_33000 && rm -rf /tmp/cookies.txt &&\
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1-cQw1xpZpxZAh5NwfKm_HN5Ga3PP-zi-' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1-cQw1xpZpxZAh5NwfKm_HN5Ga3PP-zi-" -O models_base/hfg/Rarity_HiFiGAN_11000 && rm -rf /tmp/cookies.txt

# Execute the server on startup
CMD ["/bin/sh", "-c", "/home/luna/synthapp/run_linux"]
