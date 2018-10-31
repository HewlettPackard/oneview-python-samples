# Running HPE python-hpOneView in a container

## Introduction

This how to guide and accompanying [GitHub repository](https://github.com/HewlettPackard/oneview-python-samples/tree/master/oneview-python-in-container) will show how to use the HPE [python-hpOneView](https://github.com/HewlettPackard/python-hpOneView) SDK from a containerized version on the [Docker Store](https://store.docker.com/community/images/hewlettpackardenterprise/oneview-python-debian) to manage and configure HPE infrastructure.

## HPE oneview-hpOneView in a container

Docker containers provide a low friction way to get developer environments and CI/CD pipelines up and running easily and consistently. But they do present challenges. They are isolated by design and are immutable. Somehow the oneview-python container needs to get access to the Python code to run.

*Editor's note: Let's settle the debate whether [Python is a programming language or scripting language](https://www.quora.com/Is-Python-a-programming-language-or-scripting-language). Hint: It's both.*

### Setting up the Python code

Docker volumes are storage that can be shared among containers and persist beyond the lifecycle of containers. Begin by creating a Docker volume:

```bash
docker volume create pythoncode
```

Next run a container that can access the Python code and allow you to edit the code:

```bash
docker run -it --rm -v pythoncode:/pythoncode --entrypoint /bin/ash alpine/git
```

This will run an Alpine Linux container with git installed. The arguments run the container in interactive mode (-it), remove the container on exit (--rm), mount the Docker volume `pythoncode` at the mount point `/pythoncode`, and override the default command (git) with the `ash` shell.

Use git to get the Python sample code:

```bash
cd /pythoncode
git clone https://github.com/HewlettPackard/oneview-python-samples.git
```

Edit the file `EnclosureGroups.py' and modify the CONFIG object to provide the IP address and credentials for the OneView appliance or Synergy composer:

```bash
cd /pythoncode/oneview-python-samples/oneview-python-in-container
vi EnclosureGroups.py
```

### Running the Python code

At this point you are ready to run the Python code. Either exit the alpine/git container or open another command window and run the `oneview-python-debian` container:

```bash
docker run -it --rm -v pythoncode:/pythoncode hewlettpackardenterprise/oneview-python-debian /bin/bash
cd /pythoncode/oneview-python-samples/oneview-python-in-container
```

You are now in a bash shell ready to run code with the `python-hpOneView` SDK. Enclosure Groups represent the top of the hierarchy of OneView resources. The following command will get information about all Enclosure Groups:

```bash
python EnclosureGroups.py
```

### Cleanup

When you no longer need the shared volume it can be removed with:

```bash
docker volume rm pythoncode
```

### Conclusion

You now have an environment to run Python code using the HPE OneView Python SDK in a container. You can switch to other directories in the cloned repository and try other samples. Additional samples can be found in the [python-hpOneView](https://github.com/HewlettPackard/python-hpOneView) repository under `examples`.

Copyright (2018) Hewlett Packard Enterprise Development LP
