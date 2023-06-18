# Use Nvidia Cuda container base, sync the timezone to GMT, and install necessary package dependencies.
FROM python:3.10
ENV TZ=Etc/GMT
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone.
RUN apt-get update && apt-get install -y git

# Install all python dependencies for Hay Say.
# Note: Dependencies are installed *before* cloning the repository because the dependencies are likely to change less
# often than the hay_say_ui code itself. Cloning the repo after installing the requirements helps the Docker cache
# optimize build time. See https://docs.docker.com/build/cache
RUN python -m pip install \
    dash==2.9.1 \
    dash-bootstrap-components==1.4.1 \
    hay_say_common==0.1.0 \
    gdown==4.7.1 \
    huggingface_hub==0.15.1

# Expose port 6573, the port that Hay Say uses
EXPOSE 6573

# download Hay Say
RUN git clone -b main --single-branch -q https://github.com/hydrusbeta/hay_say_ui ~/hay_say/hay_say_ui/

# Run the Hay Say Flask server on startup
CMD ["/bin/sh", "-c", "python /root/hay_say/hay_say_ui/main.py"]
