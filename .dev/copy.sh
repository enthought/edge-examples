# Copy ci, bootstrap.py, and README across all example dirs.
# Also updates a subset of these files in edge-native-base.

cp -r base-files/* ../example-dashboard
cp -r base-files/* ../example-flask
cp -r base-files/* ../example-panel
cp -r base-files/* ../example-plotly-dash
cp -r base-files/* ../example-streamlit

cp -r base-files/ci/* edge-native-base/ci
cp -r base-files/bootstrap.py edge-native-base/bootstrap.py