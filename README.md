# Naturalien

### Prerequisites

#### Local installation

- pyenv
- poetry
- docker
- [pyodbc](https://learn.microsoft.com/en-us/azure/azure-sql/database/azure-sql-python-quickstart?view=azuresql&tabs=windows%2Csql-inter)

#### Azure Resources

The azure resources are configured following [this guide](https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container?tabs=azure-cli&pivots=container-linux).

- Azure SQL Database
- Azure Web App
- Azure Container Registry

### How to run

You will need the following environment variables

- AZURE_SQL_CONNECTIONSTRING: The connection string to your Azure SQL Database. For local development one can use [connection without access token](https://docs.sqlalchemy.org/en/14/dialects/mssql.html#connecting-to-databases-with-access-tokens) together with [azure sql passwordless](https://learn.microsoft.com/en-us/azure/azure-sql/database/azure-sql-passwordless-migration-python?view=azuresql&tabs=sign-in-visual-studio-code%2Cazure-portal-create%2Cazure-portal-assign%2Capp-service-identity). For local development using docker one needs a [username and password](https://docs.sqlalchemy.org/en/14/dialects/mssql.html#dialect-mssql-pyodbc-connect). For creating a new local database instead to connecting to the Azure SQL Database one can use `sqlite:///database.db`.
- STREAMLIT_PASSWORD: Custom password to access the streamlit app

#### Without Docker

```bash
poetry install
poetry run python -m streamlit run naturalien/app.py
```

#### With Docker

You will need the additional environment variables:

- ACR_URL: The URL pointing to your Azure Container Registry
- IMAGE_NAME: The name of the image you want to build

```bash
docker build --tag $ACR_URL/$IMAGE_NAME .
docker run -p 8080:8080 -e AZURE_SQL_CONNECTIONSTRING=$AZURE_SQL_CONNECTIONSTRING -e STREAMLIT_PASSWORD=$STREAMLIT_PASSWORD $ACR_URL/$IMAGE_NAME
```

For deployment just run:

```bash
docker push $ACR_URL/$IMAGE_NAME
```
