from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "InfrastructureQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        get__best_matches = aws_lambda.Function(
        self, "GetBestMatches",
        runtime=aws_lambda.Runtime.PYTHON_3_8,
        handler="app.match_artists_handler",
        code=aws_lambda.Code.from_asset("../compute")
    )