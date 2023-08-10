ARG PACKAGE_NAME=datadoc
ARG APP_NAME=ssb_datadoc
ARG APP_PATH=/opt/$PACKAGE_NAME
ARG PYTHON_VERSION=3.11
ARG POETRY_VERSION=1.5.0

#
# Stage: build
#
FROM python:$PYTHON_VERSION as build
ARG PACKAGE_NAME
ARG APP_PATH
ARG POETRY_VERSION

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Import our project files
WORKDIR $APP_PATH
COPY ./poetry.lock ./pyproject.toml ./README.md ./
COPY ./$PACKAGE_NAME ./$PACKAGE_NAME

RUN poetry build --format wheel
RUN poetry export --format constraints.txt --output constraints.txt --without-hashes

#
# Stage: production
#
FROM python:"${PYTHON_VERSION}-slim" as production
ARG PACKAGE_NAME
ARG APP_PATH

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN useradd --create-home appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

# Get build artifact wheel and install it respecting dependency versions
WORKDIR $APP_PATH
COPY --from=build $APP_PATH/dist/*.whl ./
COPY --from=build $APP_PATH/constraints.txt ./
RUN pip install ./$APP_NAME*.whl --constraint constraints.txt

# export PACKAGE_NAME as environment variable for the CMD
ENV PACKAGE_NAME=$PACKAGE_NAME

CMD exec gunicorn --bind 0.0.0.0:8050 --workers 1 --threads 1 --timeout 0 "$PACKAGE_NAME.wsgi:server"
