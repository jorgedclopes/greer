import logging
import os.path
import shutil

import docker

logging.basicConfig(level=logging.INFO)

file_name = 'prometheus.yml'
origin_file_path = './prometheus'
dest_path = '~/.prometheus'

grafana_origin = './grafana'
grafana_destination = '~/.grafana'


def main():
    setup_prometheus()
    setup_grafana()


def setup_grafana():
    this_root_dir = os.path.abspath(os.path.dirname(__file__))
    grafana_dest_dir = os.path.expanduser(grafana_destination)
    os.makedirs(
        grafana_dest_dir,
        exist_ok=True,
    )
    shutil.copytree(
        os.path.join(this_root_dir, grafana_origin),
        grafana_dest_dir,
        dirs_exist_ok=True,
    )


def setup_prometheus():
    this_root_dir = os.path.abspath(os.path.dirname(__file__))
    prometheus_dest_dir = os.path.expanduser(dest_path)
    shutil.rmtree(prometheus_dest_dir)
    os.makedirs(
        prometheus_dest_dir,
        exist_ok=True,
    )
    shutil.copytree(
        os.path.join(this_root_dir, origin_file_path),
        prometheus_dest_dir,
        dirs_exist_ok=True,
    )
    try:
        client = docker.from_env()
        client.containers.get('prometheus').restart()
    except Exception as e:
        logging.warning(e)
        pass


if __name__ == '__main__':
    main()
