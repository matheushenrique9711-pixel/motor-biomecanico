#!/bin/bash

# Motor Biomecânico - Docker Initialization Script
# This script sets up Docker environment and checks requirements

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Docker installation
print_header "Checking Docker Installation"

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
print_success "Docker installed: $DOCKER_VERSION"

# Check Docker Compose installation
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

COMPOSE_VERSION=$(docker-compose --version)
print_success "Docker Compose installed: $COMPOSE_VERSION"

# Check Docker daemon
print_header "Checking Docker Daemon"

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo "Please start Docker Desktop or the Docker daemon"
    exit 1
fi

print_success "Docker daemon is running"

# Check disk space
print_header "Checking System Resources"

# Get available disk space (in GB)
DISK_AVAILABLE=$(df / | tail -1 | awk '{print $4}' | xargs -I {} expr {} / 1024 / 1024)
print_success "Available disk space: ${DISK_AVAILABLE}GB"

if (( $(echo "$DISK_AVAILABLE < 10" | bc -l) )); then
    print_warning "Low disk space (< 10GB). Docker images may fail to build"
fi

# Create necessary files
print_header "Setting Up Environment Files"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_success "Creating .env from .env.example"
    cp .env.example .env
    print_warning ".env file created. Please review and update with your settings"
else
    print_success ".env file already exists"
fi

# Create STL exports directory
mkdir -p stl_exports
print_success "STL exports directory created"

# Create backend .env if needed
if [ ! -f backend/.env ]; then
    print_success "Using backend/.env.example as template"
else
    print_success "Backend environment file exists"
fi

# Check docker-compose.yml
print_header "Checking Configuration"

if [ -f docker-compose.yml ]; then
    print_success "docker-compose.yml found"
else
    print_error "docker-compose.yml not found"
    exit 1
fi

if [ -f Dockerfile ]; then
    print_success "Backend Dockerfile found"
else
    print_warning "Backend Dockerfile not found"
fi

if [ -f frontend/Dockerfile ]; then
    print_success "Frontend Dockerfile found"
else
    print_warning "Frontend Dockerfile not found"
fi

# Test Docker commands
print_header "Testing Docker Commands"

# Test image building (without actually building)
if docker-compose config > /dev/null 2>&1; then
    print_success "Docker Compose configuration is valid"
else
    print_error "Docker Compose configuration is invalid"
    exit 1
fi

# Summary
print_header "Setup Summary"

echo ""
echo -e "${GREEN}Motor Biomecânico Docker Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review .env file: cat .env"
echo "  2. Start development environment: make dev-d"
echo "     or: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
echo "  3. Start production environment: make prod-d"
echo "     or: docker-compose up -d"
echo "  4. Check service health: make health"
echo "  5. View logs: make logs"
echo ""
echo "Useful commands:"
echo "  make help           - Show all available commands"
echo "  make dev            - Start development with hot reload"
echo "  make prod           - Start production"
echo "  make logs           - View service logs"
echo "  make down           - Stop all services"
echo ""
echo "For more information, see DOCKER_SETUP.md"
echo ""

# Optional: Ask if user wants to start services
read -p "Do you want to start the services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Start in development (d) or production (p) mode? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Dd]$ ]]; then
        print_header "Starting Development Environment"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        echo -e "${GREEN}Development environment started!${NC}"
        echo "Frontend: http://localhost:5173 (Vite dev server)"
        echo "Backend: http://localhost:8000/api"
    elif [[ $REPLY =~ ^[Pp]$ ]]; then
        print_header "Starting Production Environment"
        docker-compose up -d
        echo -e "${GREEN}Production environment started!${NC}"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:8000/api"
    fi

    # Wait a moment and show health
    sleep 5
    print_header "Service Status"
    docker-compose ps
fi

exit 0
