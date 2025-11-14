from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    Duration,
    CfnOutput,
    RemovalPolicy
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

        # S3 bucket for static web hosting
        web_bucket = s3.Bucket(
            self, "WebBucket",
            bucket_name=f"mortgage-eligibility-web-{self.account}-{self.region}",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Deploy static web files to S3
        s3deploy.BucketDeployment(
            self, "WebDeployment",
            sources=[s3deploy.Source.asset("../static-web")],
            destination_bucket=web_bucket
        )

        # CloudFront distribution for the web app
        distribution = cloudfront.Distribution(
            self, "WebDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(web_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )

        # Output URLs
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "WebsiteUrl", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "S3WebsiteUrl", value=web_bucket.bucket_website_url)
