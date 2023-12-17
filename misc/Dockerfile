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

# Install the official Mega command line for downloading the zip file
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    wget https://mega.nz/linux/repo/Debian_11/amd64/megacmd-Debian_11_amd64.deb && \
    apt install -y libc-ares2 libpcrecpp0v5 && \
    dpkg -i megacmd-Debian_11_amd64.deb

# Switch to a limited user
RUN useradd --create-home --shell /bin/bash luna
USER luna

# Download the application. Also download the base hifigan models ahead of time for quicker first startup.
RUN mkdir /home/luna/synthapp
WORKDIR /home/luna/synthapp
RUN mega-get https://mega.nz/folder/Zu8HmQhY#mCot1ZTzF64Z2Z4TlXgeig /home/luna/synthapp/ && \
	unzip ./Builds/pony_synth_app_r1d.zip && \
	rm -rf Builds/ && \
    rm -rf clips/ && \
    mkdir -p models_base/sr/ models_base/hfg/ && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=14fOprFAIlCQkVRxsfInhEPG0n-xN4QOa' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=14fOprFAIlCQkVRxsfInhEPG0n-xN4QOa" -O models_base/sr/Superres_Twilight_33000 && rm -rf /tmp/cookies.txt &&\
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1-cQw1xpZpxZAh5NwfKm_HN5Ga3PP-zi-' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1-cQw1xpZpxZAh5NwfKm_HN5Ga3PP-zi-" -O models_base/hfg/Rarity_HiFiGAN_11000 && rm -rf /tmp/cookies.txt && \
    mkdir website/ponyonline/clips

# Install python module dependencies
RUN chmod u+x run_linux bin/linux_install_packages bin/micromamba-linux-64 bin/run_webapp && \
    printf "\n    - gunicorn==21.2.0" >> bin/f.yaml && \
    printf "\n    - apscheduler==3.10.4" >> bin/f.yaml && \
    export CONDA_ALWAYS_YES="true" && \
    ./bin/micromamba-linux-64 create -f bin/f.yaml

# Configure the main application for a production-like dockerized setting.
# Note: In a true production setting, I recommend downloading all models yourself and then removing the admin/,
# download/, download_model/, and save_model/ views in urls.py, as well as removing the @never_cache annotation
# above get_info() in views.py. Restart the application afterwards for the changes to take effect.
RUN sed -i 's/127.0.0.1/0.0.0.0/' config.py && \
	sed -i 's\DEBUG = True\DEBUG = False\' ./website/ponyonline/ponyonline/settings.py && \
    sed -i 's\po = Popen('"'"'./bin/run_webapp'"'"', shell=True)\pass\' ./bin/webapplauncher.py && \
    # sed -i '162i \ \ \ \ request.session["file_table"] = file_table' website/ponyonline/tts/views.py && \
    # sed -i '161i \ \ \ \ file_table = request.session.get("file_table", {})' website/ponyonline/tts/views.py && \
    sed -i '156d' ./website/ponyonline/tts/views.py && \
    sed -i '156i \ \ \ \ text_filename = re.sub(r"[^A-Za-z0-9]+", "", text[:80])  # For safety' ./website/ponyonline/tts/views.py && \
    sed -i '127d' ./website/ponyonline/tts/views.py && \
    sed -i '127i \ \ \ \ text = re.sub(r"[^A-Za-z0-9!?,.;\'"'"' -]+", "", text)' ./website/ponyonline/tts/views.py && \
    sed -i '127i \ \ \ \ text = unidecode(request.POST.get("text", None))[:250]' ./website/ponyonline/tts/views.py && \
    sed -i '124i @require_http_methods(["POST"])' ./website/ponyonline/tts/views.py && \
    # sed -i '100i \ \ \ \ file_table = request.session.get("file_table", {})' website/ponyonline/tts/views.py && \
    sed -i '95i @require_http_methods(["POST"])' ./website/ponyonline/tts/views.py && \
    sed -i '89i @require_safe' ./website/ponyonline/tts/views.py && \
    sed -i '89i @never_cache' ./website/ponyonline/tts/views.py && \
    # sed -i '76,87d' ./website/ponyonline/tts/views.py && \
    sed -i '56d' ./website/ponyonline/tts/views.py && \
    sed -i '56i @require_safe' ./website/ponyonline/tts/views.py && \
    sed -i '1i from django.views.decorators.cache import never_cache' ./website/ponyonline/tts/views.py && \
    sed -i '1i from django.views.decorators.http import require_http_methods, require_safe' ./website/ponyonline/tts/views.py && \
    sed -i '1i from unidecode import unidecode' ./website/ponyonline/tts/views.py && \
    sed -i '1i import re' ./website/ponyonline/tts/views.py && \
    sed -i 's\@TEST_RAISE_EXCEPTION\TEST_RAISE_EXCEPTION\' ./website/ponyonline/tts/views.py && \
    sed -i '43d' ./website/ponyonline/staticfiles/ttsapp/ttsapp.js && \
    sed -i '43i \ \ \ \ \ \ \ \ type: "GET",' ./website/ponyonline/staticfiles/ttsapp/ttsapp.js

# Rewrite apps.py to register a scheduler that regularly deletes clips older than 24 hours. Make sure the AppConfig is
# added to the INSTALLED_APPS list so that it's ready() method is called on server startup.
RUN printf "import os\nimport time\nfrom datetime import datetime\n\nfrom apscheduler.executors.pool import ThreadPoolExecutor\nfrom apscheduler.schedulers.background import BackgroundScheduler\nfrom django.apps import AppConfig\n\nexecutors = {\n    'default': ThreadPoolExecutor(1)\n}\n\nscheduler = BackgroundScheduler(executors=executors)\nscheduler.start()\n\n\nclass TtsConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'tts'\n\n    def ready(self):\n        # Register job for apscheduler\n        @scheduler.scheduled_job(trigger='interval', seconds=3600, next_run_time=datetime.now())\n        def delete_old_clips():\n            cutoff_in_seconds = 3600*24  # i.e. 24 hours\n            print('Purging clips older than ' + str(cutoff_in_seconds/3600) + ' hours...', flush=True)\n            clip_paths = [os.path.join('./clips', file) for file in os.listdir('./clips')]\n            old_clips = [path for path in clip_paths if (time.time() - os.path.getmtime(path)) > cutoff_in_seconds]\n            for path in old_clips:\n                os.remove(path)\n            print('Old sessions have been purged', flush=True)\n" > ./website/ponyonline/tts/apps.py && \
    sed -i "48i \ \ \ \ 'tts.apps.TtsConfig'," ./website/ponyonline/ponyonline/settings.py

# Execute the helper application on an rpyc ThreadedServer and the main application on gunicorn.
# The gunicorn server listens on all addresses (0.0.0.0) instead of only loopback (127.0.0.1) so you can reach it from outside of the container.
CMD ["/bin/sh", "-c", " \
     ./run_linux & \
     ./bin/micromamba-linux-64 run -n synthapp1 \
        --root-prefix /home/luna/micromamba/ gunicorn \
        --workers 1 \
        --bind 0.0.0.0:3334 \
        --chdir ./website/ponyonline/ \
        ponyonline.wsgi:application"]
