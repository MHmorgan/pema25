from pathlib import Path

from click import echo, secho

outdir = Path('out')

def debug(msg):
    """Write a debug message to stderr"""
    secho(f'[ ] {msg}', dim=True, err=True)

def info(msg):
    """Write an info message to stderr"""
    echo(f'[*] {msg}', err=True)

def warn(msg):
    """Write a warning message to stderr"""
    echo(f'[!] {msg}', fg='yellow', err=True)

def err(msg):
    """Write an error message to stderr"""
    echo(f'[!] {msg}', fg='red', err=True)

