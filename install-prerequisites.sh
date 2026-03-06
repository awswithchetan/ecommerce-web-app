#!/bin/bash
set -e

echo "=========================================="
echo "Installing Prerequisites for eCommerce App"
echo "=========================================="

# Update system packages
echo "Updating system packages..."
sudo yum update -y

# Install Docker
echo "Installing Docker..."
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker $USER

# Install Docker Compose
echo "Installing Docker Compose..."
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install Docker Buildx
echo "Installing Docker Buildx..."
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
mkdir -p ~/.docker/cli-plugins
curl -L "https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-amd64" -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx

# Install Node.js 20 LTS
echo "Installing Node.js 20 LTS..."
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install nodejs -y

# Install Git (if not already installed)
echo "Installing Git..."
sudo yum install git -y

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Installed versions:"
docker --version
docker-compose --version
docker buildx version
node --version
npm --version
git --version
echo ""
echo "IMPORTANT: You need to log out and log back in for Docker group changes to take effect."
echo "After re-login, verify Docker works without sudo: docker ps"
echo ""
