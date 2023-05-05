import os
import signal
import subprocess

def run():
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    cmd = ["supervisord", "-c", "./dev/supervisord.conf"]
    try:
        process = subprocess.Popen(cmd, env=env, cwd=cwd)
        process.wait()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGTERM)


if __name__ == "__main__":
    run()
