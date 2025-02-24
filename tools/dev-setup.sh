#!/usr/bin/env bash
set -evo

VENV_PATH="${1:-/opt/directord}"
CLONE_PATH="${3:-/opt/directord-src}"
SETUP="${4:-true}"

. /etc/os-release

if [[ ${ID} == "rhel" ]] || [[ ${ID} == "centos" ]]; then
  # Install lynx from the powertools repo
  if ! which lynx; then
    if ! dnf -y install lynx; then
      dnf -y install http://mirror.centos.org/centos/8/PowerTools/x86_64/os/Packages/lynx-2.8.9-2.el8.x86_64.rpm \
                     http://mirror.centos.org/centos/8/BaseOS/x86_64/os/Packages/centos-indexhtml-8.0-0.el8.noarch.rpm
    fi
  fi
  TRIPLEO_REPOS=$(lynx -dump -hiddenlinks=listonly https://trunk.rdoproject.org/centos8/component/tripleo/current/ | awk '/python3-tripleo-repos.*rpm$/ {print $2}')
  VERSION_INFO="${VERSION_ID%%"."*}"
  if [[ ${ID} == "rhel" ]]; then
    dnf install -y python3 ${TRIPLEO_REPOS}
    DISTRO="--no-stream --distro rhel${VERSION_INFO[0]}"
    tripleo-repos ${DISTRO} -b master current-tripleo ceph
  elif [[ ${ID} == "centos" ]]; then
    dnf install -y python3 ${TRIPLEO_REPOS}
    DISTRO="--distro centos${VERSION_INFO[0]}"
    if grep -qi "CentOS Stream" /etc/os-release; then
      DISTRO="--stream ${DISTRO}"
    else
      DISTRO="--no-stream ${DISTRO}"
    fi
    tripleo-repos ${DISTRO} -b master current-tripleo ceph
  fi
fi

if [[ ${ID} == "rhel" ]] || [[ ${ID} == "centos" ]]; then
  PACKAGES="git python38-devel gcc python3-pyyaml zeromq libsodium"
  dnf -y install ${PACKAGES}
  PYTHON_BIN=${2:-python3.8}
elif [[ ${ID} == "fedora" ]]; then
  PACKAGES="git python3-devel gcc python3-pyyaml zeromq libsodium"
  dnf -y install ${PACKAGES}
  PYTHON_BIN=${2:-python3}
elif [[ ${ID} == "ubuntu" ]]; then
  PACKAGES="git python3-all python3-venv python3-yaml python3-zmq"
  apt update
  apt -y install ${PACKAGES}
  PYTHON_BIN=${2:-python3}
else
  echo -e "Failed unknown OS"
  exit 99
fi

# Create development workspace
rm -rf ${VENV_PATH}
${PYTHON_BIN} -m venv ${VENV_PATH}
${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel bindep pyyaml

${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel

if [ ! -d "${CLONE_PATH}" ]; then
  git clone https://github.com/cloudnull/directord ${CLONE_PATH}
fi
${VENV_PATH}/bin/pip install ${CLONE_PATH}[all]

if [ "${SETUP}" = true ]; then
  echo -e "\nDirectord is setup and installed within [ ${VENV_PATH} ]"
  echo "Activate the venv or run directord directly."

  if systemctl is-active directord-server &> /dev/null; then
    systemctl restart directord-server
    echo "Directord Server Restarted"
  else
    echo "Directord Server can be installed as a service using the following command(s):"
    echo "${VENV_PATH}/bin/directord-server-systemd"
  fi

  if systemctl is-active directord-client &> /dev/null; then
    systemctl restart directord-client
    echo "Directord Client Restarted"
  else
    echo "Directord Client can be installed as a service using the following command(s):"
    echo "${VENV_PATH}/bin/directord-client-systemd"
  fi
fi