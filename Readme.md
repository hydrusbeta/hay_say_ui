![image showing the Hay Say UI](documentation%20images/Hay%20Say%20UI.png) 

## What is Hay Say?

Hay Say is a user interface for generating pony voices. From a single UI, you can generate voices or perform voice 
conversion from AI architectures such as so-vits-svc (https://github.com/svc-develop-team/so-vits-svc), Controllable 
TalkNet (https://github.com/SortAnon/ControllableTalkNet) and RVC 
(https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI). At the moment, all supported AI architectures can run locally and do 
not require an internet connection except to download character models.

## The Motivation Behind Hay Say

Over the past few years, many AI architectures have emerged for accomplishing text-to-speech generation and voice 
conversion ("speech-to-speech"). Many of these new technologies did not have a graphical user interface when they 
first became available. Each time a new technology has entered into the awareness of the Pony Preservation Project 
thread at /mlp on 4chan, someone has had to develop a new UI to make the technology accessible to others. This has lead 
to a collection of user interfaces over time, each one unique to a particular AI architecture and with features that are
not available in the other UIs. The primary motivation behind Hay Say is to create a unified user experience for all the
voice generation solutions. Preprocessing and postprocessing options are separated from architecture-specific options so
that every architecture can benefit from new pre- or post-processing features. With a UI framework already in place, it 
should be possible to give new architectures a usable UI more quickly by integrating them with Hay Say.

A secondary motivation behind Hay Say is to reduce user frustration with installing software. Falling into Python's 
"dependency hell" seems to be a common pain point when users try to install voice generation software locally. Hay Say 
addresses this issue by pre-installing all the AI solutions into their own Docker images. Users simply need to install 
Docker and pull the pre-built images.

## Installation Instructions

Important: Be aware that Hay Say will need to download at least 41 GB of compressed Docker images, so expect it to take 
a while to start up the first time you run it. It should come up quickly after that. The exact amount of time required 
for the initial startup depends, of course, on your internet speed. 

Before you install Hay Say, I recommend you take a look at the Testing Data / Benchmarks section at the bottom of this 
page to get a ballpark figure on how fast or slow Hay Say might be on your machine.

### Required Hardware
* At least 50 GB free Hard drive space (additional space is required for any models you download within the application)
* 12 GB System RAM (Hay Say only uses up to ~8 GB RAM, but don't forget that your OS needs RAM too)

### Recommended Hardware and Software
* A fast CPU - or - an Nvidia GPU with a Cuda compute capability of 3.5 or higher.
* Hay Say was tested and worked well on the following Operating Systems. It may or may not work on other operating 
  systems.:
  * Windows 10
  * Windows 11
  * Ubuntu 22.10
  * Ubuntu 23.04

#### A Note on MacOS
I also tested Hay Say on MacOS 13.3.1 (Ventura) with Apple Silicon M2. I was unable to generate audio with Controllable 
TalkNet, and so-vits-svc (3.0 and 4.0) was unusably slow even though the machine was brand new (see Testing Data / 
Benchmarks section). I do not recommend running Hay Say on Apple Silicon. It is unknown whether it works any better on 
Macs with Intel chips.

### Windows Installation Instructions

1. Install Docker Desktop:  
	https://www.docker.com/
2. Start Docker Desktop and wait until it has finished loading.
	If you get a popup window stating "Docker Desktop requires a newer WSL kernel version", then open a command prompt, 
execute the command `wsl --update`, and then start Docker Desktop again.
3. Open a command prompt and execute the following commands:
    ```
    curl.exe --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
    docker volume create models
    docker volume create audio_cache
    docker compose up
    ```

Note: You might get a Windows Defender Firewall popup. You can safely close that window. No special firewall rules are 
required to run Hay Say.

Hay Say will take time to download the large Docker images (~41 GB). Once it is done, you should see output like the 
following:
![](documentation%20images/Windows%20ready%20to%20roll.png)

Open a web browser and go to the following URL:  
http://127.0.0.1:6573/

#### Stopping Hay Say
To stop Hay Say, go to the Command Prompt that you ran "docker compose up" in earlier and type CTRL+C. It will take 
10-30 seconds for Docker to gracefully shut down all of the containers.
I also recommend shutting down Docker Desktop. Right click on the Whale icon in the taskbar and select "Quit Docker 
Desktop".

#### Starting Hay Say Again 
To start Hay Say again, first make sure that the Docker Engine is running. You can check for Docker Engine in the 
taskbar:  
![image showing the Docker whale icon in a Windows Taskbar](documentation%20images/windows%20docker%20icon.png)  
If it is not running, you can start it by launching Docker Desktop. 
Then, open Command Prompt and type the following command:
```
docker compose up
```
Note: When you run that command, you must be in the folder where docker-compose.yaml is located (you downloaded it 
earlier when you executed the `curl` command in step 3 above). If you get an error stating `no configuration file 
provided: not found`, then cd to that directory first.


### Linux Installation Instructions

1. Install Docker Engine. This can be done in several ways according to preference. See 
https://docs.docker.com/engine/install/ubuntu. Note: By default, Docker needs to be run with superuser privileges. 
However, it is possible to install it in a way that lets you run it in rootless mode if you prefer (see 
https://docs.docker.com/engine/security/rootless/). Hay Say will run in a rootless configuration just fine on CPU, but 
if you want it to use a Cuda GPU, then you will need to perform some additional configuration. See 
[Enabling GPU Integration](#enabling-gpu-integration).

2. Open a terminal and execute the following commands:
    ```shell
    wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
    sudo docker volume create models
    sudo docker volume create audio_cache
    sudo docker compose up
    ```

Hay Say will take time to download the large Docker images (~41 GB). Once it is done, you should see output like the 
following:  
![](documentation%20images/Linux%20ready%20to%20roll.png)

Open a web browser and go to the following URL:  
http://127.0.0.1:6573/

#### Stopping Hay Say
To stop Hay Say, go to the terminal where you ran "docker compose up" earlier and type CTRL+C. It will take 10-30 
seconds for Docker to gracefully shut down all of the containers.

#### Starting Hay Say Again 
To start Hay Say again, open a terminal and type the following command:
```shell
sudo docker compose up
```
Note: When you run that command, you must be in the folder where docker-compose.yaml is located (you downloaded it 
earlier when you executed the `wget` command in step 2 above). If you get an error stating `no configuration file 
provided: not found`, then cd to that directory first.



### MacOS Installation Instructions

Important! Hay Say did not run well on Apple Silicon during my testing. See "A Note on MacOS" in the Recommended 
Hardware and Software section, above. But here are the steps in case you want to give it a try anyways.

1. Install Docker Desktop (note: if you are running MacOS on Apple Silicon (e.g. M1 or M2), make sure you download the
version for Apple Silicon):  
	https://www.docker.com/
2. Start Docker Desktop and wait until it has finished loading.
3. Open a terminal and execute the following commands:
```zsh
curl --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker volume create models
docker volume create audio_cache
docker compose up
```

Hay Say will take time to download the large Docker images (~41 GB). Once it is done, you should see output like the 
following:
![](documentation%20images/macOS%20ready%20to%20roll.png)

Open a web browser and go to the following URL:  
http://127.0.0.1:6573/

#### Stopping Hay Say
To stop Hay Say, go to the Terminal where you ran "docker compose up" earlier and type CTRL+C. It will take 10-30 
seconds for Docker to gracefully shut down all of the containers. I also recommend shutting down Docker Desktop. Right 
click on the Whale icon in the taskbar and select "Quit Docker Desktop".


#### Starting Hay Say Again 
To start Hay Say again, first make sure that the Docker Engine is running. You can check for Docker Engine in the 
taskbar:
![image showing the Docker whale icon in a MacOS Taskbar](documentation%20images/macOS%20docker%20icon.png)  
If it is not running, you can start it by launching Docker Desktop
Then open a terminal and type the following command
```zsh
sudo docker compose up
```
Note: When you run that command, you must be in the folder where docker-compose.yaml is located (you downloaded it 
earlier when you executed the `curl` command in step 3 above). If you get an error stating `no configuration file 
provided: not found`, then cd to that directory first.

## Updating Hay Say
Note: if you last installed/updated Hay Say before Aug 19, 2023, please see 
[Special Instructions for the Aug 19, 2023 update](#special-instructions-for-the-aug-19-2023-update)
If you last installed/updated Hay Say between Aug 19, 2023 and Dec 11, 2023, please see [Special Instructions for the 
Dec 11, 2023 update](#special-instructions-for-the-dec-10-2023-update)

### 1. Grab the latest docker-compose file 
To update Hay Say, first download the latest docker-compose.yaml file by executing the following command. Please note 
that this will overwrite your existing docker-compose file. If you made any edits to your old docker-compose file (e.g. 
uncommenting lines to enable Hay Say to use your Cuda GPU or commenting out lines to make it download only specific 
architectures), you will need to make the same edits to the new file:

Linux:
```shell
wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml  
```
Windows:
```
curl.exe --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
```
MacOS:
```zsh
curl --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
```

### 2. Pull the latest images
Next, execute the following commands to make sure that your containers are stopped, to pull the latest images, and to 
start Hay Say again:  

Linux:
```shell
sudo docker compose stop
sudo docker compose pull
sudo docker compose up
```
Windows and MacOS:
```zsh
docker compose stop
docker compose pull
docker compose up
```

### 3. (Optional) Remove "dangling" images to save disk space
When you pull an updated Docker image, the old image is not automatically deleted. The old image, which is no longer 
used, is referred to as a "dangling" image. You can remove dangling images to save space by executing the following 
command:

Linux:
```shell
sudo docker image prune
```

Windows and MacOS:
```zsh
docker image prune
```
Windows users must also follow the instructions in 
[Additional Required Steps for Windows Users](#additional-required-steps-for-windows-users) afterwards to finish freeing
disk space.

### Special Instructions for the Aug 19, 2023 update
Following the update on Aug 19, 2023, the "model pack" images have become obsolete and can be removed. Furthermore, 
every other image has been updated, so you can save some space by deleting all of your existing Hay Say Docker images 
first and then re-downloading them (doing so will prevent "dangling" images from taking up excessive space during the 
update). Lastly, Hay Say now expects the presence of a "models" docker volume, so you must create it. If you installed 
Hay Say before Aug 19, 2023, please execute these commands instead:

Linux:
```shell
sudo docker compose down --rmi all
wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
sudo docker volume create models
sudo docker compose up
```

MacOS:
```zsh
docker compose down --rmi all
curl --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker volume create models
docker compose up
```

Windows:
```
docker compose down --rmi all
```
Now follow the steps in [Additional Required Steps for Windows Users](#additional-required-steps-for-windows-users) to 
clear disk space. After that, open Docker Desktop again. Once it has loaded, execute the following commands:
```
curl.exe --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker volume create models
docker compose up
```

### Special Instructions for the Dec 11, 2023 update
Every Docker image in the Hay Say project was updated in the Dec 11 update, so you can save some space by deleting all 
of your existing Hay Say Docker images first and then re-downloading them (doing so will prevent "dangling" images from 
taking up excessive space during the update). If you last installed or updated Hay Say between Aug 19 and Dec 11, 2023, 
please execute these commands instead:

Linux:
```shell
sudo docker compose down --rmi all
wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
sudo docker compose up
```

MacOS:
```zsh
docker compose down --rmi all
curl --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker compose up
```

Windows:
```
docker compose down --rmi all
```
Now follow the steps in [Additional Required Steps for Windows Users](#additional-required-steps-for-windows-users) to 
clear disk space. After that, open Docker Desktop again. Once it has loaded, execute the following commands:
```
curl.exe --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker compose up
```

## Advanced Topics

### Using the Model Packs to Download Models in Bulk
Hay Say used to download character models via Docker by downloading special, data-only images called "model packs".
Model packs proved to be inefficient with disk space usage, so Hay Say was updated to allow users to download
individual characters directly from Mega, Google Drive, and Huggingface Hub instead. The existing models packs should 
still work, however, and are available as a fallback in case there is an issue with downloading models individually. 
Please note that model packs will be deprecated in the future.

You can configure Hay Say to download a model pack by "uncommenting" the relevant lines in the docker-compose.yaml file.
For example, to download the singing models for so-vits-svc 4.0, uncomment (remove the hashtag at the start of) the 
following lines:
```yaml
#so_vits_svc_3_model_pack_1:  
#  image: hydrusbeta/hay_say:so_vits_svc_3_model_pack_1  
#  volumes:  
#    - so_vits_svc_3_model_pack_1:/home/luna/hay_say/so_vits_svc_3_model_pack_1  
```
So that they look like this instead:
```yaml
so_vits_svc_3_model_pack_1:  
  image: hydrusbeta/hay_say:so_vits_svc_3_model_pack_1  
  volumes:  
    - so_vits_svc_3_model_pack_1:/home/luna/hay_say/so_vits_svc_3_model_pack_1  
```
Be sure to save the file, then restart Hay Say (type ctrl+c in Hay Say's terminal if it is running and then execute 
"docker compose up" again). 

Here is a table showing which characters are included in each model pack:

|          Model Pack Name          | Characters                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|:---------------------------------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| controllable_talknet_model_pack_0 | Apple Bloom, Applejack, Applejack (singing), Big McIntosh, Cadance, Celestia, Chrysalis, Cozy Glow, Discord, Fluttershy, Fluttershy (singing), Granny Smith, hifire, hifis, Luna, Maud Pie, Mayor Mare, Pinkie Pie, Pinkie Pie (singing), Rainbow Dash, Rainbow Dash (singing), Rarity, Rarity (singing), Scootaloo, Shining Armor, Spike, Starlight Glimmer, Sunset Shimmer, Sweetie Belle, Tirek, Trixie Lulamoon, Trixie Lulamoon (singing), Twilight Sparkle, Twilight Sparkle (singing), Twilight Sparkle (whispering), Zecora                                                                                                                                                                                                                    |
|    so_vits_svc_3_model_pack_0     | Apple Bloom, Applejack, Bon Bon, Discord, Fluttershy, Pinkie Pie, Rainbow Dash, Rarity, Scootaloo, Sweetie Belle, Trixie Lulamoon, Twilight Sparkle                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|    so_vits_svc_3_model_pack_1     | Applejack (singing), Cadance (singing), Celestia (singing), Luna (singing), Rarity (singing), Starlight Glimmer (singing), Twilight Sparkle (singing)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|    so_vits_svc_4_model_pack_0     | Apple Bloom, Applejack, Celestia, Chrysalis, Derpy Hooves, Discord, Fluttershy, Pinkie Pie, Rainbow Dash, Rarity, Saffron Masala, Shining Armor, Tree Hugger, Trixie Lulamoon, Trixie Lulamoon (singing), Twilight Sparkle                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|    so_vits_svc_4_model_pack_1     | Apple Bloom (singing), Apple Bloom (singing, PS1), Applejack (singing), Applejack (singing, PS1), Cadance (singing), Cadance (singing, PS1), Celestia (singing), Celestia (singing, alt), Celestia (singing, PS1), Fluttershy (singing), Fluttershy (singing, PS1), Luna (singing), Luna (singing, PS1), Pinkie Pie (singing), Pinkie Pie (singing, PS1), Rainbow Dash (singing), Rainbow Dash (singing, alt), Rainbow Dash (singing, PS1), Rarity (singing), Rarity (singing, PS1), Scootaloo (singing), Scootaloo (singing, alt), Scootaloo (singing, PS1), Starlight Glimmer (singing, evil), Starlight Glimmer (singing, good), Sweetie Belle (singing), Sweetie Belle (singing, PS1), Twilight Sparkle (singing), Twilight Sparkle (singing, PS1) |
|    so_vits_svc_4_model_pack_2     | Pinkie Pie (angry), Pinkie Pie (annoyed), Pinkie Pie (anxious), Pinkie Pie (fearful), Pinkie Pie (happy), Pinkie Pie (neutral), Pinkie Pie (nonverbal), Pinkie Pie (sad), Pinkie Pie (sad shouting), Pinkie Pie (shouting), Pinkie Pie (surprised), Pinkie Pie (tired), Pinkie Pie (whispering)                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|    so_vits_svc_5_model_pack_0     | Applejack (singing, mane6), Fluttershy (singing, mane6), Pinkie Pie (singing), Pinkie Pie (singing, mane6), Rainbow Dash (singing, mane6), Rarity (singing, mane6), Twilight Sparkle (singing, mane6)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|         rvc_model_pack_0          | Babs Seed, Big McIntosh, Braeburn, Bunni Bunni, Cozy Glow, Cream Heart, Derpy Hooves, Diamond Tiara, Doctor Whooves, Gallus, Octavia Melody, Thorax, Twilight Sparkle (singing), Vinyl Scratch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|         rvc_model_pack_1          | Applejack, Applejack (alt), Fluttershy, Fluttershy (alt), Pinkie Pie, Pinkie Pie (alt), Rainbow Dash (alt), Rarity (alt), Twilight Sparkle (alt)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

### Loading Custom Models
If you have acquired or trained a model that is not included with Hay Say, you can add it to Hay Say by copying it to 
the relevant characters folder inside the main docker container:  
/home/luna/hay_say/models/[architecture]/characters/  
where [architecture] is one of: controllable_talknet, rvc, so_vits_svc_3, so_vits_svc_4, or so_vits_svc_5 
1. First, make sure Hay Say is running. 
2. Execute the following command in a terminal or Command Prompt. It will display information about all of the running 
Docker containers:
    ```shell
    docker container ls
    ```
    Note: You may need to expand the command window to properly display the output, which is arranged like a wide table. You
    should see a column titled "IMAGE" in the output. Look for the entry "hydrusbeta/hay_say:hay_say_ui" and find the 
    corresponding container name under the "NAMES" column. You will need that name in a moment:
    ![Screenshots showing one possible output of "docker container ls"](documentation%20images/main%20container%20name.png)
    The name you see might be a little different. For example, another name I have seen on someone else's machine was 
    "hay_say_ui-hay_say_ui-1".
3. Arrange and rename your files to match the expected format:  
![Screenshots showing the expected file structures for each architecture's models](documentation%20images/CustomModelFileOrganization.png)  
Additional restrictions: 
   * Only a single speaker is supported per character folder. 
     * If your custom model is a so-vits-svc 5 model, you may only have a single .spk.npy file within the "singer" 
     directory.
     * If your custom model is a _multi-speaker_ so-vits-svc 4 model (i.e. the config.json file has multiple speakers 
       listed under "spk" at the bottom of the file), then you must add a speaker.json file which specifies which 
       speaker to use. The contents of the file should look like this:
       ```json
       {
          "speaker": "<name of speaker>"
       }
       ```
       where `<name of speaker>` should match one of the strings under "spk" in the config.json file.
4. Next, copy the folder containing your custom model into the desired architecture folder using the `docker cp` 
   command. For example, if you have a folder named "Rainbowshine_Custom" on your desktop containing a so-vits-svc 4.0 
   model, you can copy it by executing the following on Linux or MacOS:
    ```shell
    docker cp ~/Desktop/Rainbowshine_Custom/. hydrusbeta-hay_say_ui-1:/home/luna/hay_say/models/so_vits_svc_4/characters/RainbowShine_Custom
    ```
    or the following command on Windows:
    ```
    docker cp %HOMEDRIVE%%HOMEPATH%/Desktop/Rainbowshine_Custom/. hydrusbeta-hay_say_ui-1:/home/luna/hay_say/models/so_vits_svc_4/characters/RainbowShine_Custom
    ```
    * Note: The dot at the end of "~/Desktop/Rainbowshine_Custom/." is not a typo, so don't leave it out. It instructs 
    Docker to copy all the contents of the Rainbowshine_Custom folder.  
    * Note: I recommend that you name the folder with "_Custom" appended to the end as I have done in this example. 
    That will avoid a name clash in case the character becomes available for download in the future.  
5. Finally, restart Hay Say (type ctrl+c in Hay Say's terminal and then execute "docker compose up" again)


### Enabling GPU Integration
GPU integration is turned off by default in Hay Say. This is to prevent an error for users who do not have a 
Cuda-capable GPU. If you do have a Cuda-capable GPU on a Windows or Linux machine, you can enable GPU integration:
1. Install the NVIDIA Container Toolkit
   * On Linux, follow the instructions at https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html. Note: Unless you know you are using CRI-O or Podman, you do not need to follow the instructions under "Configuring CRI-O" or "Configuring Podman".
   * On Windows, make sure you are using a recent NVIDIA driver and then follow the instructions under the section "CUDA Support for WSL 2" at https://docs.nvidia.com/cuda/wsl-user-guide/index.html#cuda-support-for-wsl-2
   * On MacOS, as far as I can tell, Cuda GPU integration is no longer supported. See https://developer.nvidia.com/nvidia-cuda-toolkit-11_6_0-developer-tools-mac-hosts  
2. Edit the docker-compose.yaml 
file. There are several places (one under each architecture) where you will see the following lines:
    ```yaml
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]
    ```
    To enable GPU for that architecture, uncomment those lines. i.e. remove the hashtags so that they look like this instead:
    ```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    ```
3. For Linux users only, if you are running Docker in rootless mode on Linux (i.e. so you can run `docker compose up` 
instead of `sudo docker compose up`), then you will need to follow additional steps to work around a permissions issue. 
See https://stackoverflow.com/questions/74554143.


### Reducing Disk Space usage
There are a couple of ways you can reduce the disk usage of Hay Say. 

Important! Windows users must complete additional steps to free disk space after following any of these methods. See 
[Additional Required Steps for Windows Users](#additional-required-steps-for-windows-users).

#### Method 1: Deleting characters
Launch Hay Say and click on the "Manage Models" button at the top of the screen.
![Screenshot of Hay Say showing the "Manage Models" button in the toolbar](documentation%20images/ManageModelsInToolbar.png)

This will open a screen where you can delete characters.

#### Method 2: Deleting architectures
By default, Hay Say downloads all supported AI architectures. This currently includes Controllable TalkNet, so-vits-svc 
3.0, so-vits-svc 4.0, so-vits-svc 5.0, and Retrieval-based Voice Conversion (RVC). Each of those take about 10GB. If you
want to reclaim some disk space by deleting undesired architectures, you must first disable the architecture so that Hay
Say does not automatically re-download it. Open the docker-compose.yaml file and look for sections named like 
architectureName_server. For example, here is the section that defines the so-vits-svc 3.0 server:
```yaml
  # This container provides a web service interface to so-vits-svc 3.0.
  so_vits_svc_3_server:
    depends_on:
      - redis
    image: hydrusbeta/hay_say:so_vits_svc_3_server
    working_dir: /home/luna/hay_say/so_vits_svc_3
    volumes:
      - so_vits_svc_3_model_pack_0:/home/luna/hay_say/so_vits_svc_3_model_pack_0
      - so_vits_svc_3_model_pack_1:/home/luna/hay_say/so_vits_svc_3_model_pack_1
      - models:/home/luna/hay_say/models
      - audio_cache:/home/luna/hay_say/audio_cache
    # GPU integration is disabled by default to prevent an error on machines that do not have a Cuda-capable GPU.
    # Uncomment the lines below to enable it for so-vits-svc 3.0 if you wish.
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]
```
You can disable so-vits-svc 3.0 by commenting out this section, i.e., add hashtags at the beginnings of the lines to 
make it look like this: 
```yaml
  # This container provides a web service interface to so-vits-svc 3.0.
  # so_vits_svc_3_server:
    # depends_on:
    #   - redis
    # image: hydrusbeta/hay_say:so_vits_svc_3_server
    # working_dir: /home/luna/hay_say/so_vits_svc_3
    # volumes:
    #   - so_vits_svc_3_model_pack_0:/home/luna/hay_say/so_vits_svc_3_model_pack_0
    #   - so_vits_svc_3_model_pack_1:/home/luna/hay_say/so_vits_svc_3_model_pack_1
    #   - models:/home/luna/hay_say/models
    #   - audio_cache:/home/luna/hay_say/audio_cache
    # GPU integration is disabled by default to prevent an error on machines that do not have a Cuda-capable GPU.
    # Uncomment the lines below to enable it for so-vits-svc 3.0 if you wish.
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]
```
Next, delete both the Docker container and Docker image for so-vits-svc 3.0 to free disk space. Open a command prompt or 
terminal and execute the following command to list all containers:
```shell
docker container ls -a
```
The output should be similar to the following:
```shell
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED       STATUS                              PORTS     NAMES
4d3098ae4c2f   hydrusbeta/hay_say:so_vits_svc_3_server                "/bin/sh -c '/home/l…"   9 days ago    Exited (137) 9 days ago                       hay_say-so_vits_svc_3_server-1
0c6c9eac8573   hydrusbeta/hay_say:so_vits_svc_5_server                "/bin/sh -c '/home/l…"   9 days ago    Exited (137) 9 days ago                       hay_say-so_vits_svc_5_server-1
7defd670649c   hydrusbeta/hay_say:controllable_talknet_server         "/bin/sh -c '/home/l…"   9 days ago    Exited (137) 9 days ago                       hay_say-controllable_talknet_server-1
9b85ad39fea9   hydrusbeta/hay_say:so_vits_svc_4_server                "/bin/sh -c '/home/l…"   9 days ago    Exited (137) 9 days ago                       hay_say-so_vits_svc_4_server-1
48bc80452718   hydrusbeta/hay_say:rvc_server                          "/bin/sh -c '/home/l…"   9 days ago    Exited (137) 9 days ago                       hay_say-rvc_server-1
d0343f8f00d4   hydrusbeta/hay_say:hay_say_ui                          "/bin/sh -c 'python …"   9 days ago    Exited (137) 9 days ago                       hay_say-hay_say_ui-1
d82816c5889a   redis                                                  "docker-entrypoint.s…"   9 days ago    Exited (0) 9 days ago                         hay_say-redis-1
c26692c3240b   hydrusbeta/hay_say:so_vits_svc_4_model_pack_1          "/bin/sh"                9 days ago    Exited (0) 9 days ago                         hay_say-so_vits_svc_4_model_pack_1-1
e49ad2b1ff83   hydrusbeta/hay_say:so_vits_svc_3_model_pack_1          "/bin/sh"                9 days ago    Exited (0) 9 days ago                         hay_say-so_vits_svc_3_model_pack_1-1
35913b4b7f7e   hydrusbeta/hay_say:so_vits_svc_4_model_pack_2          "/bin/sh"                9 days ago    Exited (0) 9 days ago                         hay_say-so_vits_svc_4_model_pack_2-1
fd2f36c568e3   hydrusbeta/hay_say:so_vits_svc_3_model_pack_0          "/bin/sh"                11 days ago   Exited (0) 9 days ago                         hay_say-so_vits_svc_3_model_pack_0-1
feb9c22c9d1b   hydrusbeta/hay_say:controllable_talknet_model_pack_0   "/bin/sh"                11 days ago   Exited (0) 9 days ago                         hay_say-controllable_talknet_model_pack_0-1
d3c8114e4639   hydrusbeta/hay_say:so_vits_svc_5_model_pack_0          "/bin/sh"                11 days ago   Exited (0) 9 days ago                         hay_say-so_vits_svc_5_model_pack_0-1
3830263165be   hydrusbeta/hay_say:so_vits_svc_4_model_pack_0          "/bin/sh"                11 days ago   Exited (0) 9 days ago                         hay_say-so_vits_svc_4_model_pack_0-1
9c5f0eb3478a   hydrusbeta/hay_say:rvc_model_pack_0                    "/bin/sh"                11 days ago   Exited (0) 9 days ago                         hay_say-rvc_model_pack_0-1
d4824c05694a   hydrusbeta/hay_say:rvc_model_pack_1                    "/bin/sh"                11 days ago   Exited (0) 9 days ago                         hay_say-rvc_model_pack_1-1
```
In the NAMES column, look for the name of the architecture you want to delete, followed by "_server". In this case, we 
have hay_say-**so_vits_svc_3_server**-1. Delete that container by executing the following command:
```shell
docker container rm <name of the container you want to delete>
```
In this case,
```shell
docker container rm hay_say-so_vits_svc_3_server-1
```

Next, execute the following command to list all Docker images:
```shell
docker image ls
```
The output should be similar to the following:
```shell
REPOSITORY               TAG                                 IMAGE ID       CREATED        SIZE
redis                    latest                              8e69fcb59ff4   5 weeks ago    130MB
hydrusbeta/hay_say       hay_say_ui                          381f9d276433   6 weeks ago    1.47GB
hydrusbeta/hay_say       rvc_server                          a619e2e6e6ee   6 weeks ago    11.1GB
hydrusbeta/hay_say       rvc_model_pack_0                    032a923041bf   6 weeks ago    1.34GB
hydrusbeta/hay_say       so_vits_svc_5_server                2b15ea8db246   8 weeks ago    10GB
hydrusbeta/hay_say       so_vits_svc_5_model_pack_0          65410b0d89b7   8 weeks ago    1.11GB
hydrusbeta/hay_say       controllable_talknet_server         65bfaae29689   2 months ago   8.13GB
hydrusbeta/hay_say       so_vits_svc_4_server                4bae6175c9d4   2 months ago   6.89GB
hydrusbeta/hay_say       so_vits_svc_3_server                e3224b5a2c79   2 months ago   6.12GB
hydrusbeta/hay_say       so_vits_svc_4_model_pack_0          8f73a6838a1d   2 months ago   8.33GB
hydrusbeta/hay_say       so_vits_svc_3_model_pack_0          8c92571c4566   2 months ago   8.4GB
hydrusbeta/hay_say       controllable_talknet_model_pack_0   972e53accb49   3 months ago   3.96GB
```
Look for the desired architecture name in the "TAG" column and then delete the desired architecture by executing the 
following 
command:
```shell
docker image rm hydrusbeta/hay_say:<tag of image you would like to delete>
```
So, for so-vits-svc 3.0 for example, that would be:
```shell
docker image rm hydrusbeta/hay_say:so_vits_svc_3_server
```

Optional Step: You can hide the architecture in the UI by editing the docker-compose.yaml file. Look for the following
lines:
```yaml
command: ["/bin/sh", "-c", "
          celery --workdir ~/hay_say/hay_say_ui/ -A celery_download:celery_app worker --loglevel=INFO --concurrency 5 --include_architecture ControllableTalkNet --include_architecture SoVitsSvc3 --include_architecture SoVitsSvc4 --include_architecture SoVitsSvc5 --include_architecture Rvc & 
          celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_gpu:celery_app worker --loglevel=INFO --concurrency 1 --cache_implementation file --include_architecture ControllableTalkNet --include_architecture SoVitsSvc3 --include_architecture SoVitsSvc4 --include_architecture SoVitsSvc5 --include_architecture Rvc &
          celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_cpu:celery_app worker --loglevel=INFO --concurrency 1 --cache_implementation file --include_architecture ControllableTalkNet --include_architecture SoVitsSvc3 --include_architecture SoVitsSvc4 --include_architecture SoVitsSvc5 --include_architecture Rvc &
          gunicorn --config=server_initialization.py --workers 1 --bind 0.0.0.0:6573 'wsgi:get_server(enable_model_management=True, update_model_lists_on_startup=True, enable_session_caches=False, migrate_models=True, cache_implementation=\"file\", architectures=[\"ControllableTalkNet\", \"SoVitsSvc3\", \"SoVitsSvc4\", \"SoVitsSvc5\", \"Rvc\"])'
          "]
```
The architecture's name will appear four times. Delete `"--include_architecture <architectureName>"` on the 2nd, 3rd,
and 4th lines and also delete the architecture name after the `"--architectures"` flag on the 5th line. For example, 
here's the result after removing so-vits-svc 3.0:
```yaml
command: ["/bin/sh", "-c", "
          celery --workdir ~/hay_say/hay_say_ui/ -A celery_download:celery_app worker --loglevel=INFO --concurrency 5 --include_architecture ControllableTalkNet --include_architecture SoVitsSvc4 --include_architecture SoVitsSvc5 --include_architecture Rvc & 
          celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_gpu:celery_app worker --loglevel=INFO --concurrency 1 --cache_implementation file --include_architecture ControllableTalkNet --include_architecture SoVitsSvc4 --include_architecture SoVitsSvc5 --include_architecture Rvc &
          celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_cpu:celery_app worker --loglevel=INFO --concurrency 1 --cache_implementation file --include_architecture ControllableTalkNet --include_architecture SoVitsSvc4 --include_architecture SoVitsSvc5 --include_architecture Rvc &
          gunicorn --config=server_initialization.py --workers 1 --bind 0.0.0.0:6573 'wsgi:get_server(enable_model_management=True, update_model_lists_on_startup=True, enable_session_caches=False, migrate_models=True, cache_implementation=\"file\", architectures=[\"ControllableTalkNet\", \"SoVitsSvc4\", \"SoVitsSvc5\", \"Rvc\"])'
          "]
```

#### Additional Required Steps for Windows Users

Windows users must complete additional steps to free disk space after deleting characters or images. You have a couple 
of options:

###### Option 1: Shrink the WSL2 virtual disk manually

1. Locate the ext.vhdx file on your system. It is typically under 
C:\\Users\\<your_username>\AppData\Local\Docker\wsl\data
2. Shut down Hay Say (type CTRL+c into the Command Prompt window that you started Hay Say from).
3. Stop the Docker Engine by right-clicking on the whale icon in the taskbar and selecting "Quit Docker 
Desktop". Wait until the whale icon disappears.
4. Open a command prompt and execute the following commands:  
    ```
    wsl --shutdown
    diskpart
    ```
5. That will open a new command prompt window. In that one, execute the following:
    ```
    select vdisk file="C:\\path\\to\\your\\vhdx\\file.vhdx"
    attach vdisk readonly
    compact vdisk
    detach vdisk
    exit
    ```

If you are running Windows 10 _Pro_, you can use just these two commands instead of all the ones in steps 4 and 
5:
   ```
   wsl --shutdown
   optimize-vhd -Path "C:\\path\\to\\your\\vhdx\\file.vhdx" -Mode full
   ```

###### Option 2: Shrink the WSL2 virtual disk using wslcompact

If you have a drive with enough free space to save a copy of the vhdi file, another options is to use wslcompact. 
wslcompact saves a copy of the vhdi file first, operates on the copy, and then overwrites the original vhdi file if the 
operation is successful

1. Install [wslcompact](https://github.com/okibcn/wslcompact). Below are instructions on how to install it as a Scoop 
app.
   1. Open a PowerShell window and execute the following to install wslcompact as a Scoop app:
       ```shell
       irm get.scoop.sh | iex
       scoop bucket add .oki https://github.com/okibcn/Bucket
       scoop install wslcompact
       ```
2. If your primary drive does not have enough space to save a copy of the vhdi file, set the "TEMP" environment 
variable to a folder on a drive with enough space. For example, if you have space on drive letter Z:
    ```shell
   $env:TEMP="Z:/specify/a/folder/on/the/drive" 
   ```
3. Shut down Hay Say (type CTRL+c into the Command Prompt window that you started Hay Say from).
4. Stop the Docker Engine by right-clicking on the whale icon in the taskbar and selecting "Quit Docker 
Desktop". Wait until the whale icon disappears.
5. Open a command prompt and execute:
    ```
    wslcompact -c -d docker-desktop-data
    ```
It is possible that your WSL distro name is different. If the command in step 5 does not work, then execute the 
following to list all distro names:
```shell
wslcompact -l
```
and search for a distro name with the word "docker" or "ubuntu" in it.

###### Explanation: 
Hay Say runs on the Docker Engine. On Windows, Docker typically runs on a virtualization platform called 
"Windows Subsystem for Linux, version 2", or WSL2, which stores all of its data on a virtual hard disk (a .vhdx 
file). The vhdx file will automatically grow in size as data is added to it (e.g. when you download a new model 
in Hay Say), but it will not automatically shrink when you delete files. To reclaim unused disk space from WSL2, 
you need to manually shrink the .vhdx file. There is an open feature request for Microsoft to make WSL 
automatically release disk space, which is discussed here:  
https://github.com/microsoft/WSL/issues/4699  

Linux and MacOS users are unaffected by this issue and should see an immediate increase in disk space after deleting
models or architectures. 

## The Technical Design of Hay Say

The user interface code for Hay Say runs in its own Docker container, hay_say_ui, and the UI is accessed by the user via
a web browser. Each AI architecture (e.g. so-vits-svc or ControllableTalkNet) is installed in its own container and a 
simple Flask web server runs in each one, listening for connections. Each Flask web server defines a /generate method 
which invokes the AI architecture to generate an audio file.

![diagram of Hay Say's networking setup, showing that the main UI container communicates with the AI Architecture containers by sharing files and by using webservice calls to trigger audio generation](documentation%20images/design%20diagram.png)

After the user enters their desired options and presses the "Generate!" button, hay_say_ui first preprocesses the audio 
and saves the result to a mounted volume, audio_cache. It then makes a web service call to the container with the 
desired AI architecture, instructing it to generate audio. That container reads the preprocessed audio from audio_cache, 
generates a pony voice from it, and saves it back to audio_cache. The hay_say_ui container then reads the generated 
audio, performs any postprocessing, and presents the result to the user via an HTML audio element. 

Hence, there are 2 mechanisms of communication between the docker containers: calling web services and passing files 
over a shared volume.

Weights for the neural networks are stored in Docker volumes that are named like "controllable_talknet_model_pack_0" or 
"so_vits_svc_4_model_pack_1". Within each volume is a collection of folders, one for each pony character. Each character
folder contains files with the model weights for that character. The volumes are initially populated by pulling a Docker
image containing models for many characters and mounting the corresponding model_pack volume to that image, which 
automatically copies all the models from the image to the volume.

Hay say also has an "audio_cache" volume for maintaining a small cache of audio files. Any time the user uploads an 
audio file to Hay Say, the file is saved to audio_cache/raw. When a file is preprocessed, the result is saved to 
audio_cache/preprocessed. When an audio file is generated, the result is saved to audio_cache/output and, finally, when
an output audio is postprocessed, the result is saved in audio_cache/postprocessed. Up to 25 files can be stored in each
subfolder before Hay Say begins to automatically delete the oldest files. The purpose of the caching system is twofold.
First, by storing the file at various stages of production, Hay Say will be able to present a playback button at each
stage, so users can compare the "before" and "after" of a particular step. For example, the user can play back the raw
audio and also play back the preprocessed audio to compare them. Second, some operations take a lot of computational
power to complete, such as generating output from one of the AI architectures. By caching that output, Hay Say can allow
the user to tweak the post-processing options and listen to the results over and over without needing to invoke the AI 
architecture each time. 

The code for the main UI is in this repository. Code for the Flask servers for the other containers can be found in 
various other code repositories on hydrusbeta's account. See https://github.com/hydrusbeta?tab=repositories.

## "Roadmap"

Here are some tasks I consider important. I intend to work on them "soon", in no particular order:
1. Add some preprocessing and postprocessing options.
2. I forsee a need for a "Hay Say launcher" that lets the user select which architectures they want to install. That 
   way, the user doesn't have to download *everything* if all they want is, say, the TTS solutions like controllable 
   talknet. This also gives the user some control over memory usage on a resource-constrained machine, and would be a 
   good place for downloading updates and running the WSL cleanup operation on Windows. Ideally, the user would never 
   need to open a command prompt or terminal again.
3. Add another text-to-speech option. A few possibilities include:
    * BarkAI
    * tacotron
    * tortoise TTS
4. Hay Say runs terribly on Apple Silicon. I'd like to see whether performance can be improved by re-building the images 
   using a MacOS-native base image and installing ARM-specific python packages. 
5. Write up more documentation on the technical details of Hay Say and tutorials for developers on: adding a new 
   architecture, adding a model pack, and adding pre/postprocessing options.
6. Currently, the "Generate!" button becomes disabled if a required input has not been provided yet. This might be 
   confusing for users. Instead, let them hit the "Generate!" button and then highlight the missing, required fields in 
   red, along with a useful error message.
7. Every time a user clicks the "Generate!" button, the selected architecture is loaded from scratch, executed, and then
   shut down. Performance could be vastly improved by keeping architectures loaded between generation tasks. This kind
   of performance improvement should be implemented carefully, as loading too many architectures at the same time could
   overload a user's memory (either in RAM or in GPU memory).

Plus, there are numerous minor code improvement opportunities that I have marked with "todo" throughout the codebase.


## Testing Data / Benchmarks

Hay Say will run on most machines but will be very slow on older hardware. Here are the results of some tests I ran on 
various computers I could get my hooves on. Hopefully it will help inform you how fast or slow you can expect Hay Say 
to run on your machine. They are ordered here from best-performing machines to worst.

If it looks like your machine will perform poorly with Hay Say, an alternative for generating pony voices would be to 
try out one of the many online Google Colab UI projects listed throughout the following document, which run on Google's 
servers instead of your local machine:  
https://docs.google.com/document/d/1y1pfS0LCrwbbvxdn3ZksH25BKaf0LaO13uYppxIQnac/edit    
Note: At the time of this writing, Hay Say is not affiliated with any of the Google Colab projects, and Hay Say itself 
is not available in Google Colab.

I discovered during testing that, unfortunately, loading an audio file into Hay Say can take a significant amount of 
time on some machines. I have recorded those times here as well. In this case, I was uploading a short (<3-second) 
audio recording to use as an audio input.

The tests were performed manually, and times were taken with a stopwatch. Each AI architecture was invoked 2-3 times to
generate a pony saying "Testing, testing 1 2 3!" and then the times were averaged. In each case, GPU integration was 
disabled, so the CPU was used exclusively.

Note: Generating Audio with any architecture was noticeably slower for the first audio output and faster on subsequent 
generations, even with a different character selected.

| Machine Name          | Age of Computer (years) as of May 2023 |       CPU        |       RAM        | Loading time for a short audio recording (s) | Controllable TalkNet Generation time (s) | so-vits-svc 3.0 Generation time (s) | so-vits-svc 4.0 Generation time (s) |
|-----------------------|:--------------------------------------:|:----------------:|:----------------:|:--------------------------------------------:|:----------------------------------------:|:-----------------------------------:|:-----------------------------------:|
| Custom Built Tower    |                  0.5                   |   13th gen i9    | 32 GB (6000 MHz) |                      0                       |                    8                     |                  5                  |                  6                  |
| Aspire TC-895         |                   2                    |   10th gen i5    | 12 GB (2600 MHz) |                      3                       |                   26.5                   |                30.5                 |                27.5                 |
| Dell XPS 13 9380      |                   4                    |    8th gen i7    | 16 GB (1200 MHz) |                      1                       |                    44                    |                 38                  |                 41                  |
| Toshiba Qosmio laptop |                   10                   |    4th gen i7    | 16 GB (1600 MHz) |                      10                      |                   198                    |                 174                 |                 227                 |
| Mac Mini              |                   0                    | M2 Apple Silicon |       8 GB       |                      27                      |                 N/A [1]                  |                 589                 |                 575                 |  

[1] Test failed with an error. Unable to generate audio.

	

