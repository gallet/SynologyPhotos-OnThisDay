# Synology Photos - On This day
Use Synology APIs to mimic the "On this day" feature available, e.g., on Microsoft One Drive.
The program tags each picture with a MM:DD tag and modifies the conditions of 2 conditional albums to only have the pictures with the MM:DD tag matching today's date

This is by no mean a state-of-the-art program and improvements are more than welcome.

This can be used to build a container to deploy on your own Synology or you can use [this image](https://hub.docker.com/r/ggallet/synology_photos-on_this_day) straight away.
My experience is that when you deploy the container on your Synology, you will need to hit the local IP address in http not https on the standard port, e.g., http://192.168.1.42:5000, when I tried with the external address, e.g., https://nas.example.com, it would fail systematically because the SSL certificate chain would break somehow (feedback welcome).
