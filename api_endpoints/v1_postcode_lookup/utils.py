import os


def init_sentry():
    if sentry_dsn := os.environ.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=0,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                AwsLambdaIntegration(),
            ],
        )


# TODO: Add logging directly
# def init_logger(app):
#     FIREHOSE_ACCOUNT_ARN = os.environ.get("FIREHOSE_ACCOUNT_ARN", None)
#     if FIREHOSE_ACCOUNT_ARN:
#         firehose_args = {"assume_role_arn": FIREHOSE_ACCOUNT_ARN}
#     else:
#         firehose_args = {"fake": True}
#     app.state.POSTCODE_LOGGER = DCWidePostcodeLoggingClient(**firehose_args)
#     return app
