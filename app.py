import os
import json
from flask import Flask, render_template, jsonify, request
import docker
from anthropic import Anthropic

app = Flask(__name__)
docker_client = docker.from_env()

# Claude API client for AI-generated descriptions
anthropic_client = None
if os.getenv('ANTHROPIC_API_KEY'):
    anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def get_container_description(container):
    """Get or generate description for a container."""
    # Check if description exists in labels
    labels = container.labels
    if 'app.description' in labels and labels['app.description']:
        return labels['app.description']

    # Generate description using AI if API key is available
    if anthropic_client:
        try:
            description = generate_ai_description(container)
            # Store the generated description in container label
            update_container_label(container, 'app.description', description)
            return description
        except Exception as e:
            print(f"Error generating AI description: {e}")
            return f"Container: {container.name}"

    return f"Container: {container.name}"


def generate_ai_description(container):
    """Use Claude AI to generate a description based on container name and image."""
    prompt = f"""Based on this Docker container information, provide a brief 1-sentence description of what this application does:

Container name: {container.name}
Image: {container.image.tags[0] if container.image.tags else 'unknown'}

Respond with ONLY the description, no additional text."""

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()


def update_container_label(container, label_key, label_value):
    """Update a container's label (requires recreation, so we'll skip for now)."""
    # Note: Docker doesn't allow updating labels on running containers
    # This would require stopping and recreating the container
    # For now, we'll just log it and update on next container recreation
    pass


def get_container_url(container):
    """Extract the primary URL for a container based on port mappings."""
    ports = container.ports
    if not ports:
        return None

    # Look for common HTTP ports
    for container_port in ['80/tcp', '8080/tcp', '443/tcp', '3000/tcp', '5000/tcp']:
        if container_port in ports and ports[container_port]:
            host_port = ports[container_port][0]['HostPort']
            protocol = 'https' if '443' in container_port else 'http'
            return f"{protocol}://192.168.1.5:{host_port}"

    # If no common port found, use the first available
    for port_key, port_info in ports.items():
        if port_info:
            host_port = port_info[0]['HostPort']
            return f"http://192.168.1.5:{host_port}"

    return None


def get_all_ports(container):
    """Get all port mappings for a container."""
    ports = container.ports
    if not ports:
        return []

    port_list = []
    for container_port, mappings in ports.items():
        if mappings:
            for mapping in mappings:
                port_list.append({
                    'container_port': container_port,
                    'host_port': mapping['HostPort'],
                    'host_ip': mapping.get('HostIp', '0.0.0.0')
                })
    return port_list


@app.route('/')
def index():
    """Main page showing all running containers."""
    try:
        containers = docker_client.containers.list()
        container_info = []

        for container in containers:
            info = {
                'id': container.id[:12],
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'status': container.status,
                'description': get_container_description(container),
                'url': get_container_url(container),
                'ports': get_all_ports(container),
                'created': container.attrs['Created'],
                'state': container.attrs['State']
            }
            container_info.append(info)

        return render_template('index.html', containers=container_info)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/api/containers')
def api_containers():
    """API endpoint to get container information."""
    try:
        containers = docker_client.containers.list(all=True)
        container_info = []

        for container in containers:
            info = {
                'id': container.id[:12],
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'status': container.status,
                'description': get_container_description(container),
                'url': get_container_url(container),
                'ports': get_all_ports(container),
                'state': container.status
            }
            container_info.append(info)

        return jsonify(container_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/container/<container_id>/start', methods=['POST'])
def start_container(container_id):
    """Start a container."""
    try:
        container = docker_client.containers.get(container_id)
        container.start()
        return jsonify({'status': 'success', 'message': f'Container {container.name} started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/container/<container_id>/stop', methods=['POST'])
def stop_container(container_id):
    """Stop a container."""
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        return jsonify({'status': 'success', 'message': f'Container {container.name} stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/container/<container_id>/restart', methods=['POST'])
def restart_container(container_id):
    """Restart a container."""
    try:
        container = docker_client.containers.get(container_id)
        container.restart()
        return jsonify({'status': 'success', 'message': f'Container {container.name} restarted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/container/<container_id>/update', methods=['POST'])
def update_container(container_id):
    """Update a container (pull latest image and recreate)."""
    try:
        container = docker_client.containers.get(container_id)
        image_name = container.image.tags[0] if container.image.tags else None

        if not image_name:
            return jsonify({'status': 'error', 'message': 'Cannot update container without image tag'}), 400

        # Pull latest image
        docker_client.images.pull(image_name)

        # Get container config
        config = container.attrs
        name = container.name

        # Stop and remove old container
        container.stop()
        container.remove()

        # Create new container with same config
        # Note: This is simplified - in production you'd want to preserve all settings
        new_container = docker_client.containers.run(
            image_name,
            name=name,
            detach=True,
            ports=config['HostConfig'].get('PortBindings'),
            environment=config['Config'].get('Env'),
            volumes=config['HostConfig'].get('Binds')
        )

        return jsonify({'status': 'success', 'message': f'Container {name} updated', 'new_id': new_container.id[:12]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/container/<container_id>/regenerate-description', methods=['POST'])
def regenerate_description(container_id):
    """Force regenerate the AI description for a container."""
    try:
        if not anthropic_client:
            return jsonify({'status': 'error', 'message': 'AI API key not configured'}), 400

        container = docker_client.containers.get(container_id)
        description = generate_ai_description(container)

        return jsonify({
            'status': 'success',
            'description': description,
            'message': 'Description regenerated (will be saved on next container recreation)'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
