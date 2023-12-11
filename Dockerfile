# Use Nvidia Cuda container base, sync the timezone to GMT, and install necessary package dependencies.
FROM python:3.10
ENV TZ=Etc/GMT
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install git
RUN apt update && apt install --no-install-recommends -y git

# Install the official Mega command line, for downloading models stored on the Mega service.
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    wget https://mega.nz/linux/repo/Debian_11/amd64/megacmd-Debian_11_amd64.deb && \
    apt install -y libc-ares2 libpcrecpp0v5 && \
    dpkg -i megacmd-Debian_11_amd64.deb

# Create a limited user
ARG LIMITED_USER=luna
RUN useradd --create-home --shell /bin/bash $LIMITED_USER

# Give the limited user ownership over volume mount points
RUN mkdir /home/luna/hay_say && chown $LIMITED_USER:$LIMITED_USER /home/luna/hay_say && \
    mkdir /home/luna/hay_say/models && chown $LIMITED_USER:$LIMITED_USER /home/luna/hay_say/models && \
    mkdir /home/luna/hay_say/audio_cache && chown $LIMITED_USER:$LIMITED_USER /home/luna/hay_say/audio_cache

# Switch to limited user
USER $LIMITED_USER

# Some Docker directives (such as COPY and WORKDIR) and linux command options (such as wget's directory-prefix option)
# do not expand the tilde (~) character to /home/<user>, so define a temporary variable to use instead.
ARG HOME_DIR=/home/$LIMITED_USER

# Install all python dependencies for Hay Say.
# Note: Dependencies are installed *before* cloning the repository because the dependencies are likely to change less
# often than the hay_say_ui code itself. Cloning the repo after installing the requirements helps the Docker cache
# optimize build time. See https://docs.docker.com/build/cache
RUN python -m pip install \
    --timeout=300 \
    --no-cache-dir \
    dash[celery]==2.11.0 \
    dash-bootstrap-components==1.4.1 \
    hay_say_common==1.0.8 \
    gdown==4.7.1 \
    jsonschema==4.17.3 \
    huggingface_hub==0.15.1 \
    pymongo==4.5.0 \
    gunicorn==21.2.0 \
    apscheduler==3.10.4

# Permanently add gunicorn and celery to the path
ENV PATH "$PATH:$HOME_DIR/.local/bin"

# Clone Hay Say
RUN git clone -b main --single-branch -q https://github.com/hydrusbeta/hay_say_ui ~/hay_say/hay_say_ui/

# Expose port 6573, the port that Hay Say uses
EXPOSE 6573

# Start Celery workers for background callbacks and run Hay Say on a gunicorn server
CMD ["/bin/sh", "-c", " \
      celery --workdir ~/hay_say/hay_say_ui/ -A celery_download:celery_app worker --loglevel=INFO --concurrency 5 & \
      celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_gpu:celery_app worker --loglevel=INFO --concurrency 1 & \
      celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_cpu:celery_app worker --loglevel=INFO --concurrency 1 & \
      gunicorn --config=server_initialization.py --workers 1 --bind 0.0.0.0:6573 'wsgi:get_server()' \
    "]
