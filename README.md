# powertools-oas-validator
<br>[![PyPI version](https://badge.fury.io/py/powertools-oas-validator.svg)](https://pypi.org/project/powertools-oas-validator/) ![Build](https://github.com/RasmusFangel/powertools-oas-validator/workflows/Release/badge.svg) ![CI](https://github.com/RasmusFangel/powertools-oas-validator/workflows/CI/badge.svg)

## Introduction

[Powertools for AWS Lambda (Python)](https://github.com/aws-powertools/powertools-lambda-python) is an awesome set of tools for supercharging your lambdas. Powertools supports validating incoming requests (or event in PT lingo) against [JSONSchema](https://json-schema.org/) which is not ideal if you are using OpenAPI schemas to define your API contracts.

The *Powertools OAS Validator* adds a decorator that you can use with your lambda handlers and have the events validated against an OpenAPI schema instead.


## Usage
Decorate your functions with `@validate_request(oas_path="openapi.yaml")` and your request (and schema) will be validated on a request.

Schema validation is enabled per default but can be disabled if you already validate your schema (perhaps as part of a pipeline)

### Minimal Example

```python
from typing import Dict
from aws_lambda_powertools.event_handler import APIGatewayRestResolve, Rresponse
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.middleware import validate_request


app = APIGatewayRestResolver()

@app.post("/example")
def example() -> Response:
  ...

@validate_request(oas_path="openapi.yaml")
def lambda_handler(event: Dict, context: LambdaContext) -> Dict:
    response = app.resolve(event, context)

    return response
```


### Extended Example
```python
from typing import Dict
from aws_lambda_powertools.event_handler import APIGatewayRestResolve, Rresponse
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.middleware import validate_request


app = APIGatewayRestResolver()

@app.post("/example")
def example() -> Response:
  ...

@validate_request(
  oas_path="openapi.yaml",
  validate_spec=True,  # default True, disable to not validate OpenAPI Schema
  validate_body=True,  # default True, disable to not validate event["body"] 
  validate_headers=True,  # default True, disable to not validate event["headers"]
  validate_query=True,  # default True, disable to not validate event["rawQueryString"]
  validate_path=True,  # default True, disable to not validate path parameters
  validate_cookies=True, # default True, disable to not validate cookies

)
def lambda_handler(event: Dict, context: LambdaContext) -> Dict:
    response = app.resolve(event, context)

    return response
```

