# Define global args
ARG FUNCTION_DIR="/function"

# Start the build stage
FROM public.ecr.aws/amazonlinux/amazonlinux:2023 AS build-image

# Arguments for function directory
ARG FUNCTION_DIR

# Install git and libraries
RUN yum install -y git libffi-devel openssl-devel bzip2-devel python3 python3-pip

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

# Clone the git repository
RUN git clone https://github.com/sinanartun/binance_5.git .

# Set the ownership
RUN chown -R root:root ${FUNCTION_DIR}

# Change the permissions
RUN chmod 2775 ${FUNCTION_DIR} && find ${FUNCTION_DIR} -type d -exec chmod 2775 {} \;

# Install the required packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the updated script
COPY kin_lambda.py ./kin.py

# Start a new build stage so we can minimise the final image size
FROM public.ecr.aws/lambda/python:3.9

# Arguments for function directory
ARG FUNCTION_DIR

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set the CMD to your handler
CMD [ "kin.handler" ]
