from click import echo, secho


def debug(msg): secho(f'[ ] {msg}', dim=True, err=True)
def info(msg): echo(f'[*] {msg}', err=True)
