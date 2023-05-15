import shutil
import os.path as op
import os

HERE = op.abspath(op.dirname(__file__))

NAMES = [
    "example-dashboard",
    "example-flask",
    "example-panel",
    "example-plotly-dash",
    "example-streamlit",
]


def copyall():
    src = op.join(HERE, "ci-native-base")
    for name in names:
        dst = op.abspath(op.join(HERE, "..", name, "ci"))
        shutil.rmtree(dst)
        shutil.copytree(src, dst)


if __name__ == "__main__":
    copyall()
