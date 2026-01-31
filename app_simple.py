import os
import json
import subprocess
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


def run_docker_command(cmd):
    """Run a docker command and return the output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"Error running docker command: {e}")
        return None


def get_containers():
    """Get list of running containers."""
    cmd = 'docker ps --format "{{json .}}"'
    output = run_docker_command(cmd)

    if not output:
        return []

    containers = []
    for line in output.strip().split('\n'):
        if line:
            try:
                container_data = json.loads(line)
                containers.append(parse_container(container_data))
            except json.JSONDecodeError:
                continue

    return containers


def parse_container(data):
    """Parse container data and extract useful information."""
    name = data.get('Names', 'unknown')
    image = data.get('Image', 'unknown')
    ports = data.get('Ports', '')
    status = data.get('Status', '')
    container_id = data.get('ID', '')

    # Parse ports to get URLs
    port_mappings = parse_ports(ports)
    primary_url = get_primary_url(port_mappings)

    # Get description from labels
    description = get_container_description(container_id, name, image)

    return {
        'id': container_id[:12],
        'name': name,
        'image': image,
        'status': status,
        'description': description,
        'url': primary_url,
        'ports': port_mappings
    }


def parse_ports(ports_str):
    """Parse port string into structured data."""
    if not ports_str:
        return []

    port_list = []
    # Format: "0.0.0.0:8080->80/tcp, :::8080->80/tcp"
    for port_mapping in ports_str.split(', '):
        if '->' in port_mapping:
            parts = port_mapping.split('->')
            if len(parts) == 2:
                host_part = parts[0].strip()
                container_part = parts[1].strip()

                # Extract host port
                if ':' in host_part:
                    host_port = host_part.split(':')[-1]
                else:
                    host_port = host_part

                port_list.append({
                    'host_port': host_port,
                    'container_port': container_part
                })

    # Remove duplicates (IPv4 and IPv6 entries)
    seen = set()
    unique_ports = []
    for port in port_list:
        key = f"{port['host_port']}->{port['container_port']}"
        if key not in seen:
            seen.add(key)
            unique_ports.append(port)

    return unique_ports


def get_primary_url(port_mappings):
    """Get the primary URL for a container."""
    if not port_mappings:
        return None

    # Preferred ports in order
    preferred_ports = ['80', '8080', '443', '3000', '5000']

    for pref_port in preferred_ports:
        for mapping in port_mappings:
            if mapping['container_port'].startswith(pref_port + '/'):
                protocol = 'https' if pref_port == '443' else 'http'
                return f"{protocol}://192.168.1.5:{mapping['host_port']}"

    # If no preferred port, use the first one
    if port_mappings:
        host_port = port_mappings[0]['host_port']
        return f"http://192.168.1.5:{host_port}"

    return None


def get_container_description(container_id, name, image):
    """Get container description from labels or generate one."""
    # Try to get description from labels
    cmd = f"docker inspect {container_id} --format '{{{{json .Config.Labels}}}}'"
    output = run_docker_command(cmd)

    if output:
        try:
            labels = json.loads(output)
            if 'app.description' in labels and labels['app.description']:
                return labels['app.description']
        except json.JSONDecodeError:
            pass

    # Default description
    return f"Container: {name}"


@app.route('/')
def index():
    """Main page showing all running containers."""
    try:
        containers = get_containers()
        return render_template('index.html', containers=containers)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/api/containers')
def api_containers():
    """API endpoint to get container information."""
    try:
        containers = get_containers()
        return jsonify(containers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
