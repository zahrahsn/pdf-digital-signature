# pdf-digital-signature
A Django-based PDF signing/verifying platform.

**How to run**:
 - Create an `.env` file containing following values:
 ```
CA_COUNTRY=<...>
CA_PROVINCE=<...>
CA_CITY=<...>
CA_ORG=<...>
CA_DOMAIN=<...>
CA_PASSPHRASE=<...>

SQL_HOST=db
SQL_PORT=5432
POSTGRES_HOST_AUTH_METHOD=trust
POSTGRES_USER=postgres
POSTGRES_PASS=<db pass>

SUPERUSER_USERNAME=<...>
SUPERUSER_PASS=<...>
SUPERUSER_EMAIL=<...>
 ```
 - Then run:
`docker compose up`
