<!-- # CI-CD Flask App
CI-CD Flask Application with Docker, Kubernetes and Github Actions
<div id="top"></div>


 -->

<!-- PROJECT LOGO -->
<br />
<div align="center">

<h1 align="center">CI-CD Flask App</h1>

  <p align="center">
    Flask Application with a CI/CD pipline using Docker, Kubernetes and Github Actions
   <br />
</div>






<!-- ABOUT THE PROJECT -->
## About The Project

This is basic Flask Application developed in python, <br>
That has an integrated CI/CD pipeline built with 
`Docker` to build the image from the `Flask` application, and `Kubernetes` to deploy the Docker image to a kubernetes cluster, hosted in `Azure` using `Azure Kubernetes Services` <br>
Where the workflow was set up through the use of `Github Actions` devOps feature.

### Built With

* [Docker](https://www.docker.com/)
* [Kubernetes](https://kubernetes.io/)
* [Github Actions](https://github.com/features/actions/)
* [Azure Kubernetes Services](https://azure.microsoft.com/en-us/services/kubernetes-service/)
* [Flask](https://flask.palletsprojects.com/en/2.0.x/)
<!-- GETTING STARTED -->
## Project Structure

* **Dockerfile**: this file is used to build the docker container
* **manifests/:** under this folder we have all our our deployment and services YAML files used for kubernetes deployment
* ****.github/workflows/CI-CD-Action.yml:**** is the Actions file containing the steps of the github actions to build and deploy the docker image from the flask application to the kubernetes cluster in AKS
