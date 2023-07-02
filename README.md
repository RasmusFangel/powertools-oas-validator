# powertools-oas-validator
<br>[![PyPI version](https://badge.fury.io/py/powertools-oas-validator.svg)](https://pypi.org/project/powertools-oas-validator/) ![Release](https://github.com/RasmusFangel/powertools-oas-validator/workflows/Release/badge.svg) ![CI](https://github.com/RasmusFangel/powertools-oas-validator/workflows/CI/badge.svg)

## Introduction

[Powertools for AWS Lambda (Python)](https://github.com/aws-powertools/powertools-lambda-python) is an awesome set of tools for supercharging your lambdas. Powertools supports validating incoming requests (or event in PT lingo) against [JSONSchema](https://json-schema.org/) which is not ideal if you are using OpenAPI schemas to define your API contracts.

The *Powertools OAS Validator* adds a decorator that you can use with your lambda handlers and have the events validated against an OpenAPI schema instead.


## Usage
Decorate your functions with `@validate_request(oas_path="openapi.yaml")` and your request/event (and schema) will be validated on a request.


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

## Error Handling
If the validation fails, the decorator throws a `SchemaValidatonError` with relevant information about the failed validation.


## Know Issues
While all validation errors are caught, there is only limited information about the various errors. The decorator will try its best to throw a `SchemaValidatonError`
(same as the Powertools validator would), with as much of the optional attributes as possible.

In summary, it is possible that not all `SchemaValidationErrors`'s will have a nice validation message, in case you rely on piping it straight back to the client.


## Contributions
Please make a pull request and I will review it ASAP.
