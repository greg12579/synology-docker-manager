# Synology Docker Manager

A beautiful web interface for managing Docker containers on your Synology NAS with AI-powered container descriptions.

## Features

- 🐳 **Container Management**: Start, stop, restart, and update Docker containers
- 🤖 **AI-Powered Descriptions**: Automatically generate container descriptions using Claude AI
- 🌐 **Web Interface**: Clean, modern interface accessible at port 80
- 🔗 **URL Detection**: Automatically detects and displays container URLs with ports
- 📊 **Real-time Status**: View running containers, their ports, and status at a glance
- ♻️ **Auto-refresh**: Page automatically refreshes every 30 seconds
- 🎨 **Responsive Design**: Works on desktop and mobile devices

## Screenshots

The interface displays:
- Container name and status
- AI-generated description of what the application does
- Container image
- Accessible URLs with ports
- Port mappings (host → container)
- Action buttons (Start/Stop/Restart/Update)

## Requirements

- Synology NAS with Docker installed
- (Optional) Anthropic API key for AI-generated descriptions

## Installation

### 1. Clone or Download

Clone this repository or download it to your Synology NAS.

### 2. Configure Environment (Optional)

If you want AI-generated descriptions, create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Get your API key from: https://console.anthropic.com/

### 3. Deploy on Synology

#### Option A: Using Docker Compose (Recommended)

1. Upload the project folder to your Synology (e.g., `/volume1/docker/synology-docker-manager`)

2. SSH into your Synology:
   ```bash
   ssh admin@192.168.1.5
   ```

3. Navigate to the project directory:
   ```bash
   cd /volume1/docker/synology-docker-manager
   ```

4. Build and start the container:
   ```bash
   docker-compose up -d --build
   ```

#### Option B: Using Docker CLI

1. Build the image:
   ```bash
   docker build -t synology-docker-manager .
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name synology-docker-manager \
     -p 80:80 \
     -v /var/run/docker.sock:/var/run/docker.sock:ro \
     -e ANTHROPIC_API_KEY=your-key-here \
     --restart unless-stopped \
     synology-docker-manager
   ```

#### Option C: Using Synology Docker GUI

1. Build the image first using SSH (see Option B, step 1)
2. Open Synology **Docker** package
3. Go to **Container** → **Create** → **Choose Image**
4. Select `synology-docker-manager`
5. Configure:
   - **Port Settings**: Host Port 80 → Container Port 80
   - **Volume Settings**: Add `/var/run/docker.sock` (read-only) → `/var/run/docker.sock`
   - **Environment**: Add `ANTHROPIC_API_KEY` if desired
6. Apply and start the container

### 4. Access the Interface

Open your browser and navigate to:
```
http://192.168.1.5
```

## Usage

### Container Actions

- **Start**: Start a stopped container
- **Stop**: Stop a running container (requires confirmation)
- **Restart**: Restart a container (requires confirmation)
- **Update**: Pull the latest image and recreate the container (requires confirmation)
- **Regenerate Description**: Force AI to regenerate the container description

### AI Descriptions

The app automatically generates descriptions for containers that don't have one. Descriptions are generated based on:
- Container name
- Docker image name

To manually trigger description regeneration, click the "🤖 Regenerate Description" button.

**Note**: Container labels cannot be updated while running. Generated descriptions will be shown immediately but stored in labels only when the container is recreated.

### Manual Descriptions

You can manually add descriptions to your containers by adding a label when creating them:

```bash
docker run -d \
  --label app.description="My custom description" \
  your-image
```

Or in docker-compose.yml:

```yaml
services:
  myapp:
    image: myapp:latest
    labels:
      - "app.description=My custom description"
```

## API Endpoints

The app provides a REST API for programmatic access:

- `GET /api/containers` - List all containers
- `POST /api/container/<id>/start` - Start a container
- `POST /api/container/<id>/stop` - Stop a container
- `POST /api/container/<id>/restart` - Restart a container
- `POST /api/container/<id>/update` - Update a container
- `POST /api/container/<id>/regenerate-description` - Regenerate AI description

## Security Considerations

- The app requires access to `/var/run/docker.sock` to manage containers
- Port 80 is exposed - ensure your Synology firewall is configured appropriately
- Consider using a reverse proxy with authentication for production use
- API key is stored in environment variables - keep `.env` file secure

## Troubleshooting

### Port 80 Already in Use

If port 80 is already used by another service, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Change host port to 8080
```

Then access at: `http://192.168.1.5:8080`

### Cannot Connect to Docker Socket

Ensure the Docker socket is mounted correctly:
```bash
docker inspect synology-docker-manager | grep -A 10 Mounts
```

### AI Descriptions Not Working

1. Check that your API key is set correctly in `.env`
2. Verify the container has the environment variable:
   ```bash
   docker exec synology-docker-manager env | grep ANTHROPIC
   ```
3. Check container logs:
   ```bash
   docker logs synology-docker-manager
   ```

## Development

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Access at `http://localhost:80`

### Modifying the UI

- HTML templates: `templates/index.html`
- CSS styles: `static/css/style.css`
- JavaScript: `static/js/main.js`

## License

MIT License - feel free to modify and use as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Roadmap

- [ ] Container logs viewer
- [ ] Docker Compose stack management
- [ ] Image management (pull, remove, build)
- [ ] Volume and network management
- [ ] Container resource usage (CPU, memory)
- [ ] Authentication and user management
- [ ] Webhook notifications
- [ ] Container health checks
- [ ] Backup and restore functionality

## Credits

Built with:
- Flask (Python web framework)
- Docker SDK for Python
- Anthropic Claude API (AI descriptions)
- Modern CSS and vanilla JavaScript
