docker build  -t flask_dev -f Dockerfile . && docker run -p 5000:5000 --volume=$(pwd):/www flask_dev
