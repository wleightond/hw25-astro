# hw25-astro

To run outside of Raspbian you first need to mock out `RPi.GPIO`:
```
ln -s RPi_mock RPi
```

---

The service needs debugging, but eventually the process will be something like:
```
sudo cp sky-tracking.service /etc/systemd/system/sky-tracking.service
sudo systemctl enable sky-tracking
sudo systemctl start sky-tracking
```
The tracker needs to be plugged in by the time the pi finishes booting if using this route.