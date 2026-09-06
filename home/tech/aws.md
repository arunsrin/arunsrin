---
title: "AWS"
tags:
  - aws
  - cloud
---

# :material-cloud:{ .anim-fade } AWS

Most of this is from *Amazon Web Services in Action, IInd edition*.

## CloudFormation

Use CloudFormation to create a wordpress infra using these services:

- ELB - ALB specifically
- EC2 - Let's try 2 instances
- RDS - For MySql
- EFS - Using NFSv4.1 for User uploads
- Security Groups - Firewall

Full yaml written by the authors is [here](https://s3.amazonaws.com/awsinaction-code2/chapter02/template.yaml).

Well that was fast. The template file externalizes the keypair so you can put
your own from the drop down.

```yaml
Parameters:
  KeyName:
    Description: 'Key Pair name'
    Type: 'AWS::EC2::KeyPair::KeyName'
    Default: mykey
```

It adds an SG under `WebServerSecurityGroup` for ports 22 and 80.

There's a `LaunchConfiguration` section that's a bit like cloud-init (?), they
specify the conf files here for apache/php, download the wordpress tgz and
untar, etc.

Also a mount command is run there to mount the EFS that is also created and
made available to this deployment.

The `Database` section creates the RDS micro instance.

Looks like you can refer to other blocks in the file like this: `GatewayId:
!Ref InternetGateway`. And can even run some sort of queries on top:
`AvailabilityZone: !Select [1, !GetAZs '']`.

As `ASG` is also created and it sets current count to 4.

## EC2

### Instance Families

To decode the naming convention e.g. `t2.micro`:

- T - Cheap. Burst to higher perf for short periods.
- M - General Purpose
- C - Compute optimized
- R - Memory optimized
- D - Storage optimized, huge HDD
- I - Storage optimized, huge SSD
- X - Huge capacity, focus on memory, up to 1952 GB Mem and 128 virtual cores
- F - Accelerated computing based on FPGAs
- P,G and CG - Accelerated computing based on GPUs

The second part of the name, the `2` in `t2`, refers to the
generation. So this is the 2nd generation of the T family, of
size `micro`.

!!!note
    Stopped VMs incur no charges (unless you have attached resources like storage)
  
### EIPs

EIPs (elastic IPs) give you a fixed IP that you can associate to an EC2
instance. Otherwise the IP is going to change across reboots.

Seems very straightforward actually, create an EIP and you can associate to an
instance or a specific interface.

You can also create a new Network Interface, attach it to the instance, and
attach another EIP to that interface.

### Spot / Reserved instances

Spot: You bid for unused capacity in a DC. Price based on supply and demand.

Reserved: Use if you need VMs for a year or longer. Pay for a given time frame,
and get a discount. You pay even if you don't use it.

- No upfront, 1 year term
- Partial upfront, 1 or 3 year term
- All upfront, 1 or 3 year term

Potential savings may go up to 60%. You can also make scheduled reservations,
e.g. every week day from 9 AM to 5PM.

For spot instances, you set a bidding price. If the current spot price is lower
than your bid, an instance is spun up and your job runs. If the spot price then
exceeds your price, your VM is *terminated*. Good for batch processing jobs.

## Programming: CLI, SDK, CloudFormation

### Setup IAM first

IAM -> Add User -> 

- Name: *my-cli*
- Access type: `Programmatic`
- Permissions: Attach Existing Policies Directly
  - `AdministratorAccess` gives us everything

Then copy the access ID and key over somewhere safe.

Run `aws configure` to set things up.

```bash
 aws configure
 AWS Access Key ID [None]: <redacted>
 AWS Secret Access Key [None]: <redacted>
 Default region name [None]: us-east-1
 Default output format [None]: json
 ~
```

### Some CLI commands to try

This is pretty much like the `openstack` CLI.

- `aws ec2 describe-regions`
- `aws ec2 describe-instances --filters "Name=instance-type,Values=t2.micro"` - Using some filters

There is a `--query` arg that uses *JMESPath*, e.g.

- `aws ec2 describe-images --query "Images[0].ImageId"`

### SDK

Similarly, you can use the SDK for better control. e.g. `ec2.describeImages({ ... })`

### Blueprints / CloudFormation

Covered above already in brief. Contains:

- Format version
- Description
- Parameters - These are things you can set in the UI via drop-down etc, like ssh keys, AZ names, SG, etc
  - You can also set default values, remove echo (for sensitive text), specify allowed values and so on.
- Resources - instances, network, LB, EIP etc
- Outputs - return something from the template, like the generated hostname
  - Use `!GetAtt` for this. e.g. `!GetAtt 'Server.PublicDnsName'`

### Updates

Normally if you want to increase CPU/Mem, you'd have to power down, edit
settings, power back up. CF makes it all declarative. In this case, change the
`InstanceType` and redeploy, and it will figure out what to do.

### Template vs Stack

If you run a template to create a certain infrastructure, it's called a stack.
Think of template as a class and stack as the object instantiated by it.

## Automation: CF, Beanstalk, OpsWorks

- Elastic Beanstalk: fixed runtimes and conventions 
    - Config Management Tools: PHP, NodeJS, .Net
    - Deployment Runtime: Java, Python, Ruby, Go, Docker
- OpsWorks: just chef, ugh
    - Config Management Tools: PHP, NodeJS
    - Deployment Runtime: Java, Ruby, or any custom one
- CF: write shell scripts that run post-install
    - Config Management Tools: any
    - Deployment Runtime: any

### CF User Data

Find it at `http://169.254.169.254/latest/user-data`. Upto 16kb can be injected
into the VM at boot time.

It needs to be in base64 format though, so you inject it like
this:

```
UserData:
  'Fn::Base64': !Sub |
    #!/bin/bash -x
    export MY_PASSWORD="${MY_PASSWORD}"
    /usr/bin/start.sh
```

### CF Variables

Just use `!Sub`, for instance:

```
!Sub 'Your VPD id is ${VPC}' # same as !Ref VPC
!Sub '${VPC.CidrBlock}' # same as !GetAtt 'VPC.CidrBlock'
```

### Elastic Beanstalk

OS and runtime managed by AWS. Logical blocks are:

- An *application* which contains versions, environments and configurations.
- A *version* which identifies a specific release.
- A *configuration template* for app and platform configs.
- An *environment* where a specific version and config will be deployed.

### Create the application

`aws elasticbeanstalk create-application --application-name etherpad`

### Create a version

Must exist in S3.

```
aws elasticbeanstalk create-application-version --application-name etherpad \
 --version-label 1 \
 --source-bundle "S3Bucket=awsinaction-code2,S3Key=chapter05/etherpad.zip"
```
 
### Create an environment

See what PaaS offerings exist:

```
aws elasticbeanstalk list-available-solution-stacks
# for the nodeJS one we need in this example:
aws elasticbeanstalk list-available-solution-stacks --output text \
 --query "SolutionStacks[?contains(@, 'running Node.js')] | [0]"
```

There's a bunch of stuff for IIS, Java, PHP, Python, Ruby, Tomcat, Go...

Then create it:

```
$ aws elasticbeanstalk create-environment --environment-name etherpad \
 --application-name etherpad \
 --option-settings Namespace=aws:elasticbeanstalk:environment,\
 OptionName=EnvironmentType,Value=SingleInstance \                 1
 --solution-stack-name "$SolutionStackName" \
 --version-label 1
```

### Cleanup

Destroy the environment with `terminate-environment`, and the
application with `delete-application`.

### OpsWorks

um let's move on, it's Chef.

## Securing AWS: IAM, SG, VPC

Usual stuff here, pretty familiar with app and OS security
which is not covered anyway. SG for limiting network access,
VPC for private networks, IAM for RBAC.

### Systems Manager

Lets you manage all your instances from a single pane, run
remote commands on all of them, and so on.

Also let's you directly access your resources rather than via ssh.

### IAM

- *user*
- *group*
- *role*
- *policy*

Use IAM users for API access. Allows fine-grained association
to groups and resources.


#### Policies

An example:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "1",
    "Effect": "Allow",
    "Action": "ec2:*",
    "Resource": "*"
  }, {
    "Sid": "2",
    "Effect": "Deny",                      1
    "Action": "ec2:TerminateInstances",    2
    "Resource": "*"
  }]
}
```

In this case, a user attached to this policy could do
everything in ec2 except terminate the instances.

If something is both Denied and Allowed, Deny takes
precedence.

#### ARN

An AWS Resource Name (ARN) is a unique identifier with this structure:

`arn:aws:ec2:us-east-1:123456789:instance/i-zxcv123v`

Service / Region / Account ID / Resource type / Resource

Account ID is 12 digits.

Run `aws iam get-user` to see what you're logged in as, what
your account id is, etc.

#### Kinds of policies

- Managed policy - Can be reused in your account. AWS
maintans some (admin, read-only etc), customers can maintain
their own.
- Inline policy - Belongs to a specific role/user/group.

#### Creating my IAM admin user

```
aws iam create-group --group-name "admin"

#verify with
aws iam list-groups

aws iam attach-group-policy --group-name "admin" \
 --policy-arn "arn:aws:iam::aws:policy/AdministratorAccess"

# verify with
aws iam list-attached-group-policies --group-name admin

aws iam create-user --user-name "arunsrin"

# verify with
aws iam list-users

# add to group
aws iam add-user-to-group --group-name "admin" --user-name "arunsrin"

# set password
export AWS_PASSWORD='<your-password>'
aws iam create-login-profile --user-name "arunsrin" --password "$AWS_PASSWORD"

```

Then login to `https://$ACCOUNT_ID/signin.aws.amazon.com/console` and set up the
following in the account security settings:

- Access keys
- MFA
- Upload SSH keys to AWS CodeCommit

#### Authenticating AWS resources with roles

An EC2 instance might need to talk to S3 and so on. Instead of using IAM users
and uploading those secrets to each instance, use IAM Roles instead. The
credentials are automatically injected into the instance.

In CF you can just declare an inline policy giving access to an instance to a
specific API.

### SG

Create and use [VPC Flow
Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html) to debug
problems in this layer.

The source/dest of an SG can either be an IP address or another SG. A good use
case for the latter is a bastion host. You can define a SG to only allow SSH to
the rest of the environment if the source is the bastion instance, irrespective
of its IP.

Example that allows ssh to the bastion host only from a public IP, and ssh to
all other instances only *from* the bastion host's SG:

```
SecurityGroupBastionHost:
  Type: 'AWS::EC2::SecurityGroup'
  Properties:
    GroupDescription: 'Allowing incoming SSH and ICPM from anywhere.'
    VpcId: !Ref VPC
    SecurityGroupIngress:
    - IpProtocol: icmp
      FromPort: "-1"
      ToPort: "-1"
      CidrIp: '0.0.0.0/0'
    - IpProtocol: tcp
      FromPort: '22'
      ToPort: '22'
      CidrIp: !Sub '${IpForSSH}/32'
SecurityGroupInstance:
  Type: 'AWS::EC2::SecurityGroup'
  Properties:
    GroupDescription: 'Allowing incoming SSH from the Bastion Host.'
    VpcId: !Ref VPC
    SecurityGroupIngress:
    - IpProtocol: tcp
      FromPort: '22'
      ToPort: '22'
      SourceSecurityGroupId: !Ref SecurityGroupBastionHost
```

### VPC

Private address ranges:
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

Use a subnet to separate concerns. Private for DB, backend, Public for
frontend, etc. Goes well with the SG concept above to restrict traffic between
subnets.

One can attach an *Internet Gateway* to a VPC to NAT public traffic to the
private IPs.

You can also create *Network ACLs* and attach to a VPC. Unlike SGs though,
these are stateless. i.e. for TCP and any bidirectional traffic to work, you'd
need to explicitly mention ingress and egress for, say, port 22. Also consider
that incoming connections will use an ephemeral port.. Also the ordering
matters here and first matching rule is applied and rest are skipped.

Overall, stick to SGs and use NACLs only for finetuning.

#### Implementation

To create an overall VPC with a public subnet that can be reached from the
outside world:

- `AWS::EC2::VPC` creates the VPC with a certain overall CIDR range.
- `AWS::EC2::InternetGateway` connects you to the outside world.
- `AWS::EC2::VPCGatewayAttachment` connects the above 2.

- `AWS::EC2::Subnet` carve out a smaller new subnet from the VPC above.
- `AWS::EC2::RouteTable` routeTable linked to VPC above.
- `AWS::EC2::SubnetRouteTableAssociation` links the 2 above
- `AWS::EC2::Route` specifies a routing rule from the InternetGateway to the RouteTable
- `AWS::EC2::NetworkAcl` firewall rules
- `AWS::EC2::SubnetNetworkAclAssociation` Connect Network Acl to Subnet

For a private subnet that you want to restrict, you'd skiip the InternetGateway
bits. As long as its in the same VPC, entities in other subnets can reach each
other.

Don't forget to attach the SecurityGroup and SubnetId to the EC2 instance,
under NetworkInterfaces.

For devices in an internal subnet to connect to the outside world, use a NAT
gateway in a public subnet and create a route to it from the inside:

- `AWS::EC2::Subnet` dedicated subnet for public nat
- `AWS::EC2::RouteTable` in the overall VPC
- `AWS::EC2::Route` allowing 0.0.0.0 egress from RouteTable to InternetGateway
- `AWS::EC2::EIP` elastic IP for the Nat Gateway
- `AWS::EC2::NatGateway` with above elastic IP and the Subnet created initially
- `AWS::EC2::Route` routes 0.0.0.0 egress from internal RouteTable to NatGateway

Since traffic via a NAT Gateway is billed, 2 alternatives are:
- Use a public subnet if possible, instead of a private one
- Use `VPC endpoints` for accessing AWS services like S3

## Lambda

- No updates, no remote access
- Billed by invocation
- Integrated with other AWS infra well
- Java, Node, C#, Python, Go
- Publish metrics to CloudWatch by default

### Creating a lambda

Lots of blueprints available.

Seems pretty straightforward to create. We selected a
blueprint called `lambda-canary`, a simple python script that
hits a site and checks for a string.

Scheduling uses cron syntax but also a `rate` syntax, e.g.
`rate(1 hour)`. EventBridge does this.

On submission, you get a nice editor to tweak your code, a
tab to Test it, Monitor it, and so on.

### Alerting

Now to get an email alert when something changes, you need to
use CloudWatch. Each metric published by lambda has:
- Invocations: how many times it was called successfully or unsuccessfully
- Errors: exceptions, timeouts and other failures in the code
- Duration
- Throttles: If we hit a limit and AWS throttles the number of invocations of this lambda, it shows up here.

Errors & Throttles are good metrics to create alerts.

- Go to CloudWatch in the console
- Alarms -> Create Alarm
- Select metrics -> Lambda -> by Function Name -> arunsrin-site-healthcheck | Errors
- Proceed. Select `Sum` as the statistic
- `Static` Condition, whenever Error is `>=` a fixed value, say, `2`

!!!note
    lambda functions run outside your VPC by default and have
    full internet access. To access the parts within your
    private network in your VPC, you'd have to define the
    VPC, subnets and SG for your lambda function

### CloudWatch / CloudTrail

So far we have seen its metrics, logs and alarms. But it does
events too. Any state change in an EC2 instance results in a
new emit. We can detect those events in a lambda function and
take certain actions.

*CloudTrail* is the component that raises events.

You write a rule to filter certain events, like *RunInstances*.

Then for python you would implement a function like this:


```py
def lambda_handler(event, context):
  # insert your code
  return
```

- 300 second limit for each invocation
- Cold start takes time: download dependencies, start runtime..

### Serverless Application Model

An extension of CF that let's you define lambdas. Your
scripts in the folder are bundled and uploaded.

### Stitching it together

To make a backend app in this stack you would use something
like these:

- API Gateway - Secure and scalable REST APIs
- Lambda - triggered by above
- Object store and NoSQL DB - used by above

## Data Storage

- S3 - access via AWS API, third party tools
- Glacier - very slow
- EBS (SSD) - attached to instance via network
- EC2 Instance Store (SSD) - attached to instance directly
- EFS - NFSv4.1 - attached via network
- RDS - MySQL, SSD
- Elasticache - Redis / memcached protocol
- DynamoDB - access via AWS API (SDKs, CLI)

## S3

Make a bucket:

```sh
$ aws s3 mb s3://arunsrin
make_bucket: arunsrin
$
```

Upload:

```sh
aws s3 sync ~/code/dotfiles/ s3://arunsrin/dotfiles
```

List contents:

```sh
aws s3 ls 
aws s3 ls arunsrin/
aws s3 ls arunsrin/dotfiles/
```

Download:

```sh
aws s3 cp --recursrive s3://arunsrin s3backup
```

Remove:

```sh
aws s3 rm --recursive s3://arunsrin/dotfiles
```

### Versioning

Disabled by default. Replacing a key with different content will wipe out the
old data. Turn on versioning:

```sh
aws s3api put-bucket-versioning --bucket arunsrin \
 --versioning-configuration Status=Enabled
```

### Access

Create a bucket policy and upload it. Essentially we want to Allow Access, to
Anyone, to be able to GetObjects from s3, from our Bucket:

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddPerm",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::$BucketName/*"]
    }
  ]
}
```

Then upload it:

```sh
aws s3api put-bucket-policy --bucket arunsrin-uploads --policy file://s3-policy.json
```

### Static website hosting

Do the above to make it publicly accessible, then upload your html files, and
do this:

```sh
aws s3 website s3://$BucketName --index-document helloworld.html
```

You can access it on a url like this:

`http://$BucketName.s3-website-$Region.amazonaws.com`

E.g. mine is http://arunsrin-uploads.s3-website-us-east-1.amazonaws.com/

!!!warning
	At this point I tried to have a CNAME from my domain to the above, and
	realized it didn't work.

Apparently the CNAME and bucket name have to match. So I had to make a new
bucket with the correct name and copy the content over, and re-enable public
access and static website.

```sh
aws s3 mb s3://uploads.arunsr.in
aws s3 sync s3://arunsrin-uploads s3://uploads.arunsr.in
aws s3 rb --force s3://arunsrin-uploads
aws s3 website s3://uploads.arunsr.in --index-document index.html
aws s3api put-bucket-policy --bucket uploads.arunsr.in --policy file://s3-policy.json
```

Now [http://uploads.arunsr.in/](http://uploads.arunsr.in/) works :)

But SSL doesn't, TODO see CloudFront for that bit.

### Things to note

s3 is eventually consistent. i.e. concurrent creates and deletes will always be
atomic, but occassionally you might get stale data.

For better i/o performance, don't name all your keys starting with same
characters, like image0, image1, image2..

Using `foo/bar` gives a folder-like experience while browsing the contents of
`foo/` but technically the key is still `foo/bar`.

## Glacier

- Very slow, takes minutes to hours to retrieve data.
- Storage is cheap, putting and getting out data is pricey.

One can add a *lifecycle rule* in S3 to archive or delete data after a set
number of days, or move them to glacier.

## References

- [Cloudformation templates](https://github.com/widdix/aws-cf-templates)
- [AWS quick starts](https://aws.amazon.com/quickstart/?solutions-all.sort-by=item.additionalFields.sortDate&solutions-all.sort-order=desc&awsf.filter-tech-category=*all&awsf.filter-industry=*all&awsf.filter-content-type=*all)
- [List of IAM policies](https://iam.cloudonaut.io/)
- AWS Lambda in Action, by Danilo Poccia




