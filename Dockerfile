# Use Nvidia Cuda container base, sync the timezone to GMT, and install necessary package dependencies.
FROM python:3.10
ENV TZ=Etc/GMT
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone.
RUN apt-get update && apt-get install -y git

# download Hay Say
RUN git clone -b main --single-branch -q https://github.com/hydrusbeta/hay_say_ui ~/hay_say/hay_say_ui/

# Install all python dependencies for Hay Say
RUN python -m pip install -r ~/hay_say/hay_say_ui/requirements.txt

# Expose port 6573, the port that Hay Say uses
EXPOSE 6573

# Run the Hay Say Flask server on startup
CMD ["/bin/sh", "-c", "python /root/hay_say/hay_say_ui/main.py"]
