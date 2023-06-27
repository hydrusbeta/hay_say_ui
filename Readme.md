# Hay Say, A Unified Interface for Pony Voice Generation
## What is Hay Say?

Hay Say is a user interface for generating pony voices. From a single UI, you can generate voices from AI architectures, such as so-vits-svc (https://github.com/svc-develop-team/so-vits-svc) and Controllable TalkNet (https://github.com/SortAnon/ControllableTalkNet). At the moment, all supported AI architectures can run locally and do not require an internet connection.

## The Motivation Behind Hay Say

Over the past few years, many AI architectures have emerged for accomplishing text-to-speech (TTS) generation and voice modification ("speech-to-speech"). Many of these new technologies did not have a graphical user interface when they first became available. Each time a new technology has entered into the awareness of the Pony Preservation Project thread at /mlp on 4chan, someone has had to develop a new UI to make the technology accessible to others. This has lead to a collection of user interfaces over time, each one unique to a particular AI architecture and with features that are not available in the other UIs. The primary motivation behind Hay Say is to create a unified user experience for all the voice generation solutions. Preprocessing and postprocessing options are separated from architecture-specific options so that every architecture can benefit from new pre- or post-processing features. With a UI framework already in place, it should be possible to give new architectures a usable UI more quickly by integrating them with Hay Say.

A secondary motivation behind Hay Say is to reduce user frustration with installing software. Falling into Python's "dependency hell" seems to be a common pain point when users try to install voice generation software locally. Hay Say addresses this issue by pre-installing all the AI solutions into their own Docker images. Users simply need to install Docker and pull the pre-built images.

## Installation Instructions

Important: Be aware that Hay Say will need to download at least 41 GB of compressed Docker images, so expect it to take a while to start up the first time you run it. It should come up quickly after that. The exact amount of time required for the initial startup depends, of course, on your internet speed. 

Before you install Hay Say, I recommend you take a look at the Testing Data / Benchmarks section at the bottom of this page to get a ballpark figure on how fast or slow Hay Say might be on your machine.

### Required Hardware
* At least 100 GB free Hard drive space 
* 12 GB System RAM (Hay Say only uses up to ~8 GB RAM, but don't forget that your OS needs RAM too)

### Recommended Hardware and Software
* A fast CPU - or - an Nvidia GPU with a Cuda compute capability of 3.5 or higher.
* Hay Say was tested and worked well on the following Operating Systems. It may or may not work on other operating systems.:
  * Windows 10
  * Windows 11
  * Ubuntu 22.10
  * Ubuntu 23.04

#### A Note on MacOS
I also tested Hay Say on MacOS 13.3.1 (Ventura) with Apple Silicon M2. I was unable to generate audio with Controllable TalkNet, and so-vits-svc (3.0 and 4.0) was unusably slow even though the machine was brand new (see Testing Data / Benchmarks section). I do not recommend running Hay Say on Apple Silicon. It is unknown whether it works any better on Macs with Intel chips.

### Windows Installation Instructions

1. Install Docker Desktop:  
	https://www.docker.com/
2. Start Docker Desktop and wait until it has finished loading.
	If you get a popup window stating "Docker Desktop requires a newer WSL kernel version", open a command prompt, execute the following command, and then start docker desktop again:
	`wsl --update`
3. Open a command prompt and execute the following commands:
```
curl.exe --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker volume create custom_models
docker volume create audio_cache
docker compose up
```

Note: You might get a Windows Defender Firewall popup. You can safely close that window. No special firewall rules are required to run Hay Say.

Hay Say will take time to download the large Docker images (~41 GB). Once it is done, you should see output like the following:
![](documentation%20images/Windows%20ready%20to%20roll.png)

Open a web browser and go to the following URL:  
http://127.0.0.1:6573/

#### Stopping Hay Say
To stop Hay Say, go to the Command Prompt that you ran "docker compose up" in earlier and type CTRL+C. It will take 10-30 seconds for Docker to gracefully shut down all of the containers.
I also recommend shutting down Docker Desktop. Right click on the Whale icon in the taskbar and select "Quit Docker Desktop".

#### Starting Hay Say Again 
To start Hay Say again, first make sure that the Docker Engine is running. You can check for Docker Engine in the taskbar:  
![image showing the Docker whale icon in a Windows Taskbar](documentation%20images/windows%20docker%20icon.png)  
If it is not running, you can start it by launching Docker Desktop. 
Then, open Command Prompt and type the following command:
```
docker compose up
```
Note: you must be in the folder where docker-compose.yaml is located (you downloaded it earlier in step 3 above) when you execute that command. cd to that directory first if necessary.


### Linux Installation Instructions

1. Install Docker Engine. This can be done in several ways according to preference. See https://docs.docker.com/engine/install/ubuntu. I recommend following the instructions under the section "Install using the apt repository".
Note: Docker usually needs to be run as a superuser. However, it is possible to install it in a way that lets you run it in rootless mode (see https://docs.docker.com/engine/security/rootless). Hay Say has not been tested in a rootless configuration.

2. Open a terminal and execute the following commands:
```
wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
sudo docker volume create custom_models
sudo docker volume create audio_cache
sudo docker compose up
```

Hay Say will take time to download the large Docker images (~41 GB). Once it is done, you should see output like the following:  
![](documentation%20images/Linux%20ready%20to%20roll.png)

Open a web browser and go to the following URL:  
http://127.0.0.1:6573/

#### Stopping Hay Say
To stop Hay Say, go to the terminal where you ran "docker compose up" earlier and type CTRL+C. It will take 10-30 seconds for Docker to gracefully shut down all of the containers.

#### Starting Hay Say Again 
To start Hay Say again, open a terminal and type the following command:
```
sudo docker compose up
```
Note: you must be in the folder where docker-compose.yaml is located (you downloaded it earlier in step 2 above) when you execute that command. cd to that directory first if necessary.



### MacOS Installation Instructions

Important! Hay Say did not run well on Apple Silicon during my testing. See "A Note on MacOS" in the Recommended Hardware and Software section, above. But here are the steps in case you want to give it a try anyways.

1. Install Docker Desktop (note: if you are running MacOS on Apple Silicon (e.g. M1 or M2), make sure you download the version for Apple Silicon):  
	https://www.docker.com/
2. Start Docker Desktop and wait until it has finished loading.
3. Open a terminal and execute the following commands:
```
curl --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
docker volume create custom_models
docker volume create audio_cache
docker compose up
```

Hay Say will take time to download the large Docker images (~41 GB). Once it is done, you should see output like the following:
![](documentation%20images/macOS%20ready%20to%20roll.png)

Open a web browser and go to the following URL:  
http://127.0.0.1:6573/

#### Stopping Hay Say
To stop Hay Say, go to the Terminal where you ran "docker compose up" earlier and type CTRL+C. It will take 10-30 seconds for Docker to gracefully shut down all of the containers.
I also recommend shutting down Docker Desktop. Right click on the Whale icon in the taskbar and select "Quit Docker Desktop".


#### Starting Hay Say Again 
To start Hay Say again, first make sure that the Docker Engine is running. You can check for Docker Engine in the taskbar:
![image showing the Docker whale icon in a MacOS Taskbar](documentation%20images/macOS%20docker%20icon.png)  
If it is not running, you can start it by launching Docker Desktop
Then open a terminal and type the following command
```
sudo docker compose up
```
Note: you must be in the folder where docker-compose.yaml is located (you downloaded it earlier in step 3 above) when you execute that command. cd to that directory first if necessary.

## Updating Hay Say

### 1. Grab the latest docker-compose file 
To update Hay Say, it is recommended that you first download the latest docker-compose file in case new entries have 
been added (which will happen when new architecture and model packs have been added to Hay Say). To download the latest 
docker-compose file, execute the following command. Please note that it will overwrite your existing docker-compose 
file. If you made any edits to your old docker-compose file (e.g. to make it download only specific architectures), 
you will need to make the same edits to the new file:

Linux:
```
wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml  
```
Windows:
```
curl.exe --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
```
MacOS:
```
curl --output docker-compose.yaml https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/docker-compose.yaml
```
### 2. Pull the latest images
Next, execute the following commands to make sure that your containers are stopped, to pull the latest images, and to 
start Hay Say again:  

Linux:
```
sudo docker compose stop
sudo docker compose pull
sudo docker compose up
```
Windows and MacOS:
```
docker compose stop
docker compose pull
docker compose up
```




## Advanced Topics

### Downloading Additional Character Models
Character models are organized into "model packs". Hay Say only downloads some of these model packs by default. You can 
configure Hay Say to download additional model packs by editing the docker-compose.yaml file. You will need to 
"uncomment" the relevant lines. 

For example, singing models for so-vits-svc 3.0 and 4.0 are not downloaded by default. To download the so-vits-svc 3.0 
singing models, uncomment (remove the hashtag at the start of) the following lines:
```
#so_vits_svc_3_model_pack_1:  
#  image: hydrusbeta/hay_say:so_vits_svc_3_model_pack_1  
#  volumes:  
#    - so_vits_svc_3_model_pack_1:/root/hay_say/so_vits_svc_3_model_pack_1  
```
To download the so-vits-svc 4.0 singing models, uncomment (remove the hashtag at the start of) the following lines:
```
#so_vits_svc_4_model_pack_1:
#  image: hydrusbeta/hay_say:so_vits_svc_4_model_pack_1
#  volumes:
#    - so_vits_svc_4_model_pack_1:/root/hay_say/so_vits_svc_4_model_pack_1
```
Be sure to save the file, then restart Hay Say (type ctrl+c in Hay Say's terminal if it is running and then execute "docker compose up" again)

|          Model Pack Name          | Included in Default docker-compose.yaml | Characters                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|:---------------------------------:|:---------------------------------------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| controllable_talknet_model_pack_0 |           :heavy_check_mark:            | Apple Bloom, Applejack, Applejack (singing), Big McIntosh, Cadance, Celestia, Chrysalis, Cozy Glow, Discord, Fluttershy, Fluttershy (singing), Granny Smith, hifire, hifis, Luna, Maud Pie, Mayor Mare, Pinkie Pie, Pinkie Pie (singing), Rainbow Dash, Rainbow Dash (singing), Rarity, Rarity (singing), Scootaloo, Shining Armor, Spike, Starlight Glimmer, Sunset Shimmer, Sweetie Belle, Tirek, Trixie Lulamoon, Trixie Lulamoon (singing), Twilight Sparkle, Twilight Sparkle (singing), Twilight Sparkle (whispering), Zecora                                                                                                                                                                                                                    |
|    so_vits_svc_3_model_pack_0     |           :heavy_check_mark:            | Apple Bloom, Applejack, Bon Bon, Discord, Fluttershy, Pinkie Pie, Rainbow Dash, Rarity, Scootaloo, Sweetie Belle, Trixie Lulamoon, Twilight Sparkle                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|    so_vits_svc_3_model_pack_1     |                   :x:                   | Applejack (singing), Cadance (singing), Celestia (singing), Luna (singing), Rarity (singing), Starlight Glimmer (singing), Twilight Sparkle (singing)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|    so_vits_svc_4_model_pack_0     |           :heavy_check_mark:            | Apple Bloom, Applejack, Celestia, Chrysalis, Derpy Hooves, Discord, Fluttershy, Pinkie Pie, Rainbow Dash, Rarity, Saffron Masala, Shining Armor, Tree Hugger, Trixie Lulamoon, Trixie Lulamoon (singing), Twilight Sparkle                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|    so_vits_svc_4_model_pack_1     |                   :x:                   | Apple Bloom (singing), Apple Bloom (singing, PS1), Applejack (singing), Applejack (singing, PS1), Cadance (singing), Cadance (singing, PS1), Celestia (singing), Celestia (singing, alt), Celestia (singing, PS1), Fluttershy (singing), Fluttershy (singing, PS1), Luna (singing), Luna (singing, PS1), Pinkie Pie (singing), Pinkie Pie (singing, PS1), Rainbow Dash (singing), Rainbow Dash (singing, alt), Rainbow Dash (singing, PS1), Rarity (singing), Rarity (singing, PS1), Scootaloo (singing), Scootaloo (singing, alt), Scootaloo (singing, PS1), Starlight Glimmer (singing, evil), Starlight Glimmer (singing, good), Sweetie Belle (singing), Sweetie Belle (singing, PS1), Twilight Sparkle (singing), Twilight Sparkle (singing, PS1) |
|    so_vits_svc_4_model_pack_2     |                   :x:                   | Pinkie Pie (angry), Pinkie Pie (annoyed), Pinkie Pie (anxious), Pinkie Pie (fearful), Pinkie Pie (happy), Pinkie Pie (neutral), Pinkie Pie (nonverbal), Pinkie Pie (sad), Pinkie Pie (sad shouting), Pinkie Pie (shouting), Pinkie Pie (surprised), Pinkie Pie (tired), Pinkie Pie (whispering)                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|    so_vits_svc_5_model_pack_0     |           :heavy_check_mark:            | Applejack (singing, mane6), Fluttershy (singing, mane6), Pinkie Pie (singing), Pinkie Pie (singing, mane6), Rainbow Dash (singing, mane6), Rarity (singing, mane6), Twilight Sparkle (singing, mane6)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|         rvc_model_pack_0          |           :heavy_check_mark:            | Babs Seed, Big McIntosh, Braeburn, Bunni Bunni, Cozy Glow, Cream Heart, Derpy Hooves, Diamond Tiara, Doctor Whooves, Gallus, Octavia Melody, Thorax, Twilight Sparkle (singing), Vinyl Scratch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|         rvc_model_pack_1          |           :heavy_check_mark:            | Applejack, Applejack (alt), Fluttershy, Fluttershy (alt), Pinkie Pie, Pinkie Pie (alt), Rainbow Dash (alt), Rarity (alt), Twilight Sparkle (alt)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

### Loading Custom Models
If you have acquired or trained a model that is not included with Hay Say, you can add it to Hay Say by copying it to the custom models folder inside the main docker container. 
1. First, make sure Hay Say is running. 
2. Execute the following command in a terminal or Command Prompt. It will display information about all of the Docker containers:
```
docker container ls
```
Note: You may need to expand the command window to properly display the output, which is arranged like a wide table. You should see a column titled "IMAGE" in the output. Look for the entry "hydrusbeta/hay_say:hay_say_ui" and find the corresponding container name under the "NAMES" column. You will need that name in a moment:
![Screenshots showing one possible output of "docker container ls"](documentation%20images/main%20container%20name.png)
The name you see might be a little different. For example, another name I have seen on someone else's machine was "hay_say_ui-hay_say_ui-1".  
3. Create a folder for each of the architectures within the custom_models folder by executing the following commands in a new terminal (or Command Prompt if you are using Windows). Replace [container-name] with the name you found in step 2.:
```
docker exec [container-name] -p /root/hay_say/custom_models/so_vits_svc_3
docker exec [container-name] mkdir -p /root/hay_say/custom_models/so_vits_svc_4
docker exec [container-name] mkdir -p /root/hay_say/custom_models/so_vits_svc_5
docker exec [container-name] mkdir -p /root/hay_say/custom_models/controllable_talknet
docker exec [container-name] mkdir -p /root/hay_say/custom_models/rvc
```
4. Arrange and rename your files to match the expected format:  
![Screenshots showing the expected file structures for each architecture's models](documentation%20images/CustomModelFileOrganization.png)  
There are some additional restrictions:
   * For RVC, Hay Say expects the .index and .pth file to have the same name as the folder. 
   * For all versions of so-vits-svc, only a single speaker name is allowed to appear in config.json (see the "spk" key, usually at the bottom of the file).
5. Copy the folder containing your custom model into the desired architecture folder using the "docker cp" command. For example, if you have a folder named "Rainbowshine_Custom" on your desktop containing a so-vits-svc 4.0 model, you can copy it by executing the following on Linux or MacOS:
```
docker cp ~/Desktop/Rainbowshine_Custom/. [container-name]:/root/hay_say/custom_models/so_vits_svc_4/RainbowShine_Custom
```
or the following command on Windows:
```
docker cp %HOMEDRIVE%%HOMEPATH%/Desktop/Rainbowshine_Custom/. [container-name]:/root/hay_say/custom_models/so_vits_svc_4/RainbowShine_Custom
```
Note: The dot at the end of "~/Desktop/Rainbowshine_Custom/." is not a typo, so don't leave it out. It instructs Docker to copy all the contents of the Rainbowshine_Custom folder.  
Note #2: I recommend that you name the folder with "_Custom" appended to the end as I have done in this example. That will avoid a name clash in case the character is added to one of Hay Say's model packs in the future.  
6. Finally, restart Hay Say (type ctrl+c in Hay Say's terminal and then execute "docker compose up" again)


### Enabling GPU Integration
GPU integration is turned off by default in Hay Say. This is to prevent an error for users who do not have a Cuda-capable GPU. If you do have a Cuda-capable GPU, you can enable GPU integration by editing the docker-compose.yaml file. There are several place (one under each architecture) where you will see the following lines:
```
# resources:
#   reservations:
#     devices:
#       - driver: nvidia
#         count: all
#         capabilities: [gpu]
```
To enable GPU for that architecture, uncomment those lines. i.e. remove the hashtags so that they look like this instead:
```
resources:
  reservations:
    devices:
      - driver: nvidia
        count: all
        capabilities: [gpu]
```


### Installing Only Specific Architectures
You can edit the docker-compose.yaml file so that only specific architecutres are downloaded. The UI will still show tabs for all architectures, but will throw an error if you try to generate audio for an architecture which you didn't download. 

If you don't want to install so-vits-svc 3.0, for example, comment out the following lines in docker-compose.yaml by adding a hashtag character (#) in front of them before you run the "docker compose up" command for the first time:
```
so_vits_svc_3_server:
  image: hydrusbeta/hay_say:so_vits_svc_3_server
  working_dir: /root/hay_say/so_vits_svc_3
  volumes:
    - so_vits_svc_3_model_pack_0:/root/hay_say/so_vits_svc_3_model_pack_0
    - so_vits_svc_3_model_pack_1:/root/hay_say/so_vits_svc_3_model_pack_1
    - custom_models:/root/hay_say/custom_models
    - audio_cache:/root/hay_say/audio_cache
```
If you do that, you should also comment out the following lines too so you don't download all the models for so-vits-svc 3.0:
```
so_vits_svc_3_model_pack_0:
  image: hydrusbeta/hay_say:so_vits_svc_3_model_pack_0
  volumes:
    - so_vits_svc_3_model_pack_0:/root/hay_say/so_vits_svc_3_model_pack_0
```

## The Technical Design of Hay Say

The user interface code for Hay Say runs in its own Docker container, hay_say_ui, and the UI is accessed by the user via a web browser. Each AI architecture (e.g. so-vits-svc or ControllableTalkNet) is installed in its own container and a simple Flask web server runs in each one, listening for connections. Each Flask web server defines a /generate method which invokes the AI archtecture to generate an audio file.

![diagram of Hay Say's networking setup, showing that the main UI container communicates with the AI Architecture containers by sharing files and by using webservice calls to trigger audio generation](documentation%20images/design%20diagram.png)

After the user enters their desired options and presses the "Generate!" button, hay_say_ui first preprocesses the audio and saves the result to a mounted volume, audio_cache. It then makes a web service call to the container with the desired AI architecture, instructing it to generate audio. That container reads the preprocessed audio from audio_cache, generates a pony voice from it, and saves it back to audio_cache. The hay_say_ui container then reads the generated audio, performs any postprocessing, and presents the result to the user via an HTML audio element. 

Hence, there are 2 mechanisms of communication between the docker containers: calling web services and passing files over a shared volume.

Weights for the neural networks are stored in Docker volumes that are named like "controllable_talknet_model_pack_0" or "so_vits_svc_4_model_pack_1". Within each volume is a collection of folders, one for each pony character. Each character folder contains files with the model weights for that character. The volumes are initially populated by pulling a Docker image containing models for many characters and mounting the corresponding model_pack volume to that image, which automatically copies all the models from the image to the volume. There is also a "custom models" volume where the user can manually add character weights that are not yet present in any model packs. See the Advanced Topics section.

Hay say also has an "audio_cache" volume for maintaining a small cache of audio files. Any time the user uploads an audio file to Hay Say, the file is saved to audio_cache/raw. When a file is preprocessed, the result is saved to audio_cache/preprocessed. When an audio file is generated, the result is saved to audio_cache/output and, finally, when an output audio is postprocessed, the result is saved in audio_cache/postprocessed. Up to 25 files can be stored in each subfolder before Hay Say begins to automatically delete the oldest files. The purpose of the caching system is twofold. First, by storing the file at various stages of production, Hay Say will be able to present a playback button at each stage, so users can compare the "before" and "after" of a particular step. For example, the user can play back the raw audio and also play back the preprocessed audio to compare them. Second, some operations take a lot of computational power to complete, such as generating output from one of the AI architectures. By caching that output, Hay Say can allow the user to tweak the post-processing options and listen to the results over and over without needing to invoke the AI architecture each time. 

The code for the main UI is in this repository. Code for the Flask servers for the other containers can be found in various other code repositories on hydrusbeta's account. See https://github.com/hydrusbeta?tab=repositories.

## "Roadmap"

Here are some tasks I consider important. I intend to work on them "soon", in no particular order:
1. Additional character models have become available for so-vits-svc 4.0. I'd like to package these up into another model pack.
2. There are currently no preprocessing or postprocessing options. I need to do requirements gathering and start adding some options. 
3. I forsee a need for a "Hay Say launcher" that lets the user select which characters and architectures they want to download and run. That way, the user doesn't have to download *everything* if all they want is, say, the TTS solutions like controllable talknet for specific characters. This also gives the user some control over memory usage on a resource-constrained machine, and would be a good place for downloading updates.
4. New and upcoming architectures are on my radar:
    * Retrieval-based Voice Converstion (RVC)
    * BarkAI
    * so-vits-svc 5.0
5. Hay Say runs terribly on Apple Silicon. I'd like to see whether performance can be improved by re-building the images using ARM base images.
6. Write up more documentation on the technical details of Hay Say and tutorials on: adding a new architecture, adding a model pack, and adding pre/postprocessing options.
7. Currently, the "Generate!" button becomes disabled if a required input has not been provided yet. This might be confusing for users. Instead, let them hit the "Generate!" button and then highlight the missing, required fields in red, along with a useful error message.

Plus, there are numerous minor code improvement opportunities that I have marked with "todo" throughout the codebase.

### A note on Google Colab
I have decided to focus on developing locally-running software and have no plans to port this project over to Google Collab. If someone else wants to work on doing that, however, I would be happy to provide support.


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

| Machine Name          | Age of Computer (years) |       CPU        |       RAM        | Loading time for a short audio recording (s) | Controllable TalkNet Generation time (s) | so-vits-svc 3.0 Generation time (s) | so-vits-svc 4.0 Generation time (s) |
|-----------------------|:-----------------------:|:----------------:|:----------------:|:--------------------------------------------:|:----------------------------------------:|:-----------------------------------:|:-----------------------------------:|
| Custom Built Tower    |           0.5           |   13th gen i9    | 32 GB (6000 MHz) |                      0                       |                    8                     |                  5                  |                  6                  |
| Aspire TC-895         |            2            |   10th gen i5    | 12 GB (2600 MHz) |                      3                       |                   26.5                   |                30.5                 |                27.5                 |
| Dell XPS 13 9380      |            4            |    8th gen i7    | 16 GB (1200 MHz) |                      1                       |                    44                    |                 38                  |                 41                  |
| Toshiba Qosmio laptop |           10            |    4th gen i7    | 16 GB (1600 MHz) |                      10                      |                   198                    |                 174                 |                 227                 |
| Mac Mini              |            0            | M2 Apple Silicon |       8 GB       |                      27                      |                 N/A [1]                  |                 589                 |                 575                 |  

[1] Test failed with an error. Unable to generate audio.

	

