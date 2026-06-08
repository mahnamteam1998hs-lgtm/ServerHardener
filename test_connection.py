from core.ssh_manager import SSHManager

HOST = "192.168.1.101"
PORT = 22

USERNAME = "tester"
PASSWORD = "123456789"


def main():
    ssh = SSHManager(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
    )

    try:
        print("Connecting...")

        ssh.connect()

        print("Connected")

        output, error, exit_code = ssh.execute(
            "hostname"
        )

        print(f"Output: {output}")
        print(f"Error: {error}")
        print(f"Exit Code: {exit_code}")

    finally:
        ssh.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    main()