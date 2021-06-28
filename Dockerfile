FROM library/python:3.9

# basic tools
RUN set -xe \
  && apt update && apt install -y \
    wget \
    curl \
    less \
    vim \
    git \
  && apt clean

# install docker(CLI)
# refs: https://docs.docker.com/engine/install/debian/
RUN  set -xe \
  && apt update && apt install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg \
      lsb-release \
  && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
  && echo \
      "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt update && apt install -y \
      docker-ce-cli \
  && apt clean

# install python dependencies
WORKDIR /work
COPY requirements.txt /work
RUN pip3 install --upgrade -r requirements.txt
