# Note Taking App

## Local Setup

## CICD Pipeline - proposed design

## Cloud Infrastructure (GCP) - proposed design

### Overview

The cloud infrastructure was designed with the possibility of further expansion and scaling of the project. Most choices were made to prefer cloud native solutions and to make use of managed services as much as possible. The project could be significantly simplified if no further functionality or security is needed (e.g.: it is just a P.O.C. or a simple backend of an in-house tool) as everything could be fitted into a single project without any Networking or Logging, but generally preparing for increased complexity down the road is advised.

### General Design
![architecture](diagrams/Cloud_Infrastructure.drawio.png)

The simplified design diagram of the Cloud Infrastructure can be seen above. The Infrastructure uses a multi-project setup to clearly separate responsibilities in a clear and easy to understand manner. Further separation can be achieved with utilizing the Folders resource of Google Cloud and projects can be split into dev, staging and prod environments (or a separate organization with a mirrored architecture can be created but usually it is good practice to keep all things in one organization to avoid user-management, logging and monitoring overhead). Access to resources can be managed by IAM role based access and for external agents (e.g.: CICD pipeline workers) with Service Accounts.

For Security and reproducibility purposes it should be generally advised to interact with the Environment via Automated CI/CD pipelines and IaC (e.g.: terraform) tools so certain principles can be enforced and changed can be easily traced. Manual modification should only happen in special cases and preferably should be documented.

Pipelines can be authenticated through Service Accounts with Workload Identity Federation which would allow the creation of short/lived tokens which behave similarly to SA keys but no key management is required.

#### API architecture
The API architecture encompasses only a few resources as sufficient performance can be easily achieved with managed services. Here, we have 2 important projects which host 2 crucial parts of our application: *API project* and *Database project*. the *API project* host the resources needed for the API functionality and the *Database project* hosts the PostgreSQL. I chose to separate them so if other services being implemented which require SQL database, they can be handled in one place logically, so no separate logging and networking apparatus will have to be developed.

The API itself is chosen to be hosted on a Cloud Run instance. It is the simplest resource to use when we want to migrate our local Python API to the cloud as it also uses Docker images, it scales automatically and is managed by Google. So deploying our local code can happen practically without any modification. Other services like Cloud Engine or GKE would introduce significant operational overhead while not saving significant amount of money. Firebase was also considered but since it's also utilizes Cloud Run instances and it is technically a separate service from GCP with its own SDK and Console, it was rejected.

The Cloud Run instance itself while presented in the VPC network, is technically visible on the public internet as public invocations are expected but if the app will be used by a separate cloud service later on, it can be also made private by getting rid of the Public IP. The Cloud Run has an API Gateway in front of it which manages traffic, provides the possibility to use a custom url and handles load balancing. API Gateway was chosen because it is a lightweight API manager which can use multiple different GCP services and quick to setup. Apigee would be pricey and way to complex to the current scale and API Endpoints is considered outdated and in "legacy mode" by Google.

#### Database
Database was chosen to be a Cloud SQL Google managed Postgres instance. While it can be a bit expensive, no solution seem to be ideal from this POW and the benefits of Cloud SQL like easy setup, Role Based access instead of the necessity of key management, Ability to create backups and easy to setup multi-zone databases outweighs its problems. Authentication from the Cloud Run instance to the Cloud SQL happens via IAM Authentication which allows to Authenticate into to Postgres through a Cloud Run Service Account with IAM roles and short-lived OAuth 2.0 tokens, and Key and secret management can be skipped. If this is not sufficient due to some security requirements, GCP native Secret Manager and Key Management should be enough.

#### Networking
A networking setup is not strictly required for this project as GCP managed services and role base access allows the services to communicate between each other. But for security reasons and for preparation for further workloads being deployed in our Infrastructure, a preliminary network was designed.

The structure of the network was chosen to be the classic Hub-and-Spoke model for its flexibility and high security. It is a bit complex to setup but if deployment is sufficiently automated, it should not be a serious concern.

The entire organization is surrounded by a VPC perimeter in order to avoid data filtration. Only out facing appliances like API gateway and Cloud Run can communicate with the public internet. All traffic goes trough a Hub network and traffic is managed by firewall rules.

#### Logging
Logging is handled in a dedicated project where all logs are collected in dedicated log buckets. In this way, querying and analyzing logs is much easier. From here, logs can be passed to a Pub/Sub topic and be sent over to external log analyzing systems like Splunk or Grafana.