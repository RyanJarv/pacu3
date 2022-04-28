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
        "DescribeRegions",
        "DescribeReservedInstancesOfferings",
        "DescribeSnapshots",
        "DescribeSpotPriceHistory",
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
}
