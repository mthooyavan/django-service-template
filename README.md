# Django Service Template

This is a Django-based web application template designed to provide a strong starting point for new projects. It includes a set of common functionalities like user registration and authentication, email communication, and more.

## Prerequisites

- Python 3.8+
- Docker
- Docker Compose
- Git

### Installation Instructions

**Docker**:

- **Mac**: Download Docker Desktop for Mac from [here](https://hub.docker.com/editions/community/docker-ce-desktop-mac/) and follow the installation guide.
- **Ubuntu**: Follow the instructions [here](https://docs.docker.com/engine/install/ubuntu/).
- **Red Hat**: Follow the instructions [here](https://docs.docker.com/engine/install/centos/).
- **Windows**: Download Docker Desktop for Windows from [here](https://hub.docker.com/editions/community/docker-ce-desktop-windows/) and follow the installation guide.

**Docker Compose**:

- **Mac**: Docker Compose is included as part of the Docker Desktop installation.
- **Ubuntu**: Follow the instructions [here](https://docs.docker.com/compose/install/).
- **Red Hat**: Follow the instructions [here](https://docs.docker.com/compose/install/).
- **Windows**: Docker Compose is included as part of the Docker Desktop installation.

**Git**:

- **Mac**: Install using Homebrew: `brew install git`
- **Ubuntu**: Install using apt: `sudo apt-get install git`
- **Red Hat**: Install using yum: `sudo yum install git`
- **Windows**: Download Git for Windows from [here](https://gitforwindows.org/) and follow the installation guide.

**Setting Up SSH Access for GitHub**:

- Generate a new SSH key (or skip this step if you already have a key). In Terminal, paste the text below, substituting in your GitHub email address: `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
- Start the ssh-agent in the background: `eval "$(ssh-agent -s)"`
- Add your SSH key to the ssh-agent: `ssh-add ~/.ssh/id_rsa`
- Add the SSH key to your GitHub account. Follow the instructions [here](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account).

## Internationalization (i18n) and Auto-translation

We've added support for internationalization (i18n). Along with that, we've included a custom script for auto-translation using Google Translate. To ensure the translations are up-to-date, developers should:

1. **Get Google Translate API Key**:
    - Before performing translations, obtain the Google Translate API key from the Google Cloud Platform.
    - Add the API key to the project in the file named `credential_gcp.json` and add `GOOGLE_APPLICATION_CREDENTIALS=credential_gcp.json` to the `.env` file.
    - Place this file in the project root directory right after cloning the project. If this step is skipped, you might encounter an error from Docker indicating that the file is missing.

2. **Update Translation Messages**:
    - Whenever you add new text that supports translation, run:
        ```shell
        make makemessages
        ```

3. **Compile Messages**:
    - After updating the translation messages, run:
        ```shell
        make compilemessages
        ```

## Getting Started

1. **Clone the repository**:
    ```shell
    git clone https://github.com/<username>/<repo>.git
    ```

2. **Change the project name**:
    The Django project name is currently `backend_service`. If you wish to change the name, you'll need to refactor it in all the relevant places:
    - Rename the `backend_service` directory to your new project name.
    - In the settings file (`backend_service/settings.py`), update the `ROOT_URLCONF` and `WSGI_APPLICATION` variables to your new project name.
    - In the `asgi.py` and `wsgi.py` files, rename the `backend_service` module to your new project name.
    - In the Dockerfile and docker-compose.yml files, update any references to `backend_service` to your new project name.
    - In the Makefile, update any references to `backend_service` to your new project name.
    - In the `tests` directory, update any imports from `backend_service` to your new project name.
    - In the `.github/workflows` directory, update any references to `backend_service` to your new project name.
    - In the `manage.py` file, update the `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_service.settings.production')` line to your new project name.

3. **Create a .env file**:
    After cloning the repository, you need to create a .env file in the project root directory to store all environment variables. The required environment variables are:
    - `POSTGRES_USER`: The username for the PostgreSQL database.
    - `POSTGRES_PASSWORD`: The password for the PostgreSQL database.
    - `POSTGRES_DB`: The name of the PostgreSQL database.
    - `POSTGRES_PORT`: The port of the PostgreSQL database.
    - `PRIMARY_POSTGRES_HOST`: The host of the Primary PostgreSQL database.
    - `PRIMARY_POSTGRES_PORT`: The port of the Primary PostgreSQL database.
    - `SECONDARY_POSTGRES_HOST`: The host of the Secondary PostgreSQL database.
    - `SECONDARY_POSTGRES_PORT`: The port of the Secondary PostgreSQL database.
    - `REDIS_URL`: The URL for the Redis instance.
    - `APP_PORT`: The port on which the Django app will run.

4. **Build the Docker image**:
    ```shell
    make build
    ```

5. **Database Migrations**:
    Before starting the application, you need to apply the database migrations. To create the migrations, use the following command:
    ```shell
    make makemigrations
    ```
    To apply these migrations, use the following command:
    ```shell
    make migrate
    ```

6. **Create a Django superuser**:
    To create a Django superuser, use the following command:
    ```shell
    docker-compose run --rm web python manage.py createsuperuser
    ```

7. **Run the application**:
    ```shell
    make start
    ```

## Docker Commands

Here are some basic Docker commands that might be useful when developing this project:

- `docker ps`: Lists all running Docker containers.
- `docker ps -a`: Lists all Docker containers, including those that are not running.
- `docker images`: Lists all Docker images.
- `docker logs <container_name>`: Shows the logs for a specific container.
- `docker logs -f <container_name>`: Shows the logs for a specific container and follows them.
- `docker exec -it <container_name> /bin/bash`: Opens a bash shell in a specific container.
- `docker exec -it <container_name> sh`: Opens a sh shell in a specific container.
- `docker rm <container_name>`: Removes a specific container.
- `docker rmi <image_name>`: Removes a specific image.
- `docker stop <container_name>`: Stops a specific container.

## PostgreSQL Commands

Here are some basic PostgreSQL commands that might be useful when developing this project:

- `\l`: Lists all databases.
- `\c <database_name>`: Connects to a specific database.
- `\dt`: Lists all tables in the current database.
- `\d <table_name>`: Shows the structure of a specific table.
- `SELECT * FROM <table_name>;`: Selects all records from a specific table.

## Development Commands

The Makefile includes several commands that simplify the development process:

- `make start`: Starts the Docker containers for the application and displays the logs.
- `make down`: Stops and removes the Docker containers.
- `make build`: Builds the Docker images for the application.
- `make clean`: Removes unused Docker objects.
- `make deps`: Compiles the Python dependencies.
- `make migrate`: Applies Django database migrations.
- `make makemigrations`: Creates new Django database migrations.
- `make mergemigrations`: Merges existing Django database migrations.
- `make console`: Opens a Django shell.
- `make celery-worker`: Starts a Celery worker.
- `make celery-worker-beat`: Starts a Celery worker with beat.
- `make test-local`: Runs the tests locally.
- `make test`: Runs the tests inside a Docker container.
- `make lint-local`: Runs the linter locally.
- `make lint`: Runs the linter inside a Docker container.
- `make security-local`: Runs a security check locally.
- `make security`: Runs a security check inside a Docker container.

## Testing

To run the unit tests, use the following command:
```shell
make test
```

## Linting

To run the linter, use the following command:
```shell
make lint
```

## Security

To run a security check, use the following command:
```shell
make security
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License. See the LICENSE.md file for details.

## Acknowledgments

This project was created as a service template for Django applications.
