from core.ssh_manager import SSHManager
from core.server_detector import ServerDetector


HOST = "192.168.1.101"
PORT = 45891

USERNAME = "tester"
PASSWORD = "123456789"


def main():

    ssh = SSHManager(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
    )

    ssh.connect()

    detector = ServerDetector(ssh)

    info = detector.detect()

    print(info.model_dump())

    ssh.disconnect()


if __name__ == "__main__":
    main()