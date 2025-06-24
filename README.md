# Family Chore Tracker

A family chore management application that helps parents track chores, rewards, and goals for their children.

## Features

- Track chores assigned to children
- Calculate earnings based on time spent ($10/hour default rate)
- Set and track individual and family savings goals
- Record positive/negative behavior adjustments
- View earnings and activities on an interactive dashboard
- Calendar view for scheduling and reviewing activities

## Deployment Instructions for Raspberry Pi 5

### Prerequisites

1. Raspberry Pi 5 with Raspberry Pi OS (or any Debian-based OS)
2. Docker and Docker Compose installed
3. Git installed (optional, for cloning the repository)

### Docker Installation (if not already installed)

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Docker dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to the docker group (to run Docker without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose-plugin
```

### Deploying the Application

1. Create a project folder and navigate into it:
   ```bash
   mkdir family-chore-tracker
   cd family-chore-tracker
   ```

2. Copy all application files to this directory (or clone from your repository)

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file to set secure passwords:
   ```bash
   nano .env
   ```

5. Build and start the application:
   ```bash
   docker compose up -d
   ```

6. The application will be available at `http://[your-raspberry-pi-ip]:5000`

### Stopping the Application

```bash
docker compose down
```

### Updating the Application

```bash
# Pull the latest code changes
git pull  # If using a git repository

# Rebuild and restart
docker compose down
docker compose up -d --build
```

### Viewing Logs

```bash
docker compose logs -f
```

### Backing Up the Database

```bash
docker compose exec db pg_dump -U chorechamp chorechamp > backup.sql
```

### Restoring from Backup

```bash
cat backup.sql | docker compose exec -T db psql -U chorechamp chorechamp
```

## First-time Setup

1. Navigate to `http://[your-raspberry-pi-ip]:5000`
2. Create a parent account
3. Add children accounts
4. Configure your family's chore list and reward system

## Technical Architecture

- Backend: Python/Flask
- Database: PostgreSQL
- Frontend: Bootstrap CSS and Vanilla JavaScript
- Containerization: Docker & Docker Compose# ChoreTracker
