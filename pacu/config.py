# Mostly a hack for now to avoid including uninteresting info.
# TODO: Find a better way to do this. Probably run against a fresh account, and make a blacklist
#  of what not to blacklist (like the default vpc).
blacklist = {
    "devicefarm": [
        "ListDevices",
        # network timeout (I think due to feature needing out of band enabling by AWS)
        "ListOfferingTransactions",
    ],
    "ec2": [
        # return way too much (unrelated) data
        "DescribeHostReservationOfferings",
        "DescribeImages",
        #"DescribeRegions",
        "DescribeReservedInstancesOfferings",
        "DescribeSnapshots",
        "DescribeSpotPriceHistory",
        # Always the same
        "DescribeInstanceTypes",
        "DescribeInstanceTypeOfferings",
        # Need to filter out public images
        "DescribeFpgaImages",
        # likely static
        "DescribeIdFormat",
        # need to filter out non-amazon endpoints
        "DescribeVpcEndpointServices",
    ],
    "elasticache": [
        # return way too much (unrelated) data
        "DescribeCacheEngineVersions",
        "DescribeReservedCacheNodesOfferings",
    ],
    "elasticbeanstalk": [
        # return way too much (unrelated) data
        "DescribeConfigurationOptions",
        "DescribeEnvironmentResources",
        "DescribePlatformVersion",
        "ListAvailableSolutionStacks",
        # Has useful info, but likely doesn't change per customer.
        "ListPlatformVersions",
    ],
    "elastictranscoder": [
        # return way too much (unrelated) data
        "ListPresets",
    ],
    "elbv2": [
        # need a parameter
        "DescribeListeners",
    ],
    "opsworks": [
        # need a parameter
        "DescribeAgentVersions",
        "DescribeApps",
        "DescribeCommands",
        "DescribeDeployments",
        "DescribeEcsClusters",
        "DescribeElasticIps",
        "DescribeElasticLoadBalancers",
        "DescribeInstances",
        "DescribeLayers",
        "DescribePermissions",
        "DescribeRaidArrays",
        "DescribeVolumes",
    ],
    "rds": [
        # return way too much (unrelated) data
        "DescribeDBEngineVersions",
        "DescribeReservedDBInstancesOfferings",
    ],
    "workdocs": [
        # need a parameter
        "DescribeUsers",
    ],
    "importexport": [
        # slow
        "ListJobs",
    ],
    "worklink": [
        # deprecated?
        "ListFleets",
    ],
    "cloudwatch": [
        # not interesting
        "ListMetrics",
        "ListMetricStreams",
    ],
    "cloudformation": [
        # not interesting
        "ListTypeRegistrations",
        "DescribeAccountLimits",
    ],
    "dms": [
        # not interesting
        "DescribeOrderableReplicationInstances",
        # not per customer
        "DescribeEndpointTypes",
    ],
    "docdb": [
        # not interesting
        "DescribeDBEngineVersions",
    ],
    "service-quotas": [
        # not interesting
        "ListServices",
    ],
    "neptune": [
        # not interesting
        "DescribeDBEngineVersions",
    ],
    "emr": [
        # probably all the same
        "ListReleaseLabels",
    ],
    "route53": [
        # looks static
        "ListGeoLocations",
    ],
    "es": [
        # static
        "DescribeReservedElasticsearchInstanceOfferings",
    ],
    "savingsplans": [
        # probably not interesting
        "DescribeSavingsPlans",
        "DescribeSavingsPlansOfferings",
        "DescribeSavingsPlansOfferingRates",
    ],
    "route53domains": [
        # not interesting
        "ListPrices",
    ],
    "mediaconnect": [
        # not interesting
        "ListOfferings",
    ],
    "pricing": [
        # not interesting
        "DescribeServices",
    ],
    "ssm": [
        "DescribeAvailablePatches",
        # Need to filter by owner
        "ListDocuments",
    ]
}
