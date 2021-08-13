import boto3 
from string import Template


htmlTemplate = Template("""
<html>
  <body>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({ startOnLoad: true });
    </script>
    <style>
      .flex {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
      }
      .mermaid svg {
        text-align: center;
      }
      .mermaid svg rect {
        stroke-width: 0px !important;
        stroke-width: 0px;
        filter: drop-shadow(0px 3px 3px rgba(153, 153, 153, 0.8));
      }
    </style>
    $graph
    </div>
  </body>
</html>
""")

#graph 
graph = []

#clients
sso = boto3.client('sso-admin')
org = boto3.client('organizations')

# collect org information - OUs and SCPs
orgByAccount = {}
scpsInOu = {}

def recurseOrg(parent=None,chain=['root']):
    if not parent:
        for root in org.list_roots()["Roots"]:
            recurseOrg(parent=root["Id"],chain=[*chain])
    else:
        accounts = [org.describe_account(AccountId=a["Id"])["Account"]["Name"] for a in org.list_children(ParentId=parent,ChildType='ACCOUNT')["Children"]]
        for account in accounts:
            orgByAccount[account] = [*chain]
        ouChildren = org.list_children(ParentId=parent,ChildType='ORGANIZATIONAL_UNIT')["Children"]
        for ouChild in ouChildren:
            name = org.describe_organizational_unit(OrganizationalUnitId=ouChild["Id"])["OrganizationalUnit"]["Name"]
            if name not in scpsInOu:
                scpsInOu[name] = [p["Name"] for p in org.list_policies_for_target(TargetId=ouChild["Id"],Filter='SERVICE_CONTROL_POLICY')["Policies"]]
            recurseOrg(parent=ouChild["Id"],chain=[*chain,name])
recurseOrg()

#get sso instance
ssoInstance = sso.list_instances()["Instances"][0]["InstanceArn"]

#get accounts in organization, Id and Name properties are used for each account
accounts = [a for p in org.get_paginator("list_accounts").paginate() for a in p["Accounts"]]

for account in accounts:
    accountId = account["Id"]
    accountName = account["Name"]
    graph.append(f"<div id={accountId} class=\"mermaid flex\"> ")
    graph.append("flowchart RL")
    graph.append("classDef default fill:#fff;")
    graph.append(f"subgraph {accountId} [{accountName}]")
    graph.append("direction TB")
    accountScp = []
    if accountName in orgByAccount:
        ousId = accountId + "ous"
        graph.append(f"subgraph {ousId} [OUs]")
        graph.append("direction RL")
        for ou in orgByAccount[accountName]:
            # add scps from ou
            if ou in scpsInOu:
                accountScp = [*accountScp,*scpsInOu[ou]]
            accountOuId = "".join(ou.split(" "))
            graph.append(f"{ousId + accountOuId}[{ou}]")
        graph.append("end")
    if len(accountScp) > 0:
        scpsId = accountId + "scps"
        graph.append(f"subgraph {scpsId} [SCPs]")
        graph.append("direction RL")
        for scp in accountScp:
            scpId = "".join(scp.split(" "))
            graph.append(f"{scpsId + scpId}[{scp}]")
        graph.append("end")
    #get all permission sets assigned to account
    permSets = [ps for p in sso.get_paginator("list_permission_sets_provisioned_to_account").paginate(InstanceArn=ssoInstance,AccountId=account["Id"]) for ps in p['PermissionSets']]
    permId = accountId + "permissionsets"
    graph.append(f"subgraph {permId} [Permission Sets]")
    graph.append("direction RL")
    for ps in permSets:
        #for each permission set describe its name
        psName = sso.describe_permission_set(InstanceArn=ssoInstance,PermissionSetArn=ps)["PermissionSet"]["Name"]
        graph.append(f"{permId + psName}[{psName}]")
    graph.append("end")
    graph.append("end")
    graph.append("</div>")


graph = '\r\n'.join(graph)
htmlData = htmlTemplate.substitute(graph=graph)

output = open("aws-org-mapper.html", "w")
output.write(htmlData)
output.close()