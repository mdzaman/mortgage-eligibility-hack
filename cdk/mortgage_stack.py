from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Duration,
    CfnOutput
)
from constructs import Construct

class MortgageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function with X-Ray tracing
        mortgage_lambda = _lambda.Function(
            self, "MortgageLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("../genai-mortgage-hack"),
            timeout=Duration.seconds(30),
            memory_size=512,
            tracing=_lambda.Tracing.ACTIVE
        )

        # API Gateway with logging, tracing, and no caching
        api = apigw.RestApi(
            self, "MortgageApi",
            rest_api_name="Mortgage Eligibility API",
            description="Serverless mortgage eligibility engine",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
                allow_credentials=False
            ),
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                logging_level=apigw.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True,
                tracing_enabled=True,
                caching_enabled=False,
                cache_ttl=Duration.seconds(0),
                cache_data_encrypted=False,
                cache_cluster_enabled=False
            )
        )

        # Lambda integration with no caching
        lambda_integration = apigw.LambdaIntegration(
            mortgage_lambda,
            cache_key_parameters=[],
            cache_namespace=None
        )

        # API routes with explicit cache disabling
        # Add GET method to root
        api.root.add_method("GET", lambda_integration,
            method_responses=[apigw.MethodResponse(
                status_code="200",
                response_parameters={
                    "method.response.header.Cache-Control": True,
                    "method.response.header.Pragma": True,
                    "method.response.header.Expires": True
                }
            )]
        )

        # Add HEAD method to root (fixes 403 errors)
        api.root.add_method("HEAD", lambda_integration,
            method_responses=[apigw.MethodResponse(
                status_code="200",
                response_parameters={
                    "method.response.header.Cache-Control": True,
                    "method.response.header.Pragma": True,
                    "method.response.header.Expires": True
                }
            )]
        )

        # /api routes (for frontend compatibility)
        api_resource = api.root.add_resource("api")

        evaluate = api.root.add_resource("evaluate")
        evaluate.add_method("POST", lambda_integration)
        evaluate.add_method("HEAD", lambda_integration)

        api_evaluate = api_resource.add_resource("evaluate")
        api_evaluate.add_method("POST", lambda_integration)
        api_evaluate.add_method("HEAD", lambda_integration)

        presets = api.root.add_resource("presets")
        presets.add_method("GET", lambda_integration)
        presets.add_method("HEAD", lambda_integration)

        api_presets = api_resource.add_resource("presets")
        api_presets.add_method("GET", lambda_integration)
        api_presets.add_method("HEAD", lambda_integration)

        # Output API URL
        CfnOutput(self, "ApiUrl", value=api.url)
