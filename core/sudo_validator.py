def validate_sudo(ssh):

    output, error, exit_code = (
        ssh.execute_sudo(
            "sudo -n true && echo OK"
        )
    )

    return (
        exit_code == 0
        and "OK" in output
    )