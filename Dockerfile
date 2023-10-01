# Use Nvidia Cuda container base, sync the timezone to GMT, and install necessary package dependencies.
FROM python:3.10
ENV TZ=Etc/GMT
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone.

# Install git, to download code
RUN apt-get update && apt-get install -y git

# Install the official Mega command line, for downloading models stored on the Mega service.
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb &&\
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb &&\
    wget https://mega.nz/linux/repo/Debian_11/amd64/megacmd-Debian_11_amd64.deb &&\
    apt install -y libc-ares2 libpcrecpp0v5 &&\
    dpkg -i megacmd-Debian_11_amd64.deb

# Install all python dependencies for Hay Say.
# Note: Dependencies are installed *before* cloning the repository because the dependencies are likely to change less
# often than the hay_say_ui code itself. Cloning the repo after installing the requirements helps the Docker cache
# optimize build time. See https://docs.docker.com/build/cache
RUN python -m pip install \
    --timeout=300 \
    --no-cache-dir \
    dash[celery]==2.11.0 \
    dash-bootstrap-components==1.4.1 \
    hay_say_common==1.0.2 \
    gdown==4.7.1 \
    jsonschema==4.17.3 \
    huggingface_hub==0.15.1 \
    pymongo==4.5.0 \
    gunicorn==21.2.0 \
    apscheduler==3.10.4

# Expose port 6573, the port that Hay Say uses
EXPOSE 6573

# download Hay Say
RUN git clone -b main --single-branch -q https://github.com/hydrusbeta/hay_say_ui ~/hay_say/hay_say_ui/

# Start Celery workers for background callbacks and run Hay Say on a gunicorn server
CMD ["/bin/sh", "-c", " \
      celery --workdir ~/hay_say/hay_say_ui/ -A celery_download:celery_app worker --loglevel=INFO --concurrency 5 & \
      celery --workdir ~/hay_say/hay_say_ui -A celery_generate:celery_app worker --loglevel=INFO --concurrency 1 & \
      gunicorn --workers 1 --bind 0.0.0.0:6573 'wsgi:get_server()' \
      "]
