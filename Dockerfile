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
    dash[celery]==2.11.0 \
    dash-bootstrap-components==1.4.1 \
    hay_say_common==0.2.0 \
    gdown==4.7.1 \
    jsonschema==4.17.3 \
    huggingface_hub==0.15.1 \
    pymongo==4.5.0

# Expose port 6573, the port that Hay Say uses
EXPOSE 6573

# download Hay Say
RUN git clone -b main --single-branch -q https://github.com/hydrusbeta/hay_say_ui ~/hay_say/hay_say_ui/

# Start a Celery worker for background callbacks and run the Hay Say Flask server
CMD ["/bin/sh", "-c", "celery --workdir ~/hay_say/hay_say_ui/ -A celery_component:celery_app worker --loglevel=INFO & python /root/hay_say/hay_say_ui/main.py"]

# Todo: use a production server, like gunicorn
# CMD gunicorn --workers=? --threads=? --bind 0.0.0.0:6573 python /root/hay_say/hay_say_ui/main.py:app
