# Run the application
To run the Streamlit application, run the following command:

```console
docker run -d --rm --publish 8501:8501 --name my_streamlit_app docker pull theodorecurtil/streamlit_dashboard_101:linux_amd64
```

The application is now running on [http://localhost:8501/](http://localhost:8501/).

The image shipping the application is publicly available on [Docker Hub - theodorecurtil](https://hub.docker.com/u/theodorecurtil).