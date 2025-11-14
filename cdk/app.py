#!/usr/bin/env python3
import aws_cdk as cdk
from mortgage_stack import MortgageStack

app = cdk.App()
MortgageStack(app, "MortgageEligibilityStack")
app.synth()
