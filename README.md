# powertools-oas-validator
<br><a href="https://badge.fury.io/py/powertools-oas-validator"><img src="https://badge.fury.io/py/powertools-oas-validator.svg" alt="PyPI version"></a>  ![CI](https://github.com/RasmusFangel/powertools-oas-validator/workflows/CI/badge.svg) <img src="https://coveralls.io/repos/RasmusFangel/powertools-oas-validator/badge.svg?branch=main" alt="Coveralls"></a>

## Introduction

[Powertools for AWS Lambda (Python)](https://github.com/aws-powertools/powertools-lambda-python) is an awesome set of tools for supercharging your lambdas. Powertools supports validating incoming requests (or event in PT lingo) against [JSONSchema](https://json-schema.org/) which is not ideal if you are using OpenAPI schemas to define your API contracts.

The *Powertools OAS Validator* adds a decorator that you can use with your lambda handlers and have the events validated against an OpenAPI schema instead.


## Installation
Poetry:
`poetry add powertools-oas-validator`

Pip:
`pip install powertools-oas-validator`


## Usage
Decorate your functions with `@validate_request(oas_path="openapi.yaml")` and your request/event (and schema) will be validated on a request.


### Minimal Example

```python
from typing import Dict
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from powertools_oas_validator.middleware import validate_request


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


Example of a `SchemaValidatonError`:
```python
from aws_lambda_powertools.utilities.validation import SchemaValidationError

SchemaValidatonError(
  name="test-path.test-endpoint.requestBody[param_1]",
  path=["test-path", "test-endpoint", "requestBody", "param_1"],
  validation_message="'not an integer' is not of type 'integer'.",
  message="'not an integer' is not of type 'integer'",
  rule="int",
  rule_definition="type",
  value="'not an integer'"
)
```

### Articles
- [OpenAPI Spec and AWS Lambda Powertools](https://medium.com/@rasmusfangel/openapi-spec-and-aws-lambda-powertools-aa9e63f579d1)


## Know Issues
While all validation errors are caught, there is only limited information about the various errors. The decorator will try its best to throw a `SchemaValidatonError`
(same as the Powertools validator would), with as much of the optional attributes as possible.

In summary, it is possible that not all `SchemaValidationErrors`'s will have the correct name and path attributes.


## Contributions
Please make a pull request and I will review it ASAP.
