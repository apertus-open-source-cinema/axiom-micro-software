# AXIOM micro driver
A driver for controlling the AXIOM micro.

## Working Principle
The code in this repository takes care of all the low level communication to the hardware
of the camera (ie. the image sensor). This is done with a variety of protocols (ie. `i2c`
or direct memory access to shared memory regions with the FPGA).

Similar to a Linux Kernel driver, a filesystem hierarchy is exposed, which represents the
different parameters of the hardware. This "driver" only handles parameters and "not so 
realtime" stuff and no recorded images. 

Exposing the parameters as a filesystem allows for simple solutions for a wide veriety
of use cases:
1) Write/ Read single parameters:
    ```bash
    $ cat /camera_control/sensor/exposure_time
    20
    $ echo "5" > /camera_control/sensor/exposure_time # sets the exposure time to 1/20s
    ```
2) Save and Restore the current state of the camera:
    ```bash
    $ cp -r /camera_control/ ./some_nice_config
    $ cp -r ./some_nice_config/ /camera_control
    ```
3) Expose the current parameters over the network:
    ```bash
    $ (cd /camera_control; python3 -m http.server)
    ```

## No Kernel Space Code
However, no kernel code is needed to expose the outlined functionality and `FUSE` is used 
to implement the filesystem. This gives better debuggability and allows us to code
python instead of Kernel style C at the cost of some performance and the ability to handle
interrupts.


## Getting Started
```bash
$ mkdir /camera_control
$ python3 -m camera_control /camera_control/
```