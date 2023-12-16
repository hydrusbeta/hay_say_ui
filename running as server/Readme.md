# How to run Hay Say on AWS for others to use

## 1. Launch an EC2 instance

There are lots of instances to choose from. I initially used g4dn.12xlarge, which gives four T4 GPUs and 48 vCPUs, and 
plenty of RAM and SSD space, but this was definitely overkill for the number of users. I later switched to c6a.4xlarge, 
which comes with 16 reasonally-performant vCPUs. You will want an instance with at least 8GB RAM unless you're OK with 
not bringing up all of the architectures.  

* Specs for each instance type can be found here:  
https://aws.amazon.com/ec2/instance-types/  
* On-demand pricing can be found here:  
https://aws.amazon.com/ec2/pricing/on-demand/  
* You can get a better deal if you lock in a 1- or 3- year term. "Reserved Instance" pricing is here:  
https://aws.amazon.com/ec2/pricing/reserved-instances/pricing/  
* Some instances (the ones with a "d" in their name like g4dn.12xlarge) come with a hard drive. For the ones that don't 
come with a hard drive (or do, but have too small a drive), you will need to purchase EBS storage and connect it to the 
EC2 instance. I recommend at least 150GB (maybe 200GB to be safe). I've only ever used "gp3 - Storage" so I can't 
provide any guidance on price vs performance of the various types of EBS storage. It's all pretty cheap compared to the 
price of the EC2 instance anyways, though. Pricing can be found here:  
https://aws.amazon.com/ebs/pricing/  

Please note that if you want to use a GPU instance, such as g4dn.xxx, you will probably need to create a support ticket 
with Amazon to increase your quota for running on-demand G and VT instances. It's a bit of a hassle, but it's to 
safeguard customers against accidentally using more resources than they intend and getting stuck with a large bill, to 
protect the integrity of Amazon's ecosystem by mitigating unexpected increases in overall demand, and to combat fraud 
(e.g. someone using a stolen credit card to set up a malicious server for conducting attacks). If your AWS account is 
brand new, be aware that Amazon may deny your quota increase until you've been a customer for a while and they gain 
confidence that you're not up to any mischief.  

Not all instances are available in every region. To check whether an instance is available in the region you want:
1. Login to https://console.aws.amazon.com/console/home
2. Services -> EC2
3. To the right of the search bar, there should be a dropdown menu that lets you select a region. Select the region you want. The closer the region is to your user base, the less latency they will experience.
4. Click "Launch Instance" (don't worry - it won't actually launch an instance until you've clicked another Launch button on the next page)
5. Scroll down to "Instance Type". You can search for instances by name here (e.g. c6a.4xlarge). If you can select an instance (make sure you can actually *select* it, not just see it in the dropdown), that means it is available in your desired region.

Once you've decided on an EC2 instance, fill out the rest of the info on the page and actually launch the EC2 instance. 
* Name and Tags - Pick any name you like. This is simply the name that will show up in dashboards.
* Application and OS Images (Amazon Machine Image) - If using an instance with a GPU, click "Browse more AMIs", search 
for "Deep Learning AMI GPU PyTorch" and select the latest version available. Otherwise, just keep the default selection 
in the dropdown (Amazon Linux 2023 AMI).
* Instance Type - See earlier notes
* Key pair (login) - This key is used for accessing your EC2 instance from a console or from SFTP applications. Create 
a new key pair and select "RSA" as the type. Keep the Private key file format as ".pem". Save the .pem file to the 
".ssh" folder in your home directory (e.g. C:\\\\Users\\[your_username]\\.ssh\\ on Windows or 
/home/[your_username]/.ssh/ on Linux and Mac)
* Network Settings - Select "create security group" and make sure that "Allow SSH traffic from", "Allow HTTPS traffic 
from the internet" and "Allow HTTP traffic from the internet" are all selected. Also make sure that "Anywhere" is 
selected in the dropdown next to "Allow SSH traffic from".
* Storage (volumes) - If you selected an instance type that comes with a built-in hard drive (e.g. it has "d" in its 
name) that is large enough, you can skip this step. Otherwise, I recommend at least 150 GB (maybe 200 GB to be safe). 
Please note that Docker stores everything (images, volumes, containers, etc.) in a single root folder and Hay Say will 
use up about 118 GB within Docker after downloading all character models. Therefore, unless you know what you're doing 
and know how to safely split Docker's disk usage across several physical disks, one of your drives must be larger than 
118 GB to fit everything that Hay Say needs. e.g. if you selected an instance that comes with a 59 GB hard drive, don't 
get an EBS drive that is only 100 GB. Even though 59+100 is larger than 150 GB, it won't work because Hay Say needs at 
least 118 GB of contiguous space.

## 2. SSH into the EC2 instance
After you launch your instance, you should be taken to your EC2 Instances dashboard. Look for its Public IPv4 DNS name. 
It should look something like this:  
ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com  
for example:  
ec2-3-13-26-231.us-east-2.compute.amazonaws.com  
To connect to the instance over SSH, run the following command, replacing the portion after the @ symbol with your 
instance's Public IPv4 DNS and replacing name_of_your_private_key with the name of the .pem file you generated and 
downloaded earlier:  
```shell
ssh -i ~/.ssh/[name_of_your_private_key].pem ec2-user@ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com
```

## 3. Format and mount Instance Storage
If you launched an EC2 instance that comes with "Instance Storage" (includes "d" in the name, like g4dn.12xlarge), you 
need to format and mount the instance storage drive. 
1. Determine the device name of your instance storage. You can view your available instance storage with:
    ```shell
    lsblk
    ```
    or
    ```shell
    sudo yum update
    sudo yum install nvme-cli
    sudo nvme list
    ```
2. Create a filesystem on the device using mkfs (replace "nvme1n1" with the actual device name of your instance storage):
    ```shell
    sudo mkfs -t ext4 /dev/nvme1n1
    ```
3. Create a directory on which to mount the device:
    ```shell
    sudo mkdir /data
    ```
4. mount the device (again, replace "nvme1n1" with the actual device name of your instance storage):
    ```shell
    sudo mount /dev/nvme1n1 /data
    ```

## 4. Install Docker
Install Docker:
```shell
sudo yum update -y
sudo amazon-linux-extras install docker
```
note: if you get "amazon-linux-extras command not found", try `sudo yum install docker` instead.  
Start docker and add your user to the docker Linux group:
```shell
sudo service docker start
sudo usermod -a -G docker ec2-user
```

## 5. Explicitly install docker-compose
The version of Docker that you install with either amzaon-linux-extras or yum doesn't come with docker compose, so you must
separately install it.
```shell
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 6. Configure Docker to store data on your largest hard drive
If you launched an EC2 instance that comes with a large (150 GB or larger) Instance Storage drive and you mounted the Instance Storage at /data, then Docker's root directory by default is probably located on the wrong drive. To get Docker to store its files on the big, instance storage device:
1. Stop docker  
    ```shell
    sudo service docker stop
    ```
2. Create a directory on /data. Note: Docker will change the owner of this new directory to root once you restart it.
    ```shell
    mkdir /data/docker_root
    ```
3. Create the file /etc/docker/daemon.json (or C:\\\\ProgramData\\docker\\config\\daemon.json if you're using a Windows EC2 
instance) if it doesn't exist and add the following to it:
    ```json
    {
      "data-root": "/data/docker_root"
    }
    ```
4. Restart docker
    ```shell
    sudo service docker start
    ```

## 7. Configure Hay Say, Part 1/3
download the server version of docker-compose.yaml
```shell
wget https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/main/running%20as%20server/docker-compose.yaml
```

create necessary volumes
```shell
sudo docker volume create models
sudo docker volume create audio_cache
sudo docker volume create synthapp_models
```

If you are using an EC2 instance that has GPUs, edit docker-compose.yaml to enable GPU inference on all architectures.
To do this, uncomment the following set of lines wherever they appear (this group of lines appears once for each
architecture throughout the docker-compose file):
```yaml
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: all
#           capabilities: [gpu]
```
If your server has more than 1 CUDA GPU, edit docker-compose.yaml to spin up 1 celery_generate_gpu worker per GPU that 
you have, for optimal performance. In the command section under the hay_say_ui service, you will see a line like this:
```yaml
celery --workdir ~/hay_say/hay_say_ui/ -A celery_generate_gpu:celery_app worker --loglevel=INFO --concurrency 1 ...
```
Change `--concurrency 1` to `concurrency [number_of_gpus_your_server_has]`


## 8. Optional Steps

### Use your own domain name
If you own a domain name, you can configure DNS to point it at the EC2 instance.
1. Create an Elastic IP in AWS
   1. Services -> EC2 -> Elastic IPs -> Allocate Elastic IP address
2. Associate the Elastic IP with the EC2 instance
   1. Select the Elastic IP you just created -> Actions -> Associate Elastic IP address
   2. Enter your instance name and leave "Private IP address" blank
   3. click "Associate"
3. Add DNS A-Records for your domain to associate it with the Elastic IP address.
   1. The exact instructions for doing this vary by DNS provider. In general, you will need to login to your account 
   with your DNS provider (which may also be your domain name registrar) and configure the settings for your domain.

### Enable SSL
Note: with any of the three options below, you will eventually be asked to provide a "Common Name" and "Subject Alt 
Names". The Common Name should be your domain name by itself (for example, I use haysay.ai). For the Subject Alt Names, 
I recommend including your domain name by itself, www.yourDomainName, synthapp.yourDomainName, and 
www.synthapp.yourDomainName, along with any desired subdomains. For reference, this is what I use:
* haysay.ai
* www.haysay.ai
* synthapp.haysay.ai
* www.synthapp.haysay.ai
* status.haysay.ai
* www.status.haysay.ai

#### Option 1: Use the EFF's classic Certbot to obtain a certificate from LetsEncrypt
I don't have instructions for this because I never set it up myself. I recommend trying this approach, though, if you 
intend to keep your site up for more than a few months because you can configure Certbot to automatically renew your 
certificates before they expire.

#### Option 2: Use the EFF's Certbot Docker image to obtain a certificate from LetsEncrypt:
1. Generate the certificate file
    ```shell
    sudo docker run -it --rm --name certbot -p 80:80 -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" certbot/certbot certonly
    ```
    Select option 1. When you are asked for the domain names, enter the Subject Alt Names you desire. The first name 
    you enter is also the Common Name. For reference, this is what I use:
    ```
    haysay.ai,www.haysay.ai,synthapp.haysay.ai,www.synthapp.haysay.ai,status.haysay.ai,www.status.haysay.ai
    ```
2. Change the permissions on the generated files (note: if the files are not in /etc/letsencrypt/archive/[domainName], 
check /etc/letsencrypt/live/[domainName])
    ```shell
    sudo chmod 600 /etc/letsencrypt/archive/[domainName]/cert1.pem
    sudo chmod 600 /etc/letsencrypt/archive/[domainName]/chain1.pem
    sudo chmod 600 /etc/letsencrypt/archive/[domainName]/fullchain1.pem
    sudo chmod 600 /etc/letsencrypt/archive/[domainName]/privkey1.pem
    ```
3. Copy the certificate files into a standard folder:
    ```shell
    sudo cp /etc/letsencrypt/archive/[domainName]/fullchain1.pem /etc/pki/tls/certs/fullchain.pem
    sudo cp /etc/letsencrypt/archive/[domainName]/privkey1.pem /etc/pki/tls/private/privkey.pem
    ```
    Note: simply linking the files won't be sufficient. You must make hard copies because we need to mount the 
    directories into a Docker container. i.e. don't do this:
    ```shell
    # sudo ln -s /etc/letsencrypt/archive/[omainName]/fullchain1.pem /etc/pki/tls/certs/fullchain.pem
    # sudo ln -s /etc/letsencrypt/archive/[omainName]/privkey1.pem /etc/pki/tls/private/privkey.pem
    ```
    Actually, you may be able to get away with just linking if you configure the docker-compose file to also mount 
    /etc/letsencrypt/archive/[domainName]/ but I'll let you figure out the details if you want to do that.

#### Option 3: Obtain a certificate the old-fashioned way:
1. Create a private key
    cd /etc/pki/tls/private
    sudo opensll genrsa -out haysay.key 4096
    sudo chown root:root /etc/pki/tls/private/haysay.key
    sudo chmod 600 /etc/pki/tls/private/haysay.key
2. Create a Certificate Signing Request (CSR)
    sudo openssl req -new -key haysay.key -out csr.pem
    Note: you will be prompted for a bunch of info. only Common Name is required, but I recommend entering Subject Alt Names too (see earlier note).
3. Send the CSR to a certificate authority through whatever channel they require. They will send back the certificate file(s) (.pem or .crt).
4. Place the CA-provided files in /etc/pki/tls/certs then tighten the permissions:
    sudo chown root:root /etc/pki/tls/certs/mycert.crt
    sudo chmod 600 /etc/pki/tls/certs/mycert.crt

#### Configure the docker-compose file to use your certificate
Whichever option you used above, you must now configure the docker-compose.yaml file to use your certificate. 
1. Locate the `command` directive under the nginx service and uncomment the following lines:
    ```yaml
        # server {\\n
        #    listen 80;\\n
        #    server_name _;\\n
        #    return 301 https://\\$$host\\$$request_uri;\\n
        # }\\n
    ```
2. Change the following line:
    ```
    listen 80 default_server;\\n
    ```
    to this:
    ```
    listen 443 ssl default_server;\\n
    ssl_certificate /etc/pki/tls/certs/fullchain.pem;\\n
    ssl_certificate_key /etc/pki/tls/private/privkey.pem;\\n
    ```
3. Similarly, change the following line:
    ```
    listen 80;\\n
    ```
    to this:
    ```
    listen 443 ssl;\\n
    ssl_certificate /etc/pki/tls/certs/fullchain.pem;\\n
    ssl_certificate_key /etc/pki/tls/private/privkey.pem;\\n
    ```
4. Uncomment the following lines:
    ```yaml
        #    volumes:
        #      - type: bind
        #        source: /etc/pki/tls/certs
        #        target: /etc/pki/tls/certs
        #      - type: bind
        #        source: /etc/pki/tls/private
        #        target: /etc/pki/tls/private
    ```
For clarity, the nginx section of your docker-compose file should look like this:
```yaml
  nginx:
    depends_on:
      - hay_say_ui
      - synthapp
    image: hydrusbeta/nginx:synthapp
    user: root
    ports:
      - 80:80
      - 443:443
    volumes:
      - type: bind
        source: /etc/pki/tls/certs
        target: /etc/pki/tls/certs
      - type: bind
        source: /etc/pki/tls/private
        target: /etc/pki/tls/private
    command: ["/bin/sh", "-c", "
               printf \"server_tokens off;\\n
                 access_log /var/log/nginx/synthapp.access.log;\\n
                 error_log /var/log/nginx/synthapp.error.log;\\n
                 limit_req_zone \\$$binary_remote_addr zone=mylimit:10m rate=2r/s;\\n
                 client_max_body_size 100M;\\n
                 \\n
                 server {\\n
                    listen 80;\\n
                    server_name _;\\n
                    return 301 https://\\$$host\\$$request_uri;\\n
                 }\\n
                 \\n
                 server {\\n
                    listen 443 ssl default_server;\\n
                    ssl_certificate /etc/pki/tls/certs/fullchain.pem;\\n
                    ssl_certificate_key /etc/pki/tls/private/privkey.pem;\\n
                    server_name _;\\n
                    location / {\\n
                       limit_req zone=mylimit burst=500 nodelay;\\n
                       proxy_pass http://hay_say_ui:6573;\\n
                       proxy_set_header Host \\$$host;\\n
                       proxy_set_header Cookie \\$$http_cookie;\\n
                    }\\n
                 }\\n
                 \\n
                 server {\\n
                    listen 443 ssl;\\n
                    ssl_certificate /etc/pki/tls/certs/fullchain.pem;\\n
                    ssl_certificate_key /etc/pki/tls/private/privkey.pem;\\n
                    server_name .synthapp.*;\\n
                    location / {\\n
                       limit_req zone=mylimit burst=50 nodelay;\\n
                       proxy_pass http://synthapp:3334;\\n
                       proxy_set_header Host \\$$host;\\n
                    }\\n
                    location /static {\\n
                       limit_req zone=mylimit burst=50 nodelay;\\n
                       autoindex on;\\n
                       alias /home/luna/synthapp/website/ponyonline/static;\\n
                    }\\n
                 }\\n\" 
               > /etc/nginx/conf.d/synthapp.conf && 
               nginx -g 'daemon off;'"]
```

### Enable GPU monitoring
You can capture metrics about GPU usage using Amazon Cloudwatch so you can view them later in the Metrics console in 
your AWS account.

Note: see the [Capturing GPU Telemetry on the Amazon EC2 Accelerated Computing Instances](https://aws.amazon.com/blogs/compute/capturing-gpu-telemetry-on-the-amazon-ec2-accelerated-computing-instances/) 
blog for more detailed guidance.  

Create an IAM Role, associate permissions to stream metrics to Cloudwatch with it, and attach
the role to the EC2 instance. Here is a Permission you can use, in JSON format. You enter this in the AWS web console 
while creating a new Permission:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "cloudwatch:PutMetricStream",
                "logs:CreateLogDelivery",
                "logs:CreateLogStream",
                "cloudwatch:PutMetricData",
                "logs:UpdateLogDelivery",
                "ec2:DescribeTags",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
                "cloudwatch:ListMetrics"
            ],
            "Resource": "*"
        }
    ]
}
```
Next, back in the terminal, rename the json file at 
/opt/aws/amazon-cloudwatch-agent/etc/dlami-amazon-cloudwatch-agent-partial.json and edit it.
```shell
cd /opt/aws/amazon-cloudwatch-agent/etc
sudo mv dlami-amazon-cloudwatch-agent-partial.json amazon-cloudwatch-agent.json
sudo vi amazon-cloudwatch-agent.json
```
Configure the json file so that metrics are collected by the root user every 5 seconds
```json
"metrics_collection_interval": 5,
"run_as_user": "root"
```
Finally, restart the amazon-cloudwatch-agent service
```shell
sudo systemctl restart amazon-cloudwatch-agent.service
```
If it doesn't seem to be working, look for errors in the log at 
`/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log`

## 9. Configure Hay Say, Part 2/3

There are a few places in the docker-compose.yaml file where a wildcard is used for hostname matching. To prevent host 
header attacks and cache poisoning, I strongly recommend replacing the wildcard expressions with absolute values. For 
example, if the Public IPv4 DNS name of your instance is ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com, then:
1. Replace this:
    ```
    server_name _;\\n
    ```
    with this:
    ```
    server_name .ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com;\\n
    ```
2. Replace this:
    ```
    server_name .synthapp.*;\\n
    ```
    with this:
    ```
    server_name .synthapp.ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com;\\n
    ```
3. and replace this:
    ```
    sed -i \"s/ALLOWED_HOSTS = \\['127.0.0.1', 'localhost'\\]/ALLOWED_HOSTS = ['.synthapp.*']/\" website/ponyonline/ponyonline/settings.py &&
    ```
    with this:
    ```
    sed -i \"s/ALLOWED_HOSTS = \\['127.0.0.1', 'localhost'\\]/ALLOWED_HOSTS = ['.synthapp.ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com']/\" website/ponyonline/ponyonline/settings.py &&
    ```
If you followed the steps in the [Optional Steps](#8.-optional-steps) section above to use your own domain, replace the 
wildcards with your own domain name instead.

## 10. Download character models
1. Start Hay Say (note that this is a different command than what you would normally use to run docker compose on a local 
installation. There is a hyphen between "docker" and "compose" here)
    ```shell
    sudo /usr/local/bin/docker-compose up
    ```
2. Open the UI and download all models for all architectures . You can get to the UI by pasting the Public IPv4 DNS name
of your instance (e.g. http://ec2-WWW-XXX-YYY-ZZZ.region.compute.amazonaws.com) into the URL bar of your favorite 
browser. If you followed the [Optional Steps](#8.-optional-steps) above to point your own domain name at the EC2 
instance, then you can go to http://[yourDomainNameHere] instead.
3. The Hay Say UI should come up. Go to each architecture and download all the character models. 
4. Stop Hay Say by typing CTRL+C into the terminal.

## 11. Configure Hay Say, Part 3/3
1. Open docker-compose.yaml again and search for the string "enable_model_management". Make sure it is set to False. This 
prevents end users from deleting models.
2. Optional, but recommended: Two lines above that, there should be a line that starts with:
    ```
    celery --workdir ~/hay_say/hay_say_ui/ -A celery_download:celery_app worker ... 
    ```
	Delete that line. 

Todo: include instructions on locking down synthapp. i.e., hiding the model download menu and such

## 12. Launch Hay Say
Start Hay Say again:
```shell
sudo /usr/local/bin/docker-compose up
```
Now hit CTRL+z to suspend Hay Say. This will let you type in the prompt again. Move Hay Say to the background (thus also
un-suspending it) so you can safely exit the ssh session:
```shell
bg
exit
```
