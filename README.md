# reflex-aws-enforce-no-public-ebs-snapshot
A Reflex rule for enforcing no EBS snapshots are publicly accessible.

## Usage
To use this rule either add it to your `reflex.yaml` configuration file:  
```
version: 0.1

providers:
  - aws

measures:
  - reflex-aws-enforce-no-public-ebs-snapshot
```

or add it directly to your Terraform:  
```
...

module "reflex-aws-enforce-no-public-ebs-snapshot" {
  source           = "github.com/cloudmitigator/reflex-aws-enforce-no-public-ebs-snapshot"
  email            = "example@example.com"
}

...
```

## License
This Reflex rule is made available under the MPL 2.0 license. For more information view the [LICENSE](https://github.com/cloudmitigator/reflex-aws-enforce-no-public-ebs-snapshot/blob/master/LICENSE) 
